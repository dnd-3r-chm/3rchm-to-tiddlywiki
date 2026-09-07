# -*- coding: utf-8 -*-
"""已搬运书目残留噪音的通用保守清理（复用 clean_cad.py 的 normalize / br 切分思路）。

背景：2026-09-04 全库审计（`_audit_books.py`）发现已搬运书目仍有三类残留：
  1. 段落内 `<br>`：XPH 180 / DMG2 73 / PHB2 18 / MM4 1，违反全库「p 内 br 改 p」规范
  2. 弱标签 `<span>`/`<div>`/`<font>`：PHB2 34 / DMG2 18 / MM4 12 / XPH 10 / MM3 1 / HBG 1
  3. header 后缺空行：早期「固定 5 行分割 + 写入不保留空行」bug 痕迹，共 517 个文件

设计原则（保守，不破坏已有结构化成果）：
  * 只做三件事：normalize 去噪、段落内 <br> 转 <p>、补齐 header 后空行
  * **不做** h4/h5 标题提升（MM3/MM4/MM5 的怪物条目、MIC 的物品条目结构已定型）
  * **不动**表格结构（表格内的 <br> 按规范保留），表格仅过 normalize 去标签噪音
  * 内容丢失自检：异常文件**跳过不写入**，保证宁可不改也不错改

处理范围：默认 `1 核心补充书籍` / `2 万物万法万律` / `3 完美系列` 全部书目；
          干净且已合规的文件自动跳过（幂等，可重复运行）。

用法：
  python clean_residual.py            # 干跑
  python clean_residual.py --apply    # 实际写入（先自动备份到 work/）
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

TARGET_ROOTS = ["1 核心补充书籍", "2 万物万法万律", "3 完美系列"]
WORK = P.WORK
WIKI = P.WIKI_TIDDLERS

TABLE_RE = re.compile(r"<table[^>]*>.*?</table>", re.S | re.I)
BLOCK_RE = re.compile(r"<p\b[^>]*>.*?</p>|<h[1-6]\b[^>]*>.*?</h[1-6]>", re.S | re.I)
BR_SPLIT_RE = re.compile(r"<br\s*/?>", re.I)
SAFE_TAGS = {"b", "i", "u", "em", "strong", "br", "img", "sub", "sup"}


# ---------------------------------------------------------------- normalize
def normalize(body):
    """机械去噪：注释、o:p/u1:p、span/font/div、style/class/lang、xml:namespace、空属性。"""
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r"</?(?:o|u1):[a-zA-Z][^>]*/?>", "", body)
    body = re.sub(r"</?span[^>]*>", "", body, flags=re.I)
    body = re.sub(r"</?font[^>]*>", "", body, flags=re.I)
    body = re.sub(r"</?div[^>]*>", "", body, flags=re.I)
    body = re.sub(r"\sstyle\s*=\s*('[^']*'|\"[^\"]*\"|[^\s>]+)", "", body, flags=re.I | re.S)
    body = re.sub(r"\sclass\s*=\s*('[^']*'|\"[^\"]*\"|[^\s>]+)", "", body, flags=re.I | re.S)
    body = re.sub(r"\slang\s*=\s*(EN-US|ZR|ZH-CN|[^\s>]+)", "", body, flags=re.I)
    body = re.sub(r"<\?xml:namespace[^>]*\/?>", "", body, flags=re.I | re.S)
    body = re.sub(r"<b>\s*(?:<br\s*/?>\s*)*</b>", "", body, flags=re.I)
    body = re.sub(r"<i>\s*(?:<br\s*/?>\s*)*</i>", "", body, flags=re.I)
    body = re.sub(r"<(\w+)\s*/?>", r"<\1>", body, flags=re.I)
    body = re.sub(r"<(/?\w+)\s+>", r"<\1>", body, flags=re.I)
    body = re.sub(r"&(?:#0*160|#x0*a0|nbsp);", " ", body, flags=re.I)
    return body.replace("\r", "")


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"</?[^>]+>", "", s)).strip()


def collapse_ws(s):
    return re.sub(r"\s*\n\s*", " ", s).strip()


def split_tid(raw):
    """按 tid 规范分割 header（开头连续的 `key: value` 行）与 body。"""
    m = re.match(r"((?:[A-Za-z_][\w-]*:[^\n]*\n)+)", raw)
    if m:
        return m.group(1), raw[m.end() :]
    return "", raw


# ---------------------------------------------------------------- 块处理
def _balance_tags(frag):
    """修复跨 <br> 切分造成的内联标签不平衡：丢弃孤立闭标签、补齐未闭合标签。"""
    out, stack, pos = [], [], 0
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
        else:
            stack.append(name)
            out.append(m.group(0))
    out.append(frag[pos:])
    return "".join(out) + "".join(f"</{t}>" for t in reversed(stack))


def _emit_para(inner):
    """把片段压平为一个或多个 <p>：先按 <br> 切分（表格外）。"""
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


def _emit_block(block):
    """<h*> 原样保留（压平内部空白）；<p> 走 _emit_para。"""
    hs = _split_heading_br(block)
    if hs:
        return hs
    hm = re.match(r"^(<h([1-6])\b[^>]*>)(.*?)(</h\2>)$", block, re.S | re.I)
    if hm:
        return [f"{hm.group(1)}{collapse_ws(hm.group(3))}{hm.group(4)}"]
    pm = re.match(r"^<p\b[^>]*>(.*?)</p>$", block, re.S | re.I)
    if pm:
        return _emit_para(pm.group(1))
    return _emit_para(re.sub(r"<[^>]+>", "", block))


def _split_heading_br(block):
    """标题内 <br> 转空格：`<h2>血拳部落<br><i>(Bloodfist Tribe)</i></h2>`
    -> `<h2>血拳部落 <i>(Bloodfist Tribe)</i></h2>`。

    对齐 CAd 规范（`<h4>高级炼金术 Augmented Alchemy [传奇]</h4>` 中英文名空格连排）。
    保留 `<i>` 等内联标签；跨 br 的标签不平衡用 _balance_tags 修复。
    """
    hm = re.match(r"^(<h([1-6])\b[^>]*>)(.*?)(</h\2>)$", block, re.S | re.I)
    if not hm or not BR_SPLIT_RE.search(hm.group(3)):
        return None
    open_t, inner, close_t = hm.group(1), hm.group(3), hm.group(4)
    parts = [_balance_tags(p) for p in BR_SPLIT_RE.split(inner)]
    merged = " ".join(p.strip() for p in parts if p.strip())
    return [f"{open_t}{collapse_ws(merged)}{close_t}"]


def _clean_seg(seg):
    """非表格片段：逐块提取 <p>/<h1-6>，块间裸文本保留（避免内容丢失）。"""
    out, pos = [], 0
    for m in BLOCK_RE.finditer(seg):
        bare = seg[pos : m.start()]
        if bare.strip():
            out.extend(_emit_para(bare))
        out.extend(_emit_block(m.group(0)))
        pos = m.end()
    tail = seg[pos:]
    if tail.strip():
        out.extend(_emit_para(tail))
    return out


def clean_body(body):
    """去噪 + 表格外 br 转 p。表格保持原样（内部结构不动，仅过 normalize）。"""
    nb = normalize(body)
    tables = []

    def _t(m):
        tables.append(m.group(0))
        return "\u0000TABLE\u0000"

    nb = TABLE_RE.sub(_t, nb)
    out, pos = [], 0
    ti = iter(tables)
    for m in re.finditer(r"\u0000TABLE\u0000", nb):
        out.extend(_clean_seg(nb[pos : m.start()]))
        out.append(next(ti))
        pos = m.end()
    out.extend(_clean_seg(nb[pos:]))
    res = "\n\n".join(c for c in out if c and c.strip())
    res = cp.normalize_fullwidth_punct(res)
    return re.sub(r"\n{3,}", "\n\n", res).strip()


# ---------------------------------------------------------------- 处理
def needs_blank_fix(body):
    """header 与正文之间是否缺空行（tid 规范要求空行分隔）。"""
    return bool(body.strip()) and not re.match(r"^\s*\n", body)


def walk_tids(book_dir, exclude_rels=()):
    """遍历书目目录下的 .tid；exclude_rels 为相对 book_dir 的子目录（整棵子树跳过）。

    用于保护人工调整过的章节（如 DMG 简介/第一章/第二章含大量已合并节点，
    见 convert_book.py 的 SKIP_SOURCES），避免清理脚本覆盖手动成果。
    """
    ex = {os.path.normpath(p) for p in exclude_rels}
    for root, dirs, fs in os.walk(book_dir):
        dirs[:] = [d for d in dirs if not d.endswith(".files")]
        rel = os.path.relpath(root, book_dir)
        if rel == ".":
            rel = ""
        if rel and any(rel == e or rel.startswith(e + os.sep) for e in ex):
            dirs[:] = []  # 剪枝：整棵子树排除
            continue
        for x in sorted(fs):
            if x.lower().endswith(".tid"):
                yield os.path.join(root, x)


def process(book_dirs, exclude_map=None, apply=False):
    """处理指定书目目录列表；exclude_map: {书目目录: [要排除的相对子目录, ...]}。"""
    exclude_map = exclude_map or {}
    stats = {"files": 0, "changed": 0, "blank_fix": 0, "skipped": 0,
             "tb": 0, "ta": 0}
    lost, per_book = [], {}
    for bdir in book_dirs:
        if not os.path.isdir(bdir):
            continue
        name = os.path.relpath(bdir, WIKI)
        bs = {"files": 0, "changed": 0, "blank_fix": 0}
        for path in walk_tids(bdir, exclude_map.get(bdir, ())):
            raw = open(path, encoding="utf-8").read()
            header, body = split_tid(raw)
            stats["files"] += 1
            bs["files"] += 1
            new_body = clean_body(body)
            blank_fix = needs_blank_fix(body)
            # 自检：基线同样过 normalize 后比对可见字符
            tb = re.sub(r"\s+", "", strip_tags(normalize(body)))
            ta = re.sub(r"\s+", "", strip_tags(new_body))
            stats["tb"] += len(tb)
            stats["ta"] += len(ta)
            if abs(len(ta) - len(tb)) > max(30, len(tb) * 0.01):
                lost.append((os.path.relpath(path, WIKI), len(tb), len(ta)))
                continue  # 异常则跳过，不写入
            if new_body == body.strip() and not blank_fix:
                stats["skipped"] += 1
                continue
            bs["changed"] += 1
            stats["changed"] += 1
            if blank_fix:
                bs["blank_fix"] += 1
                stats["blank_fix"] += 1
            if apply:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(header.rstrip("\n") + "\n\n" + new_body + "\n")
        if bs["changed"]:
            per_book[name] = bs
    return stats, lost, per_book


def backup(book_dirs, exclude_map=None):
    """备份指定书目目录下的 .tid（同样遵守 exclude_map，只备份会被处理的文件）。"""
    exclude_map = exclude_map or {}
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = os.path.join(WORK, f"backup_residual_{ts}")
    os.makedirs(bak, exist_ok=True)
    for bdir in book_dirs:
        if not os.path.isdir(bdir):
            continue
        for path in walk_tids(bdir, exclude_map.get(bdir, ())):
            rel = os.path.relpath(path, WIKI)
            d2 = os.path.join(bak, os.path.dirname(rel))
            os.makedirs(d2, exist_ok=True)
            shutil.copy2(path, os.path.join(bak, rel))
    return bak


def collect_books(roots):
    """收集一级目录下所有书目目录（默认全量入口）。"""
    books = []
    for tr in roots:
        base = os.path.join(WIKI, tr)
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            d = os.path.join(base, name)
            if os.path.isdir(d):
                books.append(d)
    return books


def run(book_dirs, exclude_map=None, apply=False):
    """供外部常量脚本调用（规避 PowerShell 中文传参乱码）。"""
    if apply:
        print(f"[备份] -> {backup(book_dirs, exclude_map)}\n")
    stats, lost, per_book = process(book_dirs, exclude_map, apply=apply)
    print(
        f"文件 {stats['files']}  修改 {stats['changed']}  "
        f"(其中补齐空行 {stats['blank_fix']})  跳过(已合规) {stats['skipped']}"
    )
    print(f"可见字符 {stats['tb']} -> {stats['ta']}")
    if lost:
        print(f"\n[!! 字符数异常，已跳过 {len(lost)} 个文件]")
        for f, b, a in lost[:10]:
            print(f"    {f}  {b} -> {a}")
    print()
    for name, bs in per_book.items():
        print(f"  {name}: 修改 {bs['changed']}/{bs['files']}（补空行 {bs['blank_fix']}）")
    if not apply:
        print("\n（干跑，未写入。加 --apply 执行并自动备份）")


def main():
    apply = "--apply" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    roots = args if args else TARGET_ROOTS
    run(collect_books(roots), apply=apply)


if __name__ == "__main__":
    main()
