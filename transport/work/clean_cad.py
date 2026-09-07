# -*- coding: utf-8 -*-
"""CAd完美冒险 噪音页结构化重排（复用 clean_mic.py 的 normalize/表格紧凑化/自检思路）。

背景：CAd 源与 MIC/MM3/MM4/MM5 同源（Word/WinCHM 导出），47/49 页带 Word 噪音：
      <span style='FONT-SIZE: 11pt; FONT-FAMILY:"微软雅黑"; mso-bidi-*'>、<span lang=EN-US>、
      <div> 包裹、<o:p>、`<?xml:namespace>`、`&nbsp;`、跨行属性。

与 clean_mic.py 的区别：
  **不做「物品名 -> <h4>」提升**。MIC 主体是统一物品条目（<b>中文名(EN)</b> 独占一段），
  可安全提升为 h4；而 CAd 结构异质——37/49 含表格（进阶职业技能表等）、
  且 法术列表/专长 等页面中 `<b>名称(EN)</b>` 是**列表项**而非章节标题，
  提升成 h4 会造成错误层级。故仅保留原标题（h1-h6）与段落结构。

处理内容：
  1. normalize 去全部 Word 标签噪音（含 <div>、跨行 style、&nbsp;）
  2. 表格紧凑化（去 colgroup/tbody/width/style，td 仅留 rowspan/colspan）
  3. 按块（<p>/<h1-6>）提取，块间裸文本保留，避免内容丢失
  4. 全角 ASCII 转半角（遵守 tid 内禁全角字母/数字/括号规则）

安全设计：
  1. 内容丢失自检：基线同样过 normalize 后比对可见字符数
  2. --apply 前自动备份到 work/backup_cad_clean_<时间戳>
  3. 干净源（无噪音标记）直接跳过

用法：
  python clean_cad.py            # 干跑，输出统计与样本
  python clean_cad.py --apply    # 实际写入（先自动备份到 work/）
"""
import datetime
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P
import convert_pilot as cp

CAD = os.path.join(P.WIKI_TIDDLERS, "3 完美系列", "CAd完美冒险")
WORK = P.WORK

TABLE_RE = re.compile(r"<table[^>]*>.*?</table>", re.S | re.I)
SAFE_TAGS = {"b", "i", "u", "em", "strong", "br", "img", "sub", "sup"}


# ---------------------------------------------------------------- normalize
def normalize(body):
    """机械去噪：注释、o:p/u1:p、span/font/div、style/class/lang、xml:namespace、空属性。"""
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    # <o:p> <o:P> <u1:p> 等命名空间标签
    body = re.sub(r"</?(?:o|u1):[a-zA-Z][^>]*/?>", "", body)
    body = re.sub(r"</?span[^>]*>", "", body, flags=re.I)
    body = re.sub(r"</?font[^>]*>", "", body, flags=re.I)
    body = re.sub(r"</?div[^>]*>", "", body, flags=re.I)  # Word/WinCHM 的 div 包裹，无语义，直接丢弃
    # style / class / lang 属性（style 值可能跨行，字符集 [^'] 可跨行；加 re.S 保险）
    body = re.sub(r"\sstyle\s*=\s*('[^']*'|\"[^\"]*\"|[^\s>]+)", "", body, flags=re.I | re.S)
    body = re.sub(r"\sclass\s*=\s*('[^']*'|\"[^\"]*\"|[^\s>]+)", "", body, flags=re.I | re.S)
    body = re.sub(r"\slang\s*=\s*(EN-US|ZR|ZH-CN|[^\s>]+)", "", body, flags=re.I)
    # <?xml:namespace ... />（可能跨行自闭合）
    body = re.sub(r"<\?xml:namespace[^>]*\/?>", "", body, flags=re.I | re.S)
    # 空加粗/空斜体残留
    body = re.sub(r"<b>\s*(?:<br\s*/?>\s*)*</b>", "", body, flags=re.I)
    body = re.sub(r"<i>\s*(?:<br\s*/?>\s*)*</i>", "", body, flags=re.I)
    # 标签尖括号内空属性/多余空格：<p \n\n> -> <p>
    body = re.sub(r"<(\w+)\s*/?>", r"<\1>", body, flags=re.I)
    body = re.sub(r"<(/?\w+)\s+>", r"<\1>", body, flags=re.I)
    # 不间断空格实体统一转普通空格：十进制 &#160; / 十六进制 &#xa0; / 命名 &nbsp;。
    # 注意：源里大量使用 `&#160;` 数字实体形式，只处理字面 `&nbsp;` 会漏掉
    # （法术详述.tid 即此情况，满篇 `变化系&#160;<br>`）。
    body = re.sub(r"&(?:#0*160|#x0*a0|nbsp);", " ", body, flags=re.I)
    return body.replace("\r", "")


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"</?[^>]+>", "", s)).strip()


