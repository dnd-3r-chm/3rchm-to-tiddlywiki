# -*- coding: utf-8 -*-
"""搬运 8 战役引钩 下 3 本书（convert_book 标准管线）。

书：WoL传古武器 / EoE邪恶典范 / EE上古邪物。
EoE 下两个 WinCHM 空模板页（新建项目.htm）已在 convert_book.SKIP_SOURCES 排除。

用法：python run_8books.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_book as cb

BOOKS = [
    r"8 战役引钩\WoL传古武器",
    r"8 战役引钩\EoE邪恶典范",
    r"8 战役引钩\EE上古邪物",
]

if __name__ == "__main__":
    for b in BOOKS:
        n = cb.convert_book(b)
        print(f"\n===== {b} 完成，共 {n} 页 =====\n")
