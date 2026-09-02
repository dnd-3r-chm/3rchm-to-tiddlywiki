# -*- coding: utf-8 -*-
"""搬运 2 万物万法万律（MIC万物大全 / RC万律大全 / SpC万法大全）。

常量路径规避 PowerShell 中文传参乱码（见 contexts.md 第8节）。
三本书均已在 final_mapping.csv 中（MIC 51 行、RC 1 行、SpC 1 行），
可直接调用 convert_book.py 成熟管线搬运。

用法：python run_wanwu.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_book as cb

PREFIXES = [
    r"2 万物万法万律\MIC万物大全",
    r"2 万物万法万律\RC万律大全",
    r"2 万物万法万律\SpC万法大全",
]

if __name__ == "__main__":
    # 支持分批：python run_wanwu.py RC SpC  或  python run_wanwu.py MIC
    keys = sys.argv[1:]
    if keys:
        targets = [p for p in PREFIXES if any(k.lower() in p.lower() for k in keys)]
        if not targets:
            print("未匹配到书目，可用关键字：MIC / RC / SpC")
            sys.exit(1)
    else:
        targets = PREFIXES
    total = 0
    for p in targets:
        print(f"\n########## {p} ##########")
        total += cb.convert_book(p)
    print(f"\n===== 完成，共 {total} 页 =====")
