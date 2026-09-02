# -*- coding: utf-8 -*-
"""MM5怪物图鉴5 噪音页结构化重排（复用 clean_mm4.py 思路，针对 MM5 表格字段化）。

背景：MM3 由 Word 导出，怪物词条为「标题 + 斜体描述 + 2列数据表」结构。
噪音：<!--StartFragment-->、非空 <o:p>/<o:P>、<u1:p>/<u1:P>、断裂的 <span\n>、未闭合 <font>、
      海量 &nbsp;、mso- 样式属性、连续 <br>。

目标格式（对齐 PHB 怪物 / clean_xph.py 字段化）：
  <h5>中文名(ENGLISH) CR N</h5>
  <p><i>描述段落</i></p>
  <p><b>字段名：</b>值</p>
  ...（其余字段）

与 clean_xph.py 的区别：XPH 保留表格原样；MM3 的怪物数据在表格内，
本脚本解析 2 列表格并字段化为 <p><b>字段：</b>值</p>。

安全设计：
  1. 先 normalize 去全部 Word 标签噪音，再解析结构
  2. 表格行用白名单字段名判定，非字段行（如无字段名的纯文本行）原样保留
  3. 标题两遍校验：仅当其后随「描述/字段」才确认为 h5
  4. 内容丢失自检：基线同样过 normalize

用法：
  python clean_mm3.py            # 干跑，只输出统计与样本
  python clean_mm3.py --apply     # 实际写入（先自动备份）
"""
import _paths as P
import datetime
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")

PREFIX = "1 核心补充书籍\\MM5怪物图鉴5"
MM3 = os.path.join(P.WIKI_TIDDLERS, PREFIX)  # 变量名沿用，指向 MM5 目录

# 含怪物词条的子目录（噪音主要在此）；"怪物" 会遍历其下所有 tid（含子目录与顶层文件）
TARGET_DIRS = ["怪物"]
# 排除 Word 资源目录（如 碎魂杀手.files）

# ---------------------------------------------------------------- 字段白名单
MONSTER_FIELDS = {
    "生命值", "生命骰", "先攻权", "先攻", "速度", "防御等级", "基本攻击/擒抱",
    "基本攻击／擒抱", "基础攻击/擒抱", "基础攻击／擒抱", "攻击", "全力攻击",
    "全回合攻击", "面宽/触及", "面宽／触及", "特殊攻击", "特性", "属性值", "属性",
    "技能", "专长", "环境", "组织", "挑战等级", "挑战级数", "宝藏", "阵营", "进化",
    "等级调整", "类灵能能力", "心灵异能", "豁免", "豁免检定", "天生异能",
    "天生语言", "自动语言", "天赋职业", "构装体特性", "虚体特性", "异能抗力",
    "盲视", "法术抗力", "阵营与进化", "特殊能力",
}

# ---------------------------------------------------------------- 正则
# 标题行两种顺序兼容：
#   中文(English) CR N       例：伏龙兽(Ambush Drake) CR 5
#   ENGLISH 中文 CR N（无括号）例：Alchemical Golem 炼金术魔像
TITLE_RE = re.compile(
    r"^(?:"
    r"[\u4e00-\u9fff·\w]+[（(][A-Za-z][\w\s'\-,\./]*[）)]\s*CR\s*\d+(?:/\d+)?"
    r"|"
    r"[A-Za-z][\w\s'\-,\./]*[\u4e00-\u9fff·]+?(?:CR\s*\d+(?:/\d+)?)?"
    r")$"
)
# 中文(English) -> h5 中文(English)
LEAD_EN_RE = re.compile(r"^([\u4e00-\u9fff·\w]+)\s+([A-Za-z][\w\s'\-,\./]*)$")
FIELD_SPLIT = re.compile(r"^([^：:]{1,28})[：:](.*)$", re.S)
TABLE_RE = re.compile(r"<table[^>]*>(.*?)</table>", re.S | re.I)
TR_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S | re.I)
TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S | re.I)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.S | re.I)
SAFE_TAGS = {"b", "i", "u", "em", "strong", "br"}


