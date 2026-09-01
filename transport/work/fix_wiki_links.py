#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复转换时生成的 TiddlyWiki 链接参数写反问题。

TiddlyWiki 语法：[[显示文字|目标Tiddler]]
早期脚本误生成为：[[目标Tiddler|显示文字]]
本脚本根据 final_mapping 中的已知标题自动纠正。
"""
import _paths as P
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = P.WIKI_TIDDLERS
FINAL_MAPPING = os.path.join(P.WORK, "final_mapping.csv")


def load_known_titles():
    known = set()
    with open(FINAL_MAPPING, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            known.add(r["Tiddler标题"])
    return known


def fix_content(content, known):
    def repl(m):
        a = m.group(1).strip()
        b = m.group(2).strip()
        a_key = a.split("#", 1)[0].strip()
        b_key = b.split("#", 1)[0].strip()
        # 如果 a 是已知标题而 b 不是，说明参数写反了
        if a_key in known and b_key not in known:
            return f"[[{b}|{a}]]"
        return m.group(0)

    return re.sub(r"\[\[([^\]|]+)\|([^\]|]+)\]\]", repl, content)


def main():
    known = load_known_titles()
    print("known titles:", len(known))
    changed = 0
    for dirpath, _, names in os.walk(ROOT):
        for name in names:
            if not name.lower().endswith(".tid"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = fix_content(content, known)
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print("FIXED:", os.path.relpath(path, ROOT))
                changed += 1
    print("changed files:", changed)


if __name__ == "__main__":
    main()
