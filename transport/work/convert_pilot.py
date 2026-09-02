#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pilot conversion: convert a small set of HTML pages into .tid files."""
import _paths as P
import csv
import os
import re
import shutil
import sys
import urllib.parse

sys.stdout.reconfigure(encoding="utf-8")

# Phase 2 钩子清理逻辑（按书判定 class/id/style/font 边界）复用 strip_hooks
import strip_hooks as SH

ROOT = P.ROOT
WIKI_TIDDLERS = P.WIKI_TIDDLERS
FINAL_MAPPING = P.FINAL_MAPPING

# 试点页面
PILOT_FILES = [
    r"前言.htm",
    r"0 核心三宝书\PHB玩家手册\2种族\人类.htm",
    r"0 核心三宝书\PHB玩家手册\4技能\技能表.htm",
    r"0 核心三宝书\DMG城主指南\封面.htm",
]


def load_mapping():
    mapping = {}
    with open(FINAL_MAPPING, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            mapping[row["源文件相对路径"]] = row
    return mapping


def read_text(path):
    raw = open(path, "rb").read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gb18030", errors="replace")


def extract_body(text):
    # 某些源文件会出现嵌套 <body>（WinCHM 外层 + 内层页面），
    # 这里取"最后一个 <body>"到其后的第一个 </body>，即最内层正文。
    opens = [m for m in re.finditer(r"<body[^>]*>", text, re.I)]
    if opens:
        start_m = opens[-1]
        start = start_m.end()
        close_m = re.search(r"</body>", text[start:], re.I)
        if close_m:
            return text[start:start + close_m.start()]
        return text[start:]
    # 没有 body 时，去掉 html/head 后的部分
    m = re.search(r"</head>\s*(.*)", text, re.S | re.I)
    if m:
        return m.group(1)
    return text


def normalize_headings(body):
    """保留 align=center 为 text-align:center，字号交给 DND3R 全局样式表控制。"""
    def repl(m):
        level = m.group(1)
        attrs = m.group(2)
        tag = f"h{level}"

        decls = []
        sm = re.search(r"style\s*=\s*[\"']([^\"']*)[\"']", attrs, re.I)
        if sm:
            for part in sm.group(1).split(";"):
                part = part.strip()
                if part:
                    decls.append(part)

        if re.search(r"align\s*=\s*[\"']?center[\"']?", attrs, re.I) and not any(d.lower().startswith("text-align") for d in decls):
            decls.append("text-align:center")

        # 移除旧的 align/style 属性，统一用 style 表达
        attrs = re.sub(r"\s+align\s*=\s*[\"'][^\"']*[\"']", "", attrs, flags=re.I)
        attrs = re.sub(r"\s+align\s*=\s*[^\s>]+", "", attrs, flags=re.I)
        attrs = re.sub(r"\s+style\s*=\s*[\"'][^\"']*[\"']", "", attrs, flags=re.I)

        if decls:
            attrs += f' style="{"; ".join(decls)}"'
        return f"<{tag}{attrs}>"

    return re.sub(r"<h([1-6])([^>]*)>", repl, body, flags=re.I)


def lowercase_html_tags(body):
    """将 HTML 标签名统一转为小写，例如 <H1> -> <h1>、<IMG> -> <img>。"""
    return re.sub(
        r"<(/?)([A-Za-z][A-Za-z0-9]*)",
        lambda m: "<" + m.group(1) + m.group(2).lower(),
        body,
    )


def fix_heading_closing_tags(body):
    """修正标题标签闭合不匹配，例如 <h5>...</h6> 自动改为 </h5>。"""
    stack = []
    pattern = re.compile(r"<(/?)h([1-6])[^>]*>", re.I)

    def repl(m):
        closing = m.group(1) == "/"
        level = int(m.group(2))
        if not closing:
            stack.append(level)
            return m.group(0)
        if stack:
            expected = stack.pop()
            if expected != level:
                return f"</h{expected}>"
        return m.group(0)

    return pattern.sub(repl, body)


def normalize_lists(body):
    """补全 <li> 的闭合标签，避免 TiddlyWiki 渲染时出现多余的 </ul> 或列表错位。"""
    out = []
    pos = 0
    stack = []  # 每个元素代表一层 <ul>：{"open_li": bool}
    pattern = re.compile(r"<(/?)(ul|li)\b[^>]*>", re.I)

    for m in pattern.finditer(body):
        out.append(body[pos:m.start()])
        closing = m.group(1) == "/"
        tag = m.group(2).lower()
        if tag == "ul":
            if closing:
                if stack:
                    if stack[-1]["open_li"]:
                        out.append("</li>")
                        stack[-1]["open_li"] = False
                    stack.pop()
            else:
                stack.append({"open_li": False})
        elif tag == "li":
            if closing:
                if stack:
                    stack[-1]["open_li"] = False
            else:
                if stack and stack[-1]["open_li"]:
                    out.append("</li>")
                if stack:
                    stack[-1]["open_li"] = True
        out.append(m.group(0))
        pos = m.end()

    out.append(body[pos:])
    return "".join(out)


def _find_matching_div_close(body, start):
    """从 start 位置开始扫描，返回与 start 处已打开的 <div> 匹配的 </div> 位置。"""
    depth = 1
    for m in re.finditer(r"<(/?)div\b[^>]*>", body[start:], re.I):
        if m.group(1) == "/":
            depth -= 1
            if depth == 0:
                return start + m.start(), start + m.end()
        else:
            depth += 1
    return None


def _try_convert_fold(body, input_pos):
    """尝试把 input_pos 处的一个"按钮 + 隐藏 div"折叠块转换为 details/summary。"""
    # 1. 向前找包含 margin-bottom:2px 的 header div
    prefix = body[:input_pos]
    opens = list(re.finditer(r"<div\b[^>]*>", prefix, re.I))
    header_open = None
    for m in reversed(opens):
        if "margin-bottom:2px" in m.group(0).lower():
            header_open = m
            break
    if header_open is None:
        return None

    header_start = header_open.start()
    header_inner_start = header_open.end()
    header_close = _find_matching_div_close(body, header_inner_start)
    if header_close is None:
        return None
    header_close_start, header_close_end = header_close
    header_inner = body[header_inner_start:header_close_start]

    # 2. 提取标题
    hm = re.search(r"<h([1-6])[^>]*>(.*?)</h\1>", header_inner, re.S | re.I)
    if hm is None:
        return None
    heading_text = re.sub(r"<[^>]+>", "", hm.group(2)).strip()

    # 3. 提取标题下方的 summary 段落（可选）
    pm = re.search(r"<p[^>]*>.*?</p>", header_inner, re.S | re.I)
    summary_p = pm.group(0) if pm else ""

    # 4. header 后找内容容器 div
    after_header = body[header_close_end:]
    cm = re.search(r"<div\b[^>]*>", after_header, re.I)
    if cm is None:
        return None
    content_open_start = header_close_end + cm.start()
    content_open_end = header_close_end + cm.end()
    content_close = _find_matching_div_close(body, content_open_end)
    if content_close is None:
        return None
    content_close_start, content_close_end = content_close
    content_inner = body[content_open_end:content_close_start]

    # 5. 在内容容器中找 display:none 的隐藏 div
    hm2 = re.search(
        r"<div\b[^>]*style=[\"']display:\s*none;[\"'][^>]*>",
        content_inner,
        re.I,
    )
    if hm2 is None:
        return None
    hidden_open_start = content_open_end + hm2.start()
    hidden_open_end = content_open_end + hm2.end()
    hidden_close = _find_matching_div_close(body, hidden_open_end)
    if hidden_close is None:
        return None
    hidden_close_start, hidden_close_end = hidden_close
    hidden_inner = body[hidden_open_end:hidden_close_start]

    # 6. 生成 details/summary
    summary_style = (
        "display:inline-block;padding:0.2em 0.8em;"
        "border:1px solid #888;border-radius:4px;"
        "background:#f0f0f0;cursor:pointer;font-size:0.95em;"
        "user-select:none;text-indent:0;"
    )
    summary_p = re.sub(r"^<p>", '<p class="noindent">', summary_p.strip())
    new_block = (
        f"<details>\n"
        f"<summary style=\"{summary_style}\">{heading_text}</summary>\n"
        f"{summary_p}\n{hidden_inner.strip()}\n</details>"
    )
    return body[:header_start] + new_block + body[content_close_end:]


def convert_showhide_blocks(body):
    """把原始 CHM 中常见的"按钮 + 隐藏 div"折叠块转换为 <details>/<summary>。

    支持多层嵌套，处理时从后往前逐个转换。
    """
    input_positions = [
        m.start()
        for m in re.finditer(r"<input\b[^>]*type=[\"']button[\"']", body, re.I)
    ]
    # 从后往前处理，先转换内层
    for pos in reversed(input_positions):
        new_body = _try_convert_fold(body, pos)
        if new_body is not None:
            body = new_body
    return body


def normalize_fullwidth_punct(body):
    """用户规则（2026-09-02 扩展）：搬运后 tid 正文内不得出现全角 ASCII。

    全角英文字母 A-Za-z、数字 0-9、括号 （）、弯引号 “”‘’ 一律转为半角。
    （早期只覆盖 “” （），本次扩展字母/数字/弯引号‘’。）
    """
    trans = {
        # 弯引号 -> 直引号
        "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
        # 全角括号
        "\uff08": "(", "\uff09": ")",
    }
    # 全角字母 A-Z / a-z
    for i in range(26):
        trans[chr(0xFF21 + i)] = chr(0x41 + i)  # Ａ-Ｚ -> A-Z
        trans[chr(0xFF41 + i)] = chr(0x61 + i)  # ａ-ｚ -> a-z
    # 全角数字 ０-９
    for i in range(10):
        trans[chr(0xFF10 + i)] = chr(0x30 + i)
    return body.translate(str.maketrans(trans))


def normalize_bullet_paragraphs(body):
    """用户规则：以 · 开头的 <p> 段落转换为 <ul><li>（2026-08-30）。

    连续的多个合并进同一个 <ul>；仅处理内容以 ·（或 •）开头的 p。
    """
    p_re = re.compile(r"<p[^>]*>\s*[·•]\s*(?:(?!</p>).)*?</p>", re.S)
    matches = list(p_re.finditer(body))
    if not matches:
        return body
    groups = []
    for m in matches:
        if groups and not body[groups[-1][-1].end():m.start()].strip():
            groups[-1].append(m)
        else:
            groups.append([m])
    for g in reversed(groups):
        items = []
        for m in g:
            inner = m.group(0)
            inner = re.sub(r"^<p[^>]*>\s*[·•]\s*", "<li>", inner)
            inner = re.sub(r"</p>$", "</li>", inner)
            items.append(inner.strip())
        ul = "<ul>\n" + "\n".join(items) + "\n</ul>"
        body = body[:g[0].start()] + ul + body[g[-1].end():]
    return body


# 表格行内格式 class：源表格页内联 <style> 定义的斑马纹/首列标签类
_TABLE_CLASS_TARGETS = {"g", "l", "w"}
_TABLE_CLASS_ATTR = re.compile(r"""[ \t]+class[ \t]*=[ \t]*(["'])(.*?)\1""", re.I)


def strip_table_classes(body):
    """移除表格行内格式 class="g" / "l" / "w"（用户规则，2026-08-31）。

    源表格页自带内联 <style>：
        .l{font-weight:600;background:#f0f0f0;text-align:center}  # 首列标签
        .g td{background:#f7f7f7}  .w td{background:#fff}        # 斑马纹
        .w{max-width:1100px;background:#fff;...}                  # 表格外层容器
    但 clean_html() 会剥离 <style>，全局 cascading_stylesheet.css 亦未定义这些类，
    故它们在 wiki 中是失效属性，删除后渲染结果不变。

    多值 class 只剔除目标值、保留其余（如 class="l bold" -> class="bold"）；
    若某元素仅剩这些类，则整个 class 属性连同前导空白一并删除。
    """
    def repl(m):
        quote, vals = m.group(1), m.group(2).split()
        kept = [v for v in vals if v.lower() not in _TABLE_CLASS_TARGETS]
        if not kept:
            return ""
        return f' class={quote}{" ".join(kept)}{quote}'

    return _TABLE_CLASS_ATTR.sub(repl, body)


def clean_html(body, book=None):
    # &#9; (Tab 实体) 统一替换为空格，避免源码噪音（2026-09-01）
    body = body.replace("&#9;", " ")
    # <p 标签内部多余空格/换行清理：<p \n> / <p class="x" \n> -> <p> / <p class="x">
    body = re.sub(r"<p\s*\n", "<p ", body)              # <p 与属性间换行，保留空格
    body = re.sub(r"<p([^>]+?)\s+>", r"<p\1>", body)    # 带属性且 > 前多余空白
    body = re.sub(r"<p\s+>", "<p>", body)               # 纯空白型 <p  >
    # 去掉 script 和 style 块；节点内不保留单节点 CSS，统一由全局 cascading_stylesheet.css 控制
    body = re.sub(r"<script[^>]*>.*?</script>", "", body, flags=re.S | re.I)
    body = re.sub(r"<style[^>]*>.*?</style>", "", body, flags=re.S | re.I)
    # 去掉 DND3R 在线反馈区块
    body = re.sub(r"<!--\s*DND3R-FEEDBACK-BEGIN\s*-->.*?<!--\s*DND3R-FEEDBACK-END\s*-->", "", body, flags=re.S | re.I)
    body = normalize_headings(body)
    body = lowercase_html_tags(body)
    body = fix_heading_closing_tags(body)
    body = normalize_lists(body)
    body = convert_showhide_blocks(body)
    # 用户规则：<strong> -> <b>（2026-08-30，与已转换内容一致）
    body = re.sub(r"<strong\b[^>]*>", "<b>", body)
    body = re.sub(r"</strong\s*>", "</b>", body)
    # 用户规则：以 · 开头的 <p> -> <ul><li>（2026-08-30）
    body = normalize_bullet_paragraphs(body)
    body = normalize_fullwidth_punct(body)
    # 用户规则：清理表格行内格式 class="g"/"l"/"w"（2026-08-31）
    body = strip_table_classes(body)
    # 用户规则：合并相邻同标签边界（2026-09-01，各自跳过对方交叉嵌套）
    #   </b><b> -> 连续加粗；</i><i> -> 连续斜体
    body = re.sub(r"(?<!</i>)</b><b>(?!<i>)", "", body)
    body = re.sub(r"(?<!</b>)</i><i>(?!<b>)", "", body)
    # Phase 2 固化：按书判定清理 class/id/style(<o:p>/<font>/伪标题 h3)，
    # 使后续 4500 页新书直接产出干净内容，不再产生新钩子
    body, _ = SH.process_body(body, book)
    return body.strip()


MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
}


