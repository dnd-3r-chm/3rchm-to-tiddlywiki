# -*- coding: utf-8 -*-
"""搬运 4 阵营和位面 下 4 本书（convert_book 标准管线）。

用法：python run_4books.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_book as cb

BOOKS = [
    r"4 阵营和位面\BoED崇善之书",
    r"4 阵营和位面\FC1深渊堕群",
    r"4 阵营和位面\FC2九狱君王",
    r"4 阵营和位面\PlH位面手册",
]

if __name__ == "__main__":
    for b in BOOKS:
        n = cb.convert_book(b)
        print(f"\n===== {b} 完成，共 {n} 页 =====\n")
