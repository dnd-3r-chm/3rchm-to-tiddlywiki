#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为 3 完美系列/CC完美斗士 追加 final_mapping 行。

背景：CC 是 WinCHM + DND3R 在线勘误注入源，不在 Contents.hhc / hhc_mapping.csv 中，
因此 final_mapping.csv 也没有它。不能直接重跑 build_mapping.py（会覆盖
现有已搬书：CAd/CAr/MM/XPH 等），故仅把 CC 源目录下所有 .htm/.html 生成映射行
追加到 final_mapping.csv，并做跨书/书内消歧。

Tiddler标题 = build_title(文件名去扩展名, 路径分段) -> "X (CC-完美斗士)"
标签       = [[3 完美系列]] [[CC完美斗士]]
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P
import build_mapping as bm

CC_REL = r"3 完美系列\CC完美斗士"
SRC_DIR = os.path.join(P.ROOT, CC_REL)
OUT_CSV = bm.OUT_CSV
FIELDS = ["源文件相对路径", "HHC标题", "Tiddler标题", "层级",
          "祖先路径", "一级", "二级", "标签", "所在目录"]


def main():
    rels = []
    for root, dirs, fs in os.walk(SRC_DIR):
        for x in sorted(fs):
            if x.lower().endswith((".htm", ".html")):
                full = os.path.join(root, x)
                rel = os.path.relpath(full, P.ROOT).replace("/", "\\")
                rels.append(rel)
    rels.sort()
    print(f"源文件: {len(rels)}")

    new_rows = []
    for rel in rels:
        parts = rel.split("\\")
        base = os.path.splitext(parts[-1])[0]
        title = bm.build_title(base, parts)
        tags = bm.path_to_tags(rel)
        ancestors = " / ".join(parts[:-1])
        new_rows.append({
            "源文件相对路径": rel,
            "HHC标题": f"[CC] {base}",
            "Tiddler标题": title,
            "层级": str(len(parts)),
            "祖先路径": ancestors,
            "一级": parts[0],
            "二级": parts[1] if len(parts) > 1 else "",
            "标签": " ".join(f"[[{t}]]" for t in tags),
            "所在目录": "\\".join(parts[:-1]),
        })

    # 现有映射（用于跨书消歧 + 跳过重复 rel）
    existing = {}
    with open(OUT_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            existing[r["源文件相对路径"]] = r

    used = {r["Tiddler标题"] for r in existing.values()}
    titles_seen = set()
    for row in new_rows:
        t = row["Tiddler标题"]
        if t in titles_seen or t in used:
            stem = os.path.splitext(os.path.basename(row["源文件相对路径"]))[0]
            nt = bm.insert_disambig(t, stem)
            while nt in used or nt in titles_seen:
                nt = bm.insert_disambig(nt, row["源文件相对路径"])
            row["Tiddler标题"] = nt
        titles_seen.add(row["Tiddler标题"])
        used.add(row["Tiddler标题"])

    existing_rel = set(existing.keys())
    append_rows = [r for r in new_rows if r["源文件相对路径"] not in existing_rel]
    print(f"新增映射行: {len(append_rows)}（已存在跳过: {len(new_rows) - len(append_rows)}）")
    if not append_rows:
        print("无需追加。")
        return

    with open(OUT_CSV, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writerows(append_rows)
    print(f"已追加到 {OUT_CSV}")


if __name__ == "__main__":
    main()