def collapse_ws(s):
    """压掉标签内部的多余空白（含跨行空行），保留单空格分隔。"""
    return re.sub(r"\s*\n\s*", " ", s).strip()


# ---------------------------------------------------------------- 表格紧凑化
def norm_table(block):
    """表格紧凑化：去 colgroup/tbody/width/style，td 仅保留 rowspan/colspan，压平内部 p。"""
    b = re.sub(r"<colgroup>.*?</colgroup>", "", block, flags=re.S | re.I)
    b = re.sub(r"</?tbody[^>]*>", "", b, flags=re.I)
    b = re.sub(r"<table\b[^>]*>", "<table>", b, flags=re.I)
    b = re.sub(r"<tr\b[^>]*>", "<tr>", b, flags=re.I)

    def _td(m):
        attrs = m.group(1)
        kept = re.findall(r"(?:colspan|rowspan)\s*=\s*[\"']?\d+[\"']?", attrs, re.I)
        return f"<td {' '.join(kept)}>".rstrip() + ">" if kept else "<td>"

    b = re.sub(r"<td\b([^>]*)>", _td, b, flags=re.I)
    b = re.sub(r"</?p\b[^>]*>", "", b, flags=re.I)
    b = b.replace("\n", " ")
    b = re.sub(r">\s+<", "><", b)
    b = re.sub(r"<td([^>]*)>\s+", r"<td\1>", b)
    b = re.sub(r"\s+</td>", "</td>", b)
    b = re.sub(r"\s{2,}", " ", b)
    return b.strip()


# ---------------------------------------------------------------- 主体
def clean_body(body):
    nb = normalize(body)

    # 1) 表格 -> 占位符
    tables = []

    def _t(m):
        tables.append(norm_table(m.group(0)))
        return "\u0000TABLE\u0000"

    nb = TABLE_RE.sub(_t, nb)

    # 2) 非表格区：按 <p> 块与裸文本切分
    out = []
    pos = 0
    ti = iter(tables)
    for m in re.finditer(r"\u0000TABLE\u0000", nb):
        out.extend(_clean_seg(nb[pos : m.start()]))
        out.append(next(ti))
        pos = m.end()
    out.extend(_clean_seg(nb[pos:]))

    res = "\n\n".join(c for c in out if c and c.strip())
    # 全角 ASCII 转半角（遵守 tid 内禁全角字母/数字/括号规则）
    res = cp.normalize_fullwidth_punct(res)
    res = re.sub(r"\n{3,}", "\n\n", res)
    return res.strip()


