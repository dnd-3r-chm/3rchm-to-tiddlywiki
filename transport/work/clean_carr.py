# -*- coding: utf-8 -*-
"""CAr完美奥术 噪音页清理（复用 clean_cad.py 的去噪/表格紧凑化/自检）。

背景：CAr 源是混合格式——职业/法术/物品页是 DND3R 在线勘误版（干净），
但生物页（及部分进阶/战役/专长页）实为 WinCHM/Word 导出，带 mso-* 内联 style、
<font>/<span>/<u1:p>/<o:p>、lang=EN-US、跨行属性等噪音。convert_book 后残留，
违反全库「Word 噪音清零」铁律，故补一次清理（与 CAd 同理）。

相对 clean_cad.py 的调整：
  * 指向 CAr 目录。
  * 保护 <section class="official-errata"> 原样（红框 style + 内部 h2/p 不被动），
    避免勘误块被 _clean_seg 拆成裸文本丢标签。
  * 其余（normalize 去 div/span/font/style/class/lang/u1:p/o:p/xml:namespace/nbsp、
    表格紧凑化、全角转半角、内容丢失自检）沿用 clean_cad。

安全设计（同 clean_cad）：
  * 内容丢失自检：基线过 normalize 后比对可见字符数。
  * --apply 前自动备份到 work/backup_carr_clean_<时间戳>。
  * 干净源（无 WORD_MARK 标记）直接跳过。

用法：
  python clean_carr.py            # 干跑，输出统计与样本
  python clean_carr.py --apply    # 实际写入（先自动备份）
"""
import datetime
import html
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P
import convert_pilot as cp

CAR = os.path.join(P.WIKI_TIDDLERS, "3 完美系列", "CAr完美奥术")
WORK = P.WORK

TABLE_RE = re.compile(r"<table[^>]*>.*?</table>", re.S | re.I)
SAFE_TAGS = {"b", "i", "u", "em", "strong", "br", "img", "sub", "sup"}
SECTION_RE = re.compile(
    r"<section\b[^>]*class=['\"][^'\"]*official-errata[^'\"]*['\"][^>]*>.*?</section>",
    re.S | re.I,
)


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


# ---------------------------------------------------------------- 表格紧凑化
def norm_table(block):
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
    # 1) 保护 official-errata section 原样（红框 + 内部 h2/p 不被动）
    sections = []

    def _s(m):
        sections.append(m.group(0))
        return f"\u0001SEC{len(sections) - 1}\u0001"

    body = SECTION_RE.sub(_s, body)
    nb = normalize(body)

    # 2) 表格 -> 占位符
    tables = []

    def _t(m):
        tables.append(norm_table(m.group(0)))
        return "\u0000TABLE\u0000"

    nb = TABLE_RE.sub(_t, nb)

    # 3) 非表格区：按 <p> 块 / <h1-6> 块 / section 占位符 切分
    out = []
    pos = 0
    ti = iter(tables)
    for m in re.finditer(r"\u0000TABLE\u0000", nb):
        out.extend(_clean_seg(nb[pos : m.start()]))
        out.append(next(ti))
        pos = m.end()
    out.extend(_clean_seg(nb[pos:]))

    res = "\n\n".join(c for c in out if c and c.strip())
    res = cp.normalize_fullwidth_punct(res)
    res = re.sub(r"\n{3,}", "\n\n", res)
    # 还原 section
    for i, t in enumerate(sections):
        res = res.replace(f"\u0001SEC{i}\u0001", t)
    # 清除 HTML 实体引号（含被保护的 section 内部勘误引用）
    res = res.replace("&quot;", '"').replace("&#39;", "'")
    return res.strip()


def _clean_seg(seg):
    out = []
    BLOCK = re.compile(
        r"<p\b[^>]*>.*?</p>|<h[1-6]\b[^>]*>.*?</h[1-6]>|\u0001SEC\d+\u0001",
        re.S | re.I,
    )
    pos = 0
    for m in BLOCK.finditer(seg):
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
    if re.match(r"^\u0001SEC\d+\u0001$", block):
        return [block]
    hm = re.match(r"^(<h([1-6])\b[^>]*>)(.*?)(</h\2>)$", block, re.S | re.I)
    if hm:
        return [f"{hm.group(1)}{collapse_ws(hm.group(3))}{hm.group(4)}"]
    pm = re.match(r"^<p\b[^>]*>(.*?)</p>$", block, re.S | re.I)
    if pm:
        return _emit_para(pm.group(1))
    return _emit_para(re.sub(r"<[^>]+>", "", block))


BR_SPLIT_RE = re.compile(r"<br\s*/?>", re.I)


def _balance_tags(frag):
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
        else:
            stack.append(name)
            out.append(m.group(0))
    out.append(frag[pos:])
    return "".join(out) + "".join(f"</{t}>" for t in reversed(stack))


def _emit_para(inner):
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
WORD_MARK_RE = re.compile(
    r"mso-|<o:p|o:p>|FONT\s+face|SPAN\s+style|class=p\b|"
    r"xml:namespace|EndFragment|StartFragment|WinCHM|lang=EN-US|"
    r"&nbsp;|&#0*160;|&#x0*a0;|&quot;|&#39;|</?span|</?div|style\s*=|class\s*=|lang\s*=|</?br",
    re.I,
)


def is_clean_source(body):
    return not WORD_MARK_RE.search(body)


def split_tid(raw):
    m = re.match(r"((?:[A-Za-z_][\w-]*:[^\n]*\n)+)", raw)
    if m:
        return m.group(1), raw[m.end():]
    return "", raw


def process(apply=False):
    files = []
    for root, dirs, fs in os.walk(CAR):
        dirs[:] = [x for x in dirs if not x.endswith(".files")]
        for x in sorted(fs):
            if x.lower().endswith(".tid"):
                files.append(os.path.join(root, x))
    stats = {"files": 0, "changed": 0, "p": 0, "tb": 0, "ta": 0}
    lost = []
    samples = []
    for path in files:
        raw = open(path, encoding="utf-8").read()
        header, body = split_tid(raw)
        if is_clean_source(body):
            stats["files"] += 1
            stats["skipped"] = stats.get("skipped", 0) + 1
            continue
        new_body = clean_body(body)
        stats["files"] += 1
        stats["p"] += len(re.findall(r"<p>", new_body))
        if new_body != body.strip():
            stats["changed"] += 1
        tb = re.sub(r"\s+", "", strip_tags(html.unescape(normalize(body))))
        ta = re.sub(r"\s+", "", strip_tags(html.unescape(new_body)))
        stats["tb"] += len(tb)
        stats["ta"] += len(ta)
        if abs(len(ta) - len(tb)) > max(30, len(tb) * 0.01):
            lost.append((os.path.relpath(path, CAR), len(tb), len(ta)))
        if len(samples) < 3 and new_body != body.strip():
            samples.append((os.path.relpath(path, CAR), new_body[:700]))
        if apply and new_body != body.strip():
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(header.rstrip("\n") + "\n\n" + new_body + "\n")
    return stats, lost, samples


def main():
    apply = "--apply" in sys.argv
    if apply:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = os.path.join(WORK, f"backup_carr_clean_{ts}")
        os.makedirs(bak, exist_ok=True)
        for root, dirs, fs in os.walk(CAR):
            dirs[:] = [x for x in dirs if not x.endswith(".files")]
            rel = os.path.relpath(root, CAR)
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
