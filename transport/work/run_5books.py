# -*- coding: utf-8 -*-
"""搬运 5 环境和社会 下 5 本书（convert_book 标准管线）。

用法：python run_5books.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_book as cb

BOOKS = [
    r"5 环境和社会\City城市风貌",
    r"5 环境和社会\Dungeon地城风光",
    r"5 环境和社会\Frost霜燃之书",
    r"5 环境和社会\Sand沙暴之书",
    r"5 环境和社会\Storm风暴之书",
]

if __name__ == "__main__":
    for b in BOOKS:
        n = cb.convert_book(b)
        print(f"\n===== {b} 完成，共 {n} 页 =====\n")