def copy_image(src_rel, base_rel_dir):
    """Copy an image into wiki/tiddlers/ and return the TiddlyWiki image title.

    TiddlyWiki filesystem 插件会把没有 .meta 的二进制文件标题设为完整路径，
    因此这里同时生成 .meta 文件，把标题设为相对路径。
    """
    if base_rel_dir:
        full_rel = os.path.normpath(os.path.join(base_rel_dir, src_rel.replace("/", "\\")))
    else:
        full_rel = os.path.normpath(src_rel.replace("/", "\\"))
    # 防止路径逃逸到源目录之外
    full_rel = full_rel.replace("../", "")
    src_path = os.path.join(ROOT, full_rel)
    if not os.path.isfile(src_path):
        return None
    dest_rel = full_rel.replace("\\", "/")
    dest_path = os.path.join(WIKI_TIDDLERS, full_rel)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy2(src_path, dest_path)

    ext = os.path.splitext(full_rel)[1].lower()
    mime = MIME_TYPES.get(ext, "application/octet-stream")
    meta_path = dest_path + ".meta"
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"title: {dest_rel}\n")
        f.write(f"type: {mime}\n")
    return dest_rel


def rewrite_images(body, base_rel_dir):
    def repl(m):
        tag = m.group(0)
        src = m.group(1).strip()
        if src.startswith(("http://", "https://", "data:", "javascript:", "#")):
            return tag
        try:
            decoded = urllib.parse.unquote(src)
        except Exception:
            decoded = src
        title = copy_image(decoded, base_rel_dir)
        if title:
            lower_tag = tag.lower()
            # 保留常见的居中意图
            if ("align=center" in lower_tag
                    or re.search(r"width\s*=\s*[\"']?100%", lower_tag)
                    or "text-align:center" in lower_tag):
                return f'<div style="text-align:center;">[img[{title}]]</div>'
            return f"[img[{title}]]"
        return tag

    return re.sub(r"<img[^>]+src=[\"']([^\"']+)[\"'][^>]*>", repl, body, flags=re.I)


