#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 final_mapping.csv 的新标签规则（只保留书目分类+书名两级）批量重打 .tid 的 tags。

- 只处理含 source: 字段的内容 Tiddler；系统 Tiddler（$:/...）不动。
- source 在 csv 中未命中时报告并保留原 tags（不静默修改）。
- 幂等：再次运行无变化。
"""
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"E:\dnd3r_full"
WIKI_TIDDLERS = os.path.join(ROOT, "transport", "wiki", "tiddlers")
FINAL_MAPPING = os.path.join(ROOT, "transport", "work", "final_mapping.csv")


def load_new_tags():
    tags_map = {}
    with open(FINAL_MAPPING, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            key = r["源文件相对路径"].replace("\\", "/")
            tags_map[key] = r["标签"]
            tags_map[key.replace("/", "\\")] = r["标签"]
    return tags_map


def split_header(text):
    """把 .tid 拆成字段头部与正文两部分（以第一个空行分隔）。"""
    m = re.split(r"\r?\n\r?\n", text, maxsplit=1)
    if len(m) == 2:
        return m[0], m[1]
    return text, ""


def process_file(path, tags_map):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    header, body = split_header(content)

    sm = re.search(r"^source:\s*(.+)$", header, re.M)
    if not sm:
        return "skip-no-source", None
    source = sm.group(1).strip()

    tm = re.search(r"^tags:.*$", header, re.M)
    if source not in tags_map:
        return "missing-in-csv", source

    new_tags = tags_map[source]
    if tm:
        new_header = header[:tm.start()] + f"tags: {new_tags}" + header[tm.end():]
    else:
        new_header = header + f"\ntags: {new_tags}"

    new_content = new_header + "\n\n" + body
    if new_content == content:
        return "unchanged", source
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return "updated", (source, new_tags)


def main():
    tags_map = load_new_tags()
    stats = {"updated": 0, "unchanged": 0, "skip-no-source": 0, "missing-in-csv": 0}
    for dirpath, _, names in os.walk(WIKI_TIDDLERS):
        for name in names:
            if not name.lower().endswith(".tid"):
                continue
            path = os.path.join(dirpath, name)
            status, info = process_file(path, tags_map)
            stats[status] += 1
            if status == "updated":
                src, new_tags = info
                print(f"[UPD] {os.path.relpath(path, WIKI_TIDDLERS)}")
                print(f"      {src} -> tags: {new_tags}")
            elif status == "missing-in-csv":
                print(f"[WARN] csv 无此 source: {info} ({os.path.relpath(path, WIKI_TIDDLERS)})")
    print("stats:", stats)


if __name__ == "__main__":
    main()