def _clean_seg(seg):
    """处理非表格片段：逐块提取 <p> 与 <h1-6>（避免段内余下内容被丢弃）。

    重要：早期版本用 split + `^<p...>(.*?)</p>` 只取段内第一对 <p>，
    导致段内其余内容被静默丢弃。改为 finditer 遍历所有块级元素，块间裸文本也保留。
    """
    out = []
    BLOCK = re.compile(r"<p\b[^>]*>.*?</p>|<h[1-6]\b[^>]*>.*?</h[1-6]>", re.S | re.I)
    pos = 0
    for m in BLOCK.finditer(seg):
        # 块之前的裸文本（未被块级标签包裹的内容）
        bare = seg[pos : m.start()]
        if bare.strip():
            out.extend(_emit_para(bare))
        out.extend(_emit_block(m.group(0)))
        pos = m.end()
    tail = seg[pos:]
    if tail.strip():
        out.extend(_emit_para(tail))
    return out


def _emit_block(block):
    """处理单个块级元素：<h*> 原样保留；<p> 做压平。"""
    hm = re.match(r"^(<h([1-6])\b[^>]*>)(.*?)(</h\2>)$", block, re.S | re.I)
    if hm:
        # 已是标题，压平内部空白后原样保留
        return [f"{hm.group(1)}{collapse_ws(hm.group(3))}{hm.group(4)}"]
    pm = re.match(r"^<p\b[^>]*>(.*?)</p>$", block, re.S | re.I)
    if pm:
        return _emit_para(pm.group(1))
    return _emit_para(re.sub(r"<[^>]+>", "", block))


BR_SPLIT_RE = re.compile(r"<br\s*/?>", re.I)


def _balance_tags(frag):
    """修复跨 <br> 切分造成的内联标签不平衡。

    `<br>` 常落在内联标签内部（如 `<b>武器吸收 <br></b>变化系`），直接切分会产生
    `<b>X ` 与 `</b>Y ` 这类半截标签。此处丢弃孤立闭标签、补齐未闭合标签。
    """
    out = []
    stack = []
    pos = 0
    for m in re.finditer(r"<(/?)([a-zA-Z0-9]+)[^>]*?(/?)>", frag):
        closing, name, self_close = m.group(1), m.group(2).lower(), m.group(3)
        out.append(frag[pos : m.start()])
        pos = m.end()
        if self_close:
            out.append(m.group(0))
        elif closing:
            if name in stack:
                del stack[len(stack) - 1 - stack[::-1].index(name) :]
                out.append(m.group(0))
            # 孤立闭标签（无对应开标签）：丢弃
        else:
            stack.append(name)
            out.append(m.group(0))
    out.append(frag[pos:])
    return "".join(out) + "".join(f"</{t}>" for t in reversed(stack))


def _emit_para(inner):
    """把片段压平为一个或多个 <p>：<br> 视作段落分隔（CAd 不做 h4 提升，保持原结构）。

    对齐全库「p 内 br 改 p」规范；表格/表格单元格内的 <br> 由 norm_table 保留。
    """
    if not strip_tags(inner):
        return []
    parts = BR_SPLIT_RE.split(inner)
    if len(parts) > 1:
        out = []
        for part in parts:
            out.extend(_emit_para(_balance_tags(part)))
        return out
    tags = set(t.lower() for t in re.findall(r"</?([a-zA-Z0-9]+)", inner))
    if tags <= SAFE_TAGS:
        return [f"<p>{collapse_ws(inner)}</p>"]
    return [f"<p>{collapse_ws(strip_tags(inner))}</p>"]


# ---------------------------------------------------------------- 处理
# 噪音标记集：强 Word 标记 + 弱噪音（<span>/<div>/&nbsp;/任意标签的 style/class/lang）。
# 教训（见 contexts.md MIC 记录）：只认 mso-/o:p 等强标记会漏判弱噪音文件，
# 导致其被误判为「干净源」跳过、残留噪音。
WORD_MARK_RE = re.compile(
    r"mso-|<o:p|o:p>|FONT\s+face|SPAN\s+style|class=p\b|"
    r"xml:namespace|EndFragment|StartFragment|WinCHM|lang=EN-US|"
    r"&nbsp;|&#0*160;|&#x0*a0;|</?span|</?div|style\s*=|class\s*=|lang\s*=|</?br",
    re.I,
)