def normalize(body):
    """机械去噪：注释、o:p/u1:p（含大小写变体）、span、font、mso-样式、nbsp。"""
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    # <o:p> <o:P> </o:p> </o:P> 及 <u1:p> <u1:P> 等命名空间标签
    body = re.sub(r"</?(?:o|u1):[a-zA-Z][^>]*/?>", "", body)
    body = re.sub(r"</?span[^>]*>", "", body, flags=re.I)
    body = re.sub(r"</?font[^>]*>", "", body, flags=re.I)
    # mso- 样式属性（style='...mso-...' 整体删 style）
    body = re.sub(r"\sstyle\s*=\s*('[^']*'|\"[^\"]*\"|[^\s>]+)", "", body, flags=re.I)
    body = re.sub(r"\sclass\s*=\s*('[^']*'|\"[^\"]*\"|[^\s>]+)", "", body, flags=re.I)
    body = re.sub(r"\slang\s*=\s*(EN-US|ZR|ZH-CN|[^\s>]+)", "", body, flags=re.I)
    # XML 命名空间声明（Word 噪音） <?xml:namespace ... /> 可能跨行、自闭合
    body = re.sub(r"<\?xml:namespace[^>]*\/?>", "", body, flags=re.I | re.S)
    # CR 与数字被换行拆开时归一化： "CR \n5" -> "CR 5"
    body = re.sub(r"CR\s*\r?\n\s*(\d+(?:/\d+)?)", r"CR \1", body)
    # 空加粗/空斜体残留 <b><br></b> <b></b>
    body = re.sub(r"<b>\s*(?:<br\s*/?>\s*)*</b>", "", body, flags=re.I)
    body = re.sub(r"<i>\s*(?:<br\s*/?>\s*)*</i>", "", body, flags=re.I)
    # 标签尖括号内多余空格/属性残留： <p > <p class="" > -> <p>
    body = re.sub(r"<(\w+)\s*/?>", r"<\1>", body, flags=re.I)
    body = re.sub(r"<(/?\w+)\s+>", r"<\1>", body, flags=re.I)
    return body.replace("&nbsp;", " ").replace("\r", "")


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"</?[^>]+>", "", s)).strip()


def collapse_ws(s):
    """压掉标签内部的多余空白（含跨行空行），保留单空格分隔。"""
    return re.sub(r"\s*\n\s*", " ", s).strip()


def is_field(name):
    core = name.strip().lstrip("—-–").strip()
    return core in MONSTER_FIELDS or name.strip() in MONSTER_FIELDS


def clean_table(table_inner):
    """把 2列怪物数据表转为字段化段落。"""
    out = []
    for tr in TR_RE.finditer(table_inner):
        tds = TD_RE.findall(tr.group(1))
        if len(tds) < 2:
            # 单列或空行：原样（去噪后文本）保留
            txt = strip_tags(tr.group(1))
            if txt:
                out.append(f"<p>{collapse_ws(txt)}</p>")
            continue
        name_cell, val_cell = tds[0], tds[1]
        name = strip_tags(name_cell).rstrip("：:").strip()
        val = collapse_ws(strip_tags(val_cell))
        if name and is_field(name):
            out.append(f"<p><b>{name}：</b>{val}</p>")
        else:
            # 非白名单字段：原样保留（可能是说明行）
            combined = collapse_ws(strip_tags(name_cell + " " + val_cell))
            if combined:
                out.append(f"<p>{combined}</p>")
    return out


def clean_body(body, filename=None):
    nb = normalize(body)
    chunks = []

    # 文件名 h5 仅置首一次
    title_h5 = make_title_h5(filename) if filename else None

    # 1) 处理所有表格为字段化段落
    table_results = []
    def _replace_table(m):
        table_results.append(clean_table(m.group(1)))
        return "\u0000TABLE\u0000"  # 占位符
    nb = TABLE_RE.sub(_replace_table, nb)

    # 2) 处理表格外的块（标题 / 描述 / 杂项）
    pos = 0
    pending_tables = iter(table_results)
    for m in re.finditer(r"\u0000TABLE\u0000", nb):
        # 表格前的非表格文本块
        pre = nb[pos:m.start()]
        chunks.extend(clean_non_table(pre))
        chunks.extend(next(pending_tables))
        pos = m.end()
    if pos < len(nb):
        chunks.extend(clean_non_table(nb[pos:]))
    if title_h5:
        chunks.insert(0, title_h5)

    return "\n".join(c for c in chunks if c and c.strip())


def make_title_h5(filename):
    """从文件名生成 h5 标题（文件名形如 ENGLISH 中文.tid 或 中文(English).tid）。"""
    base = filename[:-4] if filename.lower().endswith(".tid") else filename
    fm = re.match(r"^([A-Za-z][\w\s'\-,\./]*?)\s+([\u4e00-\u9fff·]+.*)$", base)
    if fm:
        h = f"<h5>{fm.group(2)}({fm.group(1).strip()})</h5>"
    else:
        fc = re.match(r"^([\u4e00-\u9fff·]+)[（(]([^）)]*)[）)]", base)
        if fc:
            h = f"<h5>{fc.group(1)}({fc.group(2)})</h5>"
        else:
            h = f"<h5>{base}</h5>"
    # 全角括号统一转半角（遵守 tid 内禁全角（）规则）
    return h.replace("（", "(").replace("）", ")")


