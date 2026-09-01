#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复已有 .tid 文件中标题标签闭合不匹配的问题。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_pilot as cp

ROOT = r"E:\dnd3r_full\transport\wiki\tiddlers"


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("\n\n", 1)
    if len(parts) != 2:
        return False
    header, body = parts
    new_body = cp.fix_heading_closing_tags(body)
    if new_body != body:
        with open(path, "w", encoding="utf-8") as f:
            f.write(header + "\n\n" + new_body)
        print("FIXED:", os.path.relpath(path, ROOT))
        return True
    return False


def main():
    count = 0
    for dirpath, _, names in os.walk(ROOT):
        for name in names:
            if name.lower().endswith(".tid"):
                if process_file(os.path.join(dirpath, name)):
                    count += 1
    print("fixed files:", count)


if __name__ == "__main__":
    main()
