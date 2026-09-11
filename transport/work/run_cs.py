# -*- coding: utf-8 -*-
"""搬运 3 完美系列/CS完美恶徒（WinCHM 源，convert_book 标准管线 + clean_cs 后处理）。

常量路径规避 PowerShell 中文传参乱码（见 contexts.md 第8节）。

用法：python run_cs.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_book as cb

PREFIX = r"3 完美系列\CS完美恶徒"

if __name__ == "__main__":
    n = cb.convert_book(PREFIX)
    print(f"\n===== 完成，共 {n} 页 =====")