def clean_non_table(seg):
    """处理非表格区域：描述段落、杂项。标题统一由 clean_body 从文件名生成。

    切分规则：按 <p 或 <table 边界切块；含 p 标签的取 inner，裸文本段（如
    <b>战斗：</b>... 无 <p> 包裹）整段处理。避免漏掉未闭合/裸文本段落。
    """
    out = []
    # 按 <p 或 <table 切分（保留分隔符位置，用 lookahead 切）
    parts = re.split(r"(?=<p[^>]*>)|(?=<table[^>]*>)", seg)
    for part in parts:
        if not part.strip():
            continue
        pm = re.match(r"^<p[^>]*>(.*)$", part, re.S | re.I)
        inner = pm.group(1) if pm else part
        plain = strip_tags(inner)
        if not plain:
            continue
        # 正文里的标题格式块（文件名 h5 的重复）直接跳过
        if TITLE_RE.match(plain):
            continue
        # 描述段落：含斜体或纯文本长句 -> 原样保留（去噪后是干净 HTML）
        # 含 img 的块保留原标签（normalize 已清 style/class/lang），不 strip
        tags = set(t.lower() for t in re.findall(r"</?([a-zA-Z0-9]+)", inner))
        if tags <= SAFE_TAGS or (tags - SAFE_TAGS <= {"img"}):
            out.append(f"<p>{collapse_ws(inner)}</p>")
        else:
            out.append(f"<p>{collapse_ws(plain)}</p>")
    return out


KEY_FIELDS = ["生命值", "生命骰", "防御等级", "先攻", "速度", "挑战等级", "属性值", "技能", "专长", "特性"]


def process(rel_dir, apply=False):
    d = os.path.join(MM3, rel_dir)
    # 递归遍历该目录下的所有 .tid（含子目录如 吸血鬼/、嘲弄虫/ 等），跳过 .files 资源目录
    files = []
    for root, dirs, fs in os.walk(d):
        dirs[:] = [x for x in dirs if not x.endswith(".files")]
        for x in sorted(fs):
            if x.lower().endswith(".tid"):
                files.append(os.path.join(root, x))
    stats = {"h5": 0, "field": 0, "p": 0, "files": 0, "tb": 0, "ta": 0}
    stats.update({k: 0 for k in KEY_FIELDS})
    lost = []
    samples = []
    for path in files:
        f = os.path.basename(path)
        raw = open(path, encoding="utf-8").read()
        lines = raw.split("\n")
        header, body = "\n".join(lines[:5]), "\n".join(lines[5:])
        new_body = clean_body(body, f)
        for kf in KEY_FIELDS:
            stats["field"] += len(re.findall(rf"<p><b>{re.escape(kf)}：</b>", new_body))
        stats["h5"] += new_body.count("<h5>")
        stats["p"] += len(re.findall(r"<p>", new_body))
        stats["files"] += 1
        tb = re.sub(r"\s+", "", strip_tags(normalize(body)))
        ta = re.sub(r"\s+", "", strip_tags(new_body))
        stats["tb"] += len(tb)
        stats["ta"] += len(ta)
        if abs(len(ta) - len(tb)) > max(30, len(tb) * 0.01):
            lost.append((os.path.relpath(path, d), len(tb), len(ta)))
        if apply:
            # header 中 source 行的全角（）转半角，与 title 保持一致
            new_header = header.replace("（", "(").replace("）", ")")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new_header + new_body + "\n")
    return stats, samples, lost


def main():
    apply = "--apply" in sys.argv
    if apply:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = os.path.join(P.WORK, f"backup_mm5_clean_{ts}")
        os.makedirs(bak, exist_ok=True)
        for d in TARGET_DIRS:
            src = os.path.join(MM3, d)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(bak, d), dirs_exist_ok=True)
        print(f"[备份] -> {bak}\n")

    for d in TARGET_DIRS:
        stats, samples, lost = process(d, apply=apply)
        print(f"=== {d} === 文件 {stats['files']}  h5 {stats['h5']}  字段 {stats['field']}  <p> {stats['p']}"
              + "  " + " ".join(f"{k}{stats[k]}" for k in KEY_FIELDS if stats[k]))
        print(f"  可见字符 {stats['tb']} -> {stats['ta']}")
        if lost:
            print(f"  [!! 字符数异常 {len(lost)}] " + "; ".join(
                f"{f} {b}->{a}" for f, b, a in lost[:8]))
        if not apply:
            for name, bl, al, txt in samples:
                print(f"\n----- 样本 {d}\\{name}  ({bl} -> {al} 字符) -----")
                print(txt)
        print()

    if not apply:
        print("（干跑，未写入。加 --apply 执行并自动备份）")


if __name__ == "__main__":
    main()
