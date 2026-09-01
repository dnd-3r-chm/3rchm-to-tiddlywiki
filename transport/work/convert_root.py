#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""转换根目录下的 HTML 文件（如前言、使用说明、译者名录）。"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_pilot as cp

ROOT = cp.ROOT
WIKI_TIDDLERS = cp.WIKI_TIDDLERS
FINAL_MAPPING = os.path.join(ROOT, "transport", "work", "final_mapping.csv")

import apply_root_inline_styles as aris


def main():
    with open(FINAL_MAPPING, encoding="utf-8-sig") as f:
        all_rows = list(csv.DictReader(f))
    mapping = {r["源文件相对路径"]: r for r in all_rows}
    rows = [r for r in all_rows if "\\" not in r["源文件相对路径"]]

    print("root pages:", len(rows))
    for row in rows:
        rel = row["源文件相对路径"]
        src_path = os.path.join(ROOT, rel)
        text = cp.read_text(src_path)
        body = cp.extract_body(text)
        body = cp.clean_html(body)
        body = cp.rewrite_images(body, "")
        body = cp.rewrite_links(body, mapping, "")
        body = aris.process_body(body)

        title = row["Tiddler标题"]
        tags = row["标签"]
        source = rel.replace("\\", "/")
        tid = f"""title: {title}
tags: {tags}
source: {source}
type: text/vnd.tiddlywiki

{body}
"""
        if rel == "译者名录1.1.htm":
            out_name = "译者名录.tid"
        else:
            out_name = os.path.splitext(rel)[0] + ".tid"
        out_path = os.path.join(WIKI_TIDDLERS, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(tid)
        print(f"[OK] {title} -> {out_path}")


if __name__ == "__main__":
    main()