def is_clean_source(body):
    """已是干净格式（无 Word 噪音标记）的页面直接跳过，避免改动已正确的文件。"""
    return not WORD_MARK_RE.search(body)


def split_tid(raw):
    """按 tid 规范分割 header（开头连续的 `key: value` 行）与 body。

    不能用固定 5 行：早期版本写入时丢了 header 后的空行，导致下一轮再读时
    正文首段被误当作 header 而跳过处理（法术详述.tid 的巨大首段即踩此坑）。
    改为按「开头连续的 key: value 行」识别 header，天然免疫空行丢失。
    """
    m = re.match(r"((?:[A-Za-z_][\w-]*:[^\n]*\n)+)", raw)
    if m:
        return m.group(1), raw[m.end() :]
    return "", raw


def process(apply=False):
    files = []
    for root, dirs, fs in os.walk(CAD):
        dirs[:] = [x for x in dirs if not x.endswith(".files")]
        for x in sorted(fs):
            if x.lower().endswith(".tid"):
                files.append(os.path.join(root, x))
    stats = {"files": 0, "changed": 0, "h4": 0, "p": 0, "tb": 0, "ta": 0}
    lost = []
    samples = []
    for path in files:
        raw = open(path, encoding="utf-8").read()
        header, body = split_tid(raw)
        # 干净源（无 Word 噪音）已是理想格式，直接跳过，不参与重排
        if is_clean_source(body):
            stats["files"] += 1
            stats["skipped"] = stats.get("skipped", 0) + 1
            continue
        new_body = clean_body(body)
        stats["files"] += 1
        stats["p"] += len(re.findall(r"<p>", new_body))
        if new_body != body.strip():
            stats["changed"] += 1
        # 自检：基线同样过 normalize 后比对可见字符
        tb = re.sub(r"\s+", "", strip_tags(normalize(body)))
        ta = re.sub(r"\s+", "", strip_tags(new_body))
        stats["tb"] += len(tb)
        stats["ta"] += len(ta)
        if abs(len(ta) - len(tb)) > max(30, len(tb) * 0.01):
            lost.append((os.path.relpath(path, CAD), len(tb), len(ta)))
        if len(samples) < 2 and new_body != body.strip():
            samples.append((os.path.relpath(path, CAD), new_body[:600]))
        if apply and new_body != body.strip():
            with open(path, "w", encoding="utf-8") as fh:
                # header 后必须保留空行（tid 规范），否则下一轮读取会错位
                fh.write(header.rstrip("\n") + "\n\n" + new_body + "\n")
    return stats, lost, samples


def main():
    apply = "--apply" in sys.argv
    if apply:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = os.path.join(WORK, f"backup_cad_clean_{ts}")
        os.makedirs(bak, exist_ok=True)
        for root, dirs, fs in os.walk(CAD):
            dirs[:] = [x for x in dirs if not x.endswith(".files")]
            rel = os.path.relpath(root, CAD)
            for x in fs:
                if x.lower().endswith(".tid"):
                    d2 = os.path.join(bak, rel)
                    os.makedirs(d2, exist_ok=True)
                    shutil.copy2(os.path.join(root, x), os.path.join(d2, x))
        print(f"[备份] -> {bak}\n")

    stats, lost, samples = process(apply=apply)
    print(
        f"文件 {stats['files']}  跳过(干净源) {stats.get('skipped', 0)}  "
        f"修改 {stats['changed']}  <p> {stats['p']}"
    )
    print(f"可见字符 {stats['tb']} -> {stats['ta']}")
    if lost:
        print(f"[!! 字符数异常 {len(lost)}] " + "; ".join(f"{f} {b}->{a}" for f, b, a in lost[:8]))
    for name, txt in samples:
        print(f"\n----- 样本 {name} -----")
        print(txt)
    if not apply:
        print("\n（干跑，未写入。加 --apply 执行并自动备份）")


if __name__ == "__main__":
    main()
