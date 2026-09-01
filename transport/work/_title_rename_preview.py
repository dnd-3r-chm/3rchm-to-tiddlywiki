# -*- coding: utf-8 -*-
"""DRY-RUN：计算标题新格式 具体标题 (缩写-书名) / 具体标题 (所属内容)，预览变化。
不写任何文件。
"""
import collections
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

FINAL_MAPPING = r"E:\dnd3r_full\transport\work\final_mapping.csv"


def calc_new(row):
    rel = row["源文件相对路径"].replace("/", "\\")
    title = row["HHC标题"]
    base = re.sub(r"^\[[^\]]+\]\s*", "", title).strip()
    parts = rel.split("\\")
    if len(parts) >= 3:
        book_dir = parts[1]
        m = re.match(r"^[A-Za-z0-9]+", book_dir)
        if m:
            abbr = m.group(0)
            book_name = re.sub(r"^[A-Za-z0-9]+", "", book_dir).strip()
            return f"{base} ({abbr}-{book_name})", "abbr"
        return f"{base} ({book_dir})", "no-abbr"
    if len(parts) == 2:
        return f"{base} ({parts[0]})", "top-level"
    return f"龙与地下城3版扩展规则大全 - {base}", "root"


def main():
    with open(FINAL_MAPPING, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    pairs = []
    by_kind = collections.Counter()
    changed = 0
    for r in rows:
        old = r["Tiddler标题"]
        new, kind = calc_new(r)
        by_kind[kind] += 1
        if new != old:
            changed += 1
        pairs.append((r["源文件相对路径"], old, new, kind))
    print(f"rows: {len(rows)}, changed: {changed}, kinds: {dict(by_kind)}")

    # 冲突检测
    cnt = collections.Counter(p for _, _, p, _ in pairs)
    dups = {t: c for t, c in cnt.items() if c > 1}
    print(f"duplicate new titles: {len(dups)}")
    for t, c in list(dups.items())[:10]:
        print(f"  x{c}: {t}")

    # 样例：每类各 4 个
    shown = collections.Counter()
    for src, old, new, kind in pairs:
        if shown[kind] < 4:
            shown[kind] += 1
            print(f"[{kind}] {old}  =>  {new}   ({src})")


if __name__ == "__main__":
    main()
