# -*- coding: utf-8 -*-
"""搬运 PHB2玩家手册2（常量路径规避 PowerShell 中文乱码）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_book as cb

PREFIX = r"1 核心补充书籍\PHB2玩家手册2"
if __name__ == "__main__":
    cb.convert_book(PREFIX)
