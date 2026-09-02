# -*- coding: utf-8 -*-
"""搬运 MM4怪物图鉴4（常量路径规避 PowerShell 中文乱码）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_book as cb

PREFIX = r"1 核心补充书籍\MM4怪物图鉴4"
if __name__ == "__main__":
    cb.convert_book(PREFIX)