def rewrite_links(body, mapping, base_rel_dir):
    link_map = {}
    for row in mapping.values():
        link_map[row["源文件相对路径"].replace("\\", "/").lower()] = row["Tiddler标题"]
        link_map[row["源文件相对路径"].replace("/", "\\").lower()] = row["Tiddler标题"]

    def repl(m):
        href = m.group(1).strip()
        inner = m.group(2)
        if href.startswith(("http://", "https://", "mailto:", "javascript:", "data:")):
            return m.group(0)
        if href.startswith("#"):
            return m.group(0)
        # 去掉锚点
        path_part = href.split("#", 1)[0]
        anchor = href.split("#", 1)[1] if "#" in href else ""
        try:
            decoded = urllib.parse.unquote(path_part)
        except Exception:
            decoded = path_part
        if base_rel_dir:
            full_rel = os.path.normpath(os.path.join(base_rel_dir, decoded.replace("/", "\\")))
        else:
            full_rel = os.path.normpath(decoded.replace("/", "\\"))
        full_rel = full_rel.replace("../", "")
        normalized = full_rel.replace("\\", "/").lower()
        title = link_map.get(normalized)
        if not title:
            # 也尝试直接原样
            title = link_map.get(decoded.lower())
        if title:
            display = re.sub(r"<[^>]+>", "", inner).strip()
            if anchor:
                title = f"{title}#{anchor}"
            if display:
                return f"[[{display}|{title}]]"
            return f"[[{title}]]"
        return m.group(0)

    # 只处理简单 <a href="...">文本</a>
    return re.sub(r"<a\s+[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", repl, body, flags=re.S | re.I)


