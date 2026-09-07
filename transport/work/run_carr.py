# -*- coding: utf-8 -*-
"""搬运 3 完美系列/CAr完美奥术（DND3R 在线勘误版源，标准 clean_html 管线）。

常量路径规避 PowerShell 中文传参乱码（见 contexts.md 第8节）。
全书已在 final_mapping.csv 中（61 个源文件），直接调用 convert_book.py 成熟管线。

用法：python run_carr.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_book as cb

PREFIX = r"3 完美系列\CAr完美奥术"

if __name__ == "__main__":
    n = cb.convert_book(PREFIX)
    print(f"\n===== 完成，共 {n} 页 =====")
