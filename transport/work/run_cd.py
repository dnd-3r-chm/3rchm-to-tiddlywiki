# -*- coding: utf-8 -*-
"""搬运 3 完美系列/CD完美神力（WinCHM 源，convert_book 标准管线 + clean_cd 后处理）。

常量路径规避 PowerShell 中文传参乱码（见 contexts.md 第8节）。
全书将在 final_mapping.csv 中加入（add_cd_mapping.py）后，调用 convert_book.py 成熟管线。

用法：python run_cd.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_book as cb

PREFIX = r"3 完美系列\CD完美神力"

if __name__ == "__main__":
    n = cb.convert_book(PREFIX)
    print(f"\n===== 完成，共 {n} 页 =====")
