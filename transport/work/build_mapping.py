#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build final migration mapping with unique Tiddler titles and tags."""
import _paths as P
import collections
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = P.ROOT
HHC_CSV = os.path.join(ROOT, "transport", "work", "hhc_mapping.csv")
OUT_CSV = os.path.join(ROOT, "transport", "work", "final_mapping.csv")


def path_to_tags(rel_path):
    """标签只保留前两级目录：书目分类（一级）+ 书名/模块（二级）。

    例：
       0 核心三宝书\\MM怪物图鉴\\第一章：怪物\\D\\真龙\\红龙.htm
           -> ["0 核心三宝书", "MM怪物图鉴"]
       10 附录\\html教学\\开始之前.htm
           -> ["10 附录", "html教学"]
       10 附录\版本历史.htm
           -> ["10 附录"]
       前言.htm
           -> []
    """
    parts = rel_path.replace("/", "\\").split("\\")
    dirs = parts[:-1] if len(parts) > 1 else []
    return dirs[:2]


def build_title(base_title, parts):
    """标题新格式（用户规则 2026-08-30）：具体标题 (书目缩写-书名)；无缩写则 具体标题 (所属内容)。

    例：[DMG] 简介 -> 简介 (DMG-城主指南)；10 附录\版本历史 -> 版本历史 (10 附录)。
    根目录文件保持：龙与地下城3版扩展规则大全 - 标题。
    """
    if len(parts) >= 3:
        book_dir = parts[1]
        m = re.match(r"^[A-Za-z0-9]+", book_dir)
        if m:
            abbr = m.group(0)
            book_name = re.sub(r"^[A-Za-z0-9]+", "", book_dir).strip()
            return f"{base_title} ({abbr}-{book_name})"
        return f"{base_title} ({book_dir})"
    if len(parts) == 2:
        owner = parts[0]
        # 用户规则：所属内容为 10 附录时不写序号
        if owner == "10 附录":
            owner = "附录"
        return f"{base_title} ({owner})"
    # 根目录文件：2026-08-30 起不再加「龙与地下城3版扩展规则大全 - 」前缀
    return base_title


def insert_disambig(title, suffix):
    """在「 (书目)」后缀之前插入消歧后缀，保持 标题 (书目) 格式。"""
    m = re.match(r"^(.*?)(\s\([^)]*\))$", title)
    if m:
        return f"{m.group(1)}({suffix}){m.group(2)}"
    return f"{title}({suffix})"


def main():
    rows = []
    seen = set()
    with open(HHC_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if not r["源文件相对路径"]:
                continue
            key = r["源文件相对路径"].replace("/", "\\").lower()
            if key in seen:
                continue
            seen.add(key)
            rows.append(r)

    out_rows = []
    for r in rows:
        rel = r["源文件相对路径"].replace("/", "\\")
        title = r["标题"]
        # 去掉标题中已有的 [缩写] 前缀，避免重复
        base_title = re.sub(r"^\[[^\]]+\]\s*", "", title).strip()
        parts = rel.split("\\")
        unique_title = build_title(base_title, parts)

        tags = path_to_tags(rel)
        out_rows.append({
            "源文件相对路径": rel,
            "HHC标题": title,
            "Tiddler标题": unique_title,
            "层级": r["层级"],
            "祖先路径": r["祖先路径"],
            "一级": r["一级"],
            "二级": r["二级"],
            "标签": " ".join(f"[[{t}]]" for t in tags),
            "所在目录": "\\".join(rel.split("\\")[:-1]) if "\\" in rel else "",
        })

    # 二次消歧：重名时在标题部分追加文件名（保持「标题 (书目)」格式）
    title_used = collections.Counter(r["Tiddler标题"] for r in out_rows)
    for r in out_rows:
        if title_used[r["Tiddler标题"]] > 1:
            stem = os.path.splitext(os.path.basename(r["源文件相对路径"]))[0]
            r["Tiddler标题"] = insert_disambig(r["Tiddler标题"], stem)

    title_used2 = collections.Counter(r["Tiddler标题"] for r in out_rows)
    for r in out_rows:
        if title_used2[r["Tiddler标题"]] > 1:
            r["Tiddler标题"] = insert_disambig(r["Tiddler标题"], r["源文件相对路径"])

    # 全角引号/括号 -> 半角（用户规则，与转换管道/已转换内容一致，2026-09）
    _trans = str.maketrans({"\u201c": '"', "\u201d": '"', "\uff08": "(", "\uff09": ")"})
    for r in out_rows:
        r["HHC标题"] = r["HHC标题"].translate(_trans)
        r["Tiddler标题"] = r["Tiddler标题"].translate(_trans)
        r["祖先路径"] = r["祖先路径"].translate(_trans)
        r["一级"] = r["一级"].translate(_trans)
        r["二级"] = r["二级"].translate(_trans)

    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "源文件相对路径", "HHC标题", "Tiddler标题", "层级",
            "祖先路径", "一级", "二级", "标签", "所在目录",
        ])
        writer.writeheader()
        writer.writerows(out_rows)

    print("rows:", len(out_rows))
    print("unique tiddler titles:", len(set(r["Tiddler标题"] for r in out_rows)))
    print("output:", OUT_CSV)


if __name__ == "__main__":
    main()
