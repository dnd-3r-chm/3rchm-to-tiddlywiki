#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""XPH 扩展灵能手册 噪音页结构化重排。

背景：XPH 的 6显能/7装备/8怪物/9附录 共 82 页由 Word 导出，含大量噪音：
  <!--StartFragment-->、非空 <o:p>、断裂的 <span\\n>、未闭合 <font>、海量 &nbsp;

目标格式（对齐 PHB 法术描述 / 武器附魔测评）：
  <h5>中文名(ENGLISH)</h5>
  <p>系别/体型行</p>
  <p><b>字段名：</b>值</p>
  <p>描述段落</p>

安全设计：
  1. <table> 区域整体保留，不做任何改写（防止表格单元格被重排破坏）
  2. 字段识别用白名单，避免把描述句（"寒冷：""第一轮："）误判为字段
  3. 条目标题两遍校验：仅当其后随「系别行」或「字段行」才确认为 h5
  4. 含表格/链接/图片等复杂内联标签的块原样保留

用法：
  python clean_xph.py            # 干跑，只输出统计与样本
  python clean_xph.py --apply     # 实际写入（先自动备份）
"""
import _paths as P
import datetime
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")

PREFIX = "1 核心补充书籍\\XPH扩展灵能手册"
XPH = os.path.join(P.WIKI_TIDDLERS, PREFIX)

TARGET_DIRS = ["6显能", "7装备", "8怪物", "9附录"]

# ---------------------------------------------------------------- 字段白名单
COMMON_FIELDS = {
    "等级", "持续时间", "距离", "目标", "豁免检定", "区域", "效果", "豁免",
}
DIR_FIELDS = {
    "6显能": {
        "灵能点", "显能时间", "异象", "异能抗力", "增幅", "经验值消耗",
        "目标或区域", "单一目标", "区域效果",
        "目标、效果和影响区域", "目标、效果或影响区域", "目标、效果或区域",
        "目标、效果和区域", "灵光强度", "残留灵光",
        "目标性解除", "区域性解除", "减弱", "伪装", "移除胁迫", "物质重塑",
    },
    "8怪物": {
        "生命值", "生命骰", "先攻权", "先攻", "速度", "防御等级", "攻击",
        "全回合攻击", "面宽/触及", "基础攻击/擒抱", "基本攻击/擒抱",
        "特殊攻击", "特性", "技能", "专长", "环境", "组织", "挑战等级",
        "挑战级数", "宝藏", "阵营", "进化", "等级调整", "类灵能能力",
        "属性值", "属性", "心灵异能", "盲视(Ex)", "构装体特性",
        "异能抗力(Ex)", "虚体特性", "天赋职业", "自动语言", "天生灵能",
        "天生异能", "特性(见上文)", "特殊攻击(见上文)",
    },
    "9附录": {
        "法术成分", "施法时间", "法术抗力", "施法材料", "神职", "领域",
        "牧师训练", "任务", "祷文", "庙宇", "仪式", "神使和盟友",
        "神授能力", "神明",
    },
    "7装备": {
        "物理描述", "启动", "随机产生", "特殊性质", "特别提示", "交易价格",
        "所需物品制造专长", "描述", "使用", "技能", "属性", "精神噪音",
        "显能 Manifester",
    },
}

# ---------------------------------------------------------------- 正则
TITLE_RE = re.compile(r"^[\u4e00-\u9fff\w·\-\s]{1,24}[（(]\s*[A-Za-z][^）)]*[）)]")
# 系别行：中文 + 系 + 可选括号/方括号/【】后缀（如 预言系【影响心灵】、咒法系(创造)[强酸]）
DISC_RE = re.compile(
    r"^[\u4e00-\u9fff]{2,10}系"
    r"(?:（[^）]*）|\([^)]*\)|\[[^\]]*\]|【[^】]*】)*$"
)

# 8怪物 数据块常见字段粘连（源 HTML 缺段落分隔），需在值内二次拆分
_SPLIT_FIELDS = [
    "基础攻击/擒抱", "基本攻击/擒抱", "全回合攻击", "面宽/触及", "特殊攻击",
    "生命值", "生命骰", "先攻权", "先攻", "防御等级", "挑战等级", "挑战级数",
    "等级调整", "类灵能能力", "属性值", "属性", "技能", "专长", "特性",
    "环境", "组织", "宝藏", "阵营", "进化", "速度", "攻击", "豁免检定",
    "豁免", "心灵异能",
]
_SPLIT_RE = re.compile(
    r"\s(" + "|".join(re.escape(f) for f in sorted(_SPLIT_FIELDS, key=len, reverse=True)) + r")："
)
FIELD_SPLIT = re.compile(r"^([^：:]{1,28})[：:](.*)$", re.S)
# 「中文 English」-> h5 中文(English)；英文部分允许逗号/句点/连字符（如 Githyanki, Psionic）
LEAD_EN_RE = re.compile(r"^([\u4e00-\u9fff·\w]+)\s+([A-Za-z][\w\s'\-,\./]*)$")
TABLE_RE = re.compile(r"<table[^>]*>.*?</table>", re.S | re.I)
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.S)
SAFE_TAGS = {"b", "i", "u", "em", "strong"}


def normalize(body):
    """机械去噪：注释、o:p、span、font、&nbsp;。"""
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r"</?o:p[^>]*>", "", body, flags=re.I)
    body = re.sub(r"</?span[^>]*>", "", body, flags=re.I)
    body = re.sub(r"</?font[^>]*>", "", body, flags=re.I)
    return body.replace("&nbsp;", " ")


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"</?[^>]+>", "", s)).strip()


def split_tables(body):
    parts, pos = [], 0
    for m in TABLE_RE.finditer(body):
        if m.start() > pos:
            parts.append((False, body[pos:m.start()]))
        parts.append((True, m.group(0)))
        pos = m.end()
    if pos < len(body):
        parts.append((False, body[pos:]))
    return parts


def is_field(prefix, dirname):
    p = prefix.strip()
    core = p.lstrip("—-–").strip()
    allowed = DIR_FIELDS.get(dirname, set()) | COMMON_FIELDS
    return core in allowed or p in allowed


def classify(inner, dirname):
    """返回 (kind, payload, confirmed)。

    confirmed=True 的 h5 为「整块加粗的章节/条目名」（如 <p><b>牧师法术</b></p>），
    属结构性标题，无需后续二次校验；TITLE_RE 命中的 h5 仍需二次校验以防误判。
    """
    plain = strip_tags(inner)
    if not plain:
        return ("drop", None, False)
    # 整块加粗且短、无句读 -> 章节标题
    if (re.fullmatch(r"\s*<b>([^<]*)</b>\s*", inner, re.S)
            and len(plain) <= 30 and "。" not in plain and "：" not in plain):
        m2 = LEAD_EN_RE.match(plain)
        if m2:
            return ("h5", f"{m2.group(1)}({m2.group(2)})", True)
        return ("h5", plain, True)
    if TITLE_RE.match(plain) and len(plain) <= 60 and "。" not in plain:
        return ("h5", plain, False)
    if DISC_RE.match(plain):
        return ("disc", plain, False)
    m = FIELD_SPLIT.match(plain)
    if m and is_field(m.group(1), dirname):
        tags = set(t.lower() for t in re.findall(r"</?([a-zA-Z0-9]+)", inner))
        if tags <= SAFE_TAGS:
            return ("field", (m.group(1).strip(), m.group(2).strip()), False)
    return ("keep", inner, False)


def split_merged_fields(name, val, dirname):
    """拆分值中被粘连的后续字段（仅 8怪物：源 HTML 缺段落分隔）。

    例：属性值：...魅力 11 专长：警戒，武器娴熟
        -> <p><b>属性值：</b>...</p> + <p><b>专长：</b>警戒，武器娴熟</p>
    """
    if dirname != "8怪物":
        return [f"<p><b>{name}：</b>{val}</p>"]
    out, cur_n, cur_v = [], name, val
    while True:
        m = _SPLIT_RE.search(cur_v)
        if not m:
            out.append(f"<p><b>{cur_n}：</b>{cur_v}</p>")
            break
        head, nxt, rest = cur_v[:m.start()].strip(), m.group(1), cur_v[m.end():].strip()
        if head:
            out.append(f"<p><b>{cur_n}：</b>{head}</p>")
        cur_n, cur_v = nxt, rest
    return out


def clean_body(body, dirname):
    nb = normalize(body)
    items = []  # (kind, payload)，kind ∈ {table, raw, p}
    for is_table, seg in split_tables(nb):
        if is_table:
            items.append(("table", seg.strip()))
            continue
        pos = 0
        for m in P_RE.finditer(seg):
            if m.start() > pos:
                items.append(("raw", seg[pos:m.start()]))
            items.append(("p", m.group(1)))
            pos = m.end()
        if pos < len(seg):
            items.append(("raw", seg[pos:]))

    # 第一遍分类。(kind, payload, confirmed)
    # confirmed=True 的 h5 来自 <p> 外的结构块（标题/章节名），不做二次校验。
    kinds = []
    for kind, payload in items:
        if kind == "table":
            kinds.append(("keep", payload, True))
            continue
        plain = strip_tags(payload)
        if kind == "raw":
            if not plain:
                kinds.append(("drop", None, False))
                continue
            # 首尾 <br> 是 Word 噪音，剥离后再判定（否则整块加粗匹配失败）
            core = re.sub(r"^\s*(?:<br\s*/?>\s*)*", "", payload)
            core = re.sub(r"\s*(?:<br\s*/?>\s*)*$", "", core)
            m = LEAD_EN_RE.match(plain)
            if m:  # 「中文 English」-> h5 中文(English)
                kinds.append(("h5", f"{m.group(1)}({m.group(2)})", True))
                continue
            if TITLE_RE.match(plain) and len(plain) <= 60:
                kinds.append(("h5", plain, True))
                continue
            mb = re.fullmatch(r"\s*<b>([^<]*)</b>\s*", core, re.S)
            if mb and len(plain) <= 30:  # 整块加粗且短 -> 章节标题
                kinds.append(("h5", plain, True))
                continue
            kinds.append(("keep", core.strip() if core.strip() else payload.strip(), False))
        else:
            kinds.append(classify(payload, dirname))

    out = list(kinds)

    # 8怪物：首个非空块若为整块加粗，确认为怪物名（名字可能超过 30 字）
    if dirname == "8怪物":
        for i, (k, _v, _c) in enumerate(out):
            if k == "drop":
                continue
            if (items[i][0] in ("p", "raw")
                    and re.fullmatch(r"\s*<b>([^<]*)</b>\s*", items[i][1], re.S)):
                txt = strip_tags(items[i][1])
                m2 = LEAD_EN_RE.match(txt)
                out[i] = ("h5", f"{m2.group(1)}({m2.group(2)})" if m2 else txt, True)
            break

    # 第二遍：仅校验 <p> 内的 h5（须后随 disc/field，否则降级为段落）

    for i, (k, _v, conf) in enumerate(kinds):
        if k != "h5" or conf:
            continue
        nxt = None
        for j in range(i + 1, len(kinds)):
            if kinds[j][0] != "drop":
                nxt = kinds[j][0]
                break
        if nxt not in ("disc", "field", "h5"):
            src = items[i][1]
            out[i] = ("keep", strip_tags(src) if items[i][0] == "p" else src, True)

    # 渲染
    chunks = []
    for k, v, _c in out:
        if k == "drop":
            continue
        if k == "h5":
            chunks.append(f"<h5>{v}</h5>")
        elif k == "disc":
            chunks.append(f"<p>{v}</p>")
        elif k == "field":
            chunks.extend(split_merged_fields(v[0], v[1], dirname))
        elif k == "keep":
            if "<" not in v:  # 纯文本：折叠源码换行与多余空格
                v = re.sub(r"\s+", " ", v).strip()
                chunks.append(f"<p>{v}</p>" if v else "")
            else:
                chunks.append(v)
    return "\n\n".join(c for c in chunks if c and c.strip())


KEY_FIELDS = ["属性值", "专长", "技能", "特性", "生命值", "防御等级", "豁免检定"]


def process(rel_dir, apply=False):
    d = os.path.join(XPH, rel_dir)
    files = sorted(f for f in os.listdir(d) if f.lower().endswith(".tid"))
    stats = {"h5": 0, "field": 0, "disc": 0, "keep": 0, "drop": 0, "files": 0}
    stats.update({k: 0 for k in KEY_FIELDS})
    stats["tb"] = stats["ta"] = 0
    noh5, lost = [], []
    samples = []
    for f in files:
        path = os.path.join(d, f)
        raw = open(path, encoding="utf-8").read()
        lines = raw.split("\n")
        header, body = "\n".join(lines[:5]), "\n".join(lines[5:])
        new_body = clean_body(body, rel_dir)
        before_len = len(body)
        after_len = len(new_body)
        for kf in KEY_FIELDS:
            stats[kf] += len(re.findall(rf"<p><b>{re.escape(kf)}：</b>", new_body))
        nh5 = new_body.count("<h5>")
        stats["h5"] += nh5
        stats["field"] += len(re.findall(r"<p><b>[^<]+：</b>", new_body))
        stats["keep"] += len(re.findall(r"<p>", new_body))
        stats["files"] += 1
        if nh5 == 0:
            noh5.append(f)
        # 内容丢失自检：基线同样过 normalize（否则字面量 &nbsp; 被误计为内容）
        tb = re.sub(r"\s+", "", strip_tags(normalize(body)))
        ta = re.sub(r"\s+", "", strip_tags(new_body))
        stats["tb"] += len(tb)
        stats["ta"] += len(ta)
        if abs(len(ta) - len(tb)) > max(20, len(tb) * 0.005):
            lost.append((f, len(tb), len(ta)))
        if f in ("A.tid", "溶晶怪.tid", "灵物.tid", "法术.tid", "E.tid"):
            samples.append((f, before_len, after_len, new_body[:1400]))
        if apply:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(header + new_body + "\n")
    return stats, samples, noh5, lost


def main():
    apply = "--apply" in sys.argv
    if apply:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = os.path.join(P.WORK, f"backup_xph_clean_{ts}")
        os.makedirs(bak, exist_ok=True)
        for d in TARGET_DIRS:
            src = os.path.join(XPH, d)
            shutil.copytree(src, os.path.join(bak, d))
        print(f"[备份] -> {bak}\n")

    for d in TARGET_DIRS:
        stats, samples, noh5, lost = process(d, apply=apply)
        print(f"=== {d} === 文件 {stats['files']}  h5 {stats['h5']}  字段 {stats['field']}  <p> {stats['keep']}"
              + "  " + " ".join(f"{k}{stats[k]}" for k in KEY_FIELDS if stats[k]))
        if noh5:
            print(f"  [无标题 {len(noh5)}] {', '.join(noh5[:14])}")
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
