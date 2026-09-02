# -*- coding: utf-8 -*-
"""MIC万物大全 噪音页结构化重排（复用 clean_mm5.py 的 normalize/自检思路，针对 MIC 物品条目改造）。

背景：MIC 源与 MM3/MM4/MM5 同源（Word/WinCHM 导出），46/51 页带 Word 噪音：
      <p \n\n>（空属性跨行）、<span \n\n style='mso-*...'>、<o:P>、<?xml:namespace>、
      lang=EN-US、连续空行。convert_book 清洗不彻底，需重排。

目标格式（对齐 MIC 干净源，如 穿戴物/身体.tid）：
  <h4>物品名(ENGLISH)</h4>
  <p><b>价格</b>(物品等级)：5000GP(9)</p>
  <p><b>部位</b>：身体</p>
  ...（其余字段）

与 clean_mm5.py 的区别：
  1. 不做「表格字段化」——MM5 是怪物 2 列数据表；MIC 主体是「物品名 + 字段段落」，
     表格仅少数页面（价格清单等），统一做紧凑化处理（对齐 XPH 表格规范）。
  2. 不生成文件名 h5——MIC 标题来自正文（<h4>/<b>物品名</b>）。
  3. 物品名识别：整段仅为 <b>中文名(EN)</b> 且不含「：」的段落 -> <h4>。

安全设计：
  1. 先 normalize 去全部 Word 标签噪音，再解析结构
  2. 物品名用严格正则（中文/英文括号 + 不含冒号）判定，避免误伤字段行
  3. 内容丢失自检：基线同样过 normalize 后比对可见字符数

用法：
  python clean_mic.py            # 干跑，输出统计与样本
  python clean_mic.py --apply    # 实际写入（先自动备份到 work/）
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

MIC = os.path.join(P.WIKI_TIDDLERS, "2 万物万法万律", "MIC万物大全")
WORK = P.WORK

# 物品名：中文名(ENGLISH) —— 全段仅为 <b>...</b> 且匹配此模式才转 h4
ITEM_TITLE_PLAIN = re.compile(
    r"^[\u4e00-\u9fff·\w\-\s'\.,/&]+[（(]\s*[A-Za-z][\w\s'\-,\./&]*\s*[）)]$"
)
TABLE_RE = re.compile(r"<table[^>]*>.*?</table>", re.S | re.I)
P_BLOCK_RE = re.compile(r"<p\b[^>]*>.*?</p>", re.S | re.I)
SAFE_TAGS = {"b", "i", "u", "em", "strong", "br", "img", "sub", "sup"}


# ---------------------------------------------------------------- normalize
def normalize(body):
    """机械去噪：注释、o:p/u1:p、span、font、style/class/lang、xml:namespace、空属性。"""
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
    return body.replace("&nbsp;", " ").replace("\r", "")


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
def is_item_title(inner):
    """整段是否仅为 <b>物品名(EN)</b>（不含冒号，匹配 中文(EN) 模式）。"""
    m = re.match(r"^\s*<(b|strong)>(.*?)</\1>\s*$", inner, re.S | re.I)
    if not m:
        return None
    text = strip_tags(m.group(2))
    if "：" in text or ":" in text:
        return None
    if ITEM_TITLE_PLAIN.match(text):
        return text
    return None


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
        out.extend(_clean_seg(nb[pos:m.start()]))
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
    导致段内其余内容（尤其是干净源已有的 <h4> 物品名标题）被静默丢弃
    （身体/头部/躯干/项链_护符/+1/特殊武器 6 个文件共丢 140~652 字）。
    改为 finditer 遍历所有块级元素，块间裸文本也保留。
    """
    out = []
    BLOCK = re.compile(
        r"<p\b[^>]*>.*?</p>|<h[1-6]\b[^>]*>.*?</h[1-6]>", re.S | re.I
    )
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
    """处理单个块级元素：<h*> 原样保留；<p> 做物品名识别与压平。"""
    hm = re.match(r"^(<h([1-6])\b[^>]*>)(.*?)(</h\2>)$", block, re.S | re.I)
    if hm:
        # 已是标题（干净源），压平内部空白后原样保留
        return [f"{hm.group(1)}{collapse_ws(hm.group(3))}{hm.group(4)}"]
    pm = re.match(r"^<p\b[^>]*>(.*?)</p>$", block, re.S | re.I)
    if pm:
        return _emit_para(pm.group(1))
    return _emit_para(re.sub(r"<[^>]+>", "", block))


