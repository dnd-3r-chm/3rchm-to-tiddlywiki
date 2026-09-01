# -*- coding: utf-8 -*-
"""只读扫描全库 .tid 的 class / id / 内联 style 分布，产出 hooks-inventory.csv。

不做任何写入。判断规则与 Phase 2 清理规格对齐：
  - class：全删，白名单 subhead/noindent/noidt 保留
  - id：全删
  - 内联 style：
      * 含 mso- 或 含全大写 CSS 属性名(MARGIN-/LINE-/TEXT-INDENT 等) -> 视为待清(全库)
      * MM怪物图鉴：删全部
      * PHB玩家手册：完全不动
      * 其他书/小写属性：自动免疫
"""
import os
import re
import csv

import _paths as P

WIKI = P.WIKI_TIDDLERS
OUT = os.path.join(P.WORK, "hooks-inventory.csv")

CLASS_RE = re.compile(r'\sclass\s*=\s*("([^"]*)"|\'([^\']*)\'|([^\s>]+))')
ID_RE = re.compile(r'\sid\s*=\s*("([^"]*)"|\'([^\']*)\'|([^\s>]+))')
STYLE_RE = re.compile(r'\sstyle\s*=\s*"([^"]*)"')

WHITELIST_CLASS = {"subhead", "noindent", "noidt"}

# 跳过清单（系统/样式/手工页，不做任何改动）
SKIP_FILES = {
    "CHM目录侧边栏.tid",
    "总目录.tid",
    "标题配色.tid",
    "cascading_stylesheet.css.tid",
}

UPPER_PROP_RE = re.compile(r'(?:^|;)\s*[A-Z][A-Z0-9-]*\s*:')


def is_system(tid_name):
    return tid_name.startswith("$__")


def book_of(rel):
    """返回『书』归属：
    - 0 核心三宝书/MM怪物图鉴/... -> MM怪物图鉴 (取二级目录)
    - 0 核心三宝书/PHB玩家手册/... -> PHB玩家手册
    - 0 核心三宝书/DMG城主指南/... -> DMG城主指南
    - 10 附录/... -> 10 附录
    - 根目录 aaa.tid -> aaa.tid
    """
    parts = rel.split(os.sep)
    if not parts:
        return "(root)"
    if parts[0] == "0 核心三宝书" and len(parts) > 1:
        return parts[1]
    return parts[0]


def main():
    class_counter = {}
    id_counter = {}
    style_total = {}
    style_clearable = {}     # 命中 mso- 或 全大写属性
    style_mm = {}            # MM 书内 style（全部可清）
    style_phb = {}           # PHB 书内 style（全部不动）
    file_count_class = {}
    file_count_id = {}

    for dp, dn, fn in os.walk(WIKI):
        for f in fn:
            if not f.endswith(".tid"):
                continue
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, WIKI)
            if f in SKIP_FILES or is_system(f):
                continue
            book = book_of(rel)
            try:
                text = open(full, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            # 只扫描空行之后的正文（跳过 tiddler 字段区）
            body = text.split("\n", 1)[1] if "\n" in text else ""
            # class
            for m in CLASS_RE.finditer(body):
                val = (m.group(2) or m.group(3) or m.group(4) or "").strip()
                for c in val.split():
                    if c in WHITELIST_CLASS:
                        continue
                    class_counter[c] = class_counter.get(c, 0) + 1
                    file_count_class.setdefault(c, set()).add(rel)
            # id
            for m in ID_RE.finditer(body):
                val = (m.group(2) or m.group(3) or m.group(4) or "").strip()
                if val:
                    id_counter[val] = id_counter.get(val, 0) + 1
                    file_count_id.setdefault(val, set()).add(rel)
            # style
            for m in STYLE_RE.finditer(body):
                sval = m.group(1)
                style_total[book] = style_total.get(book, 0) + 1
                upper = bool(UPPER_PROP_RE.search(sval)) or ("mso-" in sval.lower())
                if book == "MM怪物图鉴":
                    style_mm[book] = style_mm.get(book, 0) + 1
                elif book == "PHB玩家手册":
                    style_phb[book] = style_phb.get(book, 0) + 1
                elif upper:
                    style_clearable[book] = style_clearable.get(book, 0) + 1

    # 输出 CSV
    with open(OUT, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["类型", "值/归属", "出现次数", "涉及文件数", "处置"])
        for c, n in sorted(class_counter.items(), key=lambda x: -x[1]):
            w.writerow(["class", c, n, len(file_count_class.get(c, ())), "移除"])
        for i, n in sorted(id_counter.items(), key=lambda x: -x[1])[:200]:
            w.writerow(["id", i, n, len(file_count_id.get(i, ())), "移除"])
        w.writerow(["style", "MM怪物图鉴(全部)", sum(style_mm.values()), "", "移除"])
        w.writerow(["style", "PHB玩家手册(全部)", sum(style_phb.values()), "", "保留"])
        for b, n in sorted(style_clearable.items(), key=lambda x: -x[1]):
            w.writerow(["style", b + "(mso-/大写属性)", n, "", "移除"])
        for b, n in sorted(style_total.items(), key=lambda x: -x[1]):
            if b not in ("MM怪物图鉴", "PHB玩家手册"):
                w.writerow(["style", b + "(小写属性-免疫)", n, "", "保留"])

    print("扫描完成 ->", OUT)
    print("class 种类数:", len(class_counter), " 总出现:", sum(class_counter.values()))
    print("id 种类数:", len(id_counter), " 总出现:", sum(id_counter.values()))
    print("style 总数:", sum(style_total.values()),
          " | MM:", sum(style_mm.values()),
          " PHB:", sum(style_phb.values()),
          " 可清(其他书):", sum(style_clearable.values()))


if __name__ == "__main__":
    main()
