# -*- coding: utf-8 -*-
"""搬运 MM5怪物图鉴5（常量路径规避 PowerShell 中文乱码）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_book as cb

PREFIX = r"1 核心补充书籍\MM5怪物图鉴5"
if __name__ == "__main__":
    cb.convert_book(PREFIX)
