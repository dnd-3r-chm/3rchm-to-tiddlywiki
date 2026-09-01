#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给根目录节点追加指定的排版 style。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT_STYLE = """<style>
table{width: 100%;border-color: transparent;}/*表格边框透明*/
td{width: 16.67%; border-color: transparent;}/*单元格宽度，单元格边框透明*/
h1{color:DarkSlateGray}
h2{color:DarkSlateGray}
h3{color:teal}
h4{color:teal}
h5{color:teal}
h6{color:teal}
</style>
"""

FILES = [
    r"E:\dnd3r_full\transport\wiki\tiddlers\前言.tid",
    r"E:\dnd3r_full\transport\wiki\tiddlers\如何使用大不全.tid",
    r"E:\dnd3r_full\transport\wiki\tiddlers\译者名录.tid",
]


def main():
    for path in FILES:
        if not os.path.exists(path):
            print("MISSING:", path)
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if "<style>" in content:
            print("ALREADY HAS STYLE:", path)
            continue
        parts = content.split("\n\n", 1)
        if len(parts) != 2:
            print("SKIP:", path)
            continue
        header, body = parts
        new_content = header + "\n\n" + ROOT_STYLE + "\n" + body
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("ADDED STYLE:", path)


if __name__ == "__main__":
    main()