def main():
    mapping = load_mapping()
    os.makedirs(WIKI_TIDDLERS, exist_ok=True)

    for idx, rel in enumerate(PILOT_FILES, 1):
        src_path = os.path.join(ROOT, rel)
        if not os.path.isfile(src_path):
            print("MISSING:", rel)
            continue
        row = mapping.get(rel)
        text = read_text(src_path)
        body = extract_body(text)
        body = clean_html(body)
        base_rel_dir = os.path.dirname(rel) if "\\" in rel else ""
        body = rewrite_images(body, base_rel_dir)
        body = rewrite_links(body, mapping, base_rel_dir)

        title = row["Tiddler标题"] if row else os.path.splitext(os.path.basename(rel))[0]
        tags = row["标签"] if row else ""
        source = rel.replace("\\", "/")

        tid = f"""title: {title}
tags: {tags}
source: {source}
type: text/vnd.tiddlywiki

{body}
"""
        # 按源文件相对路径分目录存放 .tid，便于管理和后续增量搬运
        tid_rel = os.path.splitext(rel)[0] + ".tid"
        out_path = os.path.join(WIKI_TIDDLERS, tid_rel)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(tid)
        print(f"[OK] {idx}: {title} -> {out_path}")

    print("pilot done.")


if __name__ == "__main__":
    main()
