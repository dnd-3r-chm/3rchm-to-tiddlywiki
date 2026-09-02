#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""搬运 XPH 扩展灵能手册。

为什么需要本脚本：
    PowerShell 传中文路径作为命令行参数会乱码（contexts.md 已记录），
    因此把目录前缀写成常量，而不是 `python convert_book.py "1 核心补充书籍\\XPH..."`。

用法：
    python transport/work/run_xph.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import convert_book

PREFIX = "1 核心补充书籍\\XPH扩展灵能手册"


def main():
    mapping = convert_book.load_final_mapping()
    selected = [
        row for row in mapping.values()
        if row["源文件相对路径"].startswith(PREFIX + "\\")
    ]
    print(f"待转换页数: {len(selected)}")
    ok = convert_book.convert_book(PREFIX)
    print(f"完成: {ok}/{len(selected)}")


if __name__ == "__main__":
    main()
