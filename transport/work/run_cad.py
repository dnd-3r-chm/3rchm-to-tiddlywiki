# -*- coding: utf-8 -*-
"""搬运 3 完美系列/CAd完美冒险。

常量路径规避 PowerShell 中文传参乱码（见 contexts.md 第8节）。
全书 49 页均已在 final_mapping.csv 中（源目录 49 个 .htm 精确对应：
基础 3 + 封面 1 + 进阶职业 27 + 技能专长 5 + 装备物品 7 + 法术动作 3
+ 组织 1 + 传奇等级 2），可直接调用 convert_book.py 成熟管线搬运。

用法：python run_cad.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_book as cb

PREFIX = r"3 完美系列\CAd完美冒险"

if __name__ == "__main__":
    n = cb.convert_book(PREFIX)
    print(f"\n===== 完成，共 {n} 页 =====")