def _emit_para(inner):
    """把片段压平为一个 <p>；若是纯 <b>物品名(EN)</b> 则转 <h4>。"""
    plain = strip_tags(inner)
    if not plain:
        return []
    title = is_item_title(inner)
    if title:
        return [f"<h4>{title}</h4>"]
    tags = set(t.lower() for t in re.findall(r"</?([a-zA-Z0-9]+)", inner))
    if tags <= SAFE_TAGS:
        return [f"<p>{collapse_ws(inner)}</p>"]
    return [f"<p>{collapse_ws(plain)}</p>"]


# ---------------------------------------------------------------- 处理
WORD_MARK_RE = re.compile(
    r"mso-|<o:p|o:p>|FONT\s+face|SPAN\s+style|class=p\b|"
    r"xml:namespace|EndFragment|StartFragment|WinCHM|lang=EN-US|"
    r"&nbsp;|</?span|</?div|style\s*=|class\s*=|lang\s*=",
    re.I,
)


def is_clean_source(body):
    """已是干净格式（无 Word 噪音标记）的页面直接跳过，避免改动已正确的文件。"""
    return not WORD_MARK_RE.search(body)


def process(apply=False):
    files = []
    for root, dirs, fs in os.walk(MIC):
        dirs[:] = [x for x in dirs if not x.endswith(".files")]
        for x in sorted(fs):
            if x.lower().endswith(".tid"):
                files.append(os.path.join(root, x))
    stats = {"files": 0, "changed": 0, "h4": 0, "p": 0, "tb": 0, "ta": 0}
    lost = []
    samples = []
    for path in files:
        raw = open(path, encoding="utf-8").read()
        lines = raw.split("\n")
        header, body = "\n".join(lines[:5]), "\n".join(lines[5:])
        # 干净源（无 Word 噪音）已是理想格式，直接跳过，不参与重排
        if is_clean_source(body):
            stats["files"] += 1
            stats["skipped"] = stats.get("skipped", 0) + 1
            continue
        new_body = clean_body(body)
        stats["files"] += 1
        stats["h4"] += new_body.count("<h4>")
        stats["p"] += len(re.findall(r"<p>", new_body))
        if new_body != body.strip():
            stats["changed"] += 1
        # 自检：基线同样过 normalize 后比对可见字符
        tb = re.sub(r"\s+", "", strip_tags(normalize(body)))
        ta = re.sub(r"\s+", "", strip_tags(new_body))
        stats["tb"] += len(tb)
        stats["ta"] += len(ta)
        if abs(len(ta) - len(tb)) > max(30, len(tb) * 0.01):
            lost.append((os.path.relpath(path, MIC), len(tb), len(ta)))
        if samples.__len__() < 2 and new_body != body.strip():
            samples.append((os.path.relpath(path, MIC), new_body[:600]))
        if apply and new_body != body.strip():
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(header + new_body + "\n")
    return stats, lost, samples


def main():
    apply = "--apply" in sys.argv
    if apply:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = os.path.join(WORK, f"backup_mic_clean_{ts}")
        os.makedirs(bak, exist_ok=True)
        for root, dirs, fs in os.walk(MIC):
            dirs[:] = [x for x in dirs if not x.endswith(".files")]
            rel = os.path.relpath(root, MIC)
            for x in fs:
                if x.lower().endswith(".tid"):
                    d2 = os.path.join(bak, rel)
                    os.makedirs(d2, exist_ok=True)
                    shutil.copy2(os.path.join(root, x), os.path.join(d2, x))
        print(f"[备份] -> {bak}\n")

    stats, lost, samples = process(apply=apply)
    print(
        f"文件 {stats['files']}  跳过(干净源) {stats.get('skipped', 0)}  "
        f"修改 {stats['changed']}  h4 {stats['h4']}  <p> {stats['p']}"
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
