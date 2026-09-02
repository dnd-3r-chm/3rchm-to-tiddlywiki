# -*- coding: utf-8 -*-
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fm = os.path.join(ROOT, "transport", "work", "final_mapping.csv")
prefix = "1 核心补充书籍\\MM5怪物图鉴5"
n = 0
with open(fm, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        if row["源文件相对路径"].startswith(prefix + "\\"):
            n += 1
print(f"final_mapping 中 {prefix} 条目数:", n)

# 源目录统计
src = os.path.join(ROOT, "1 核心补充书籍", "MM5怪物图鉴5")
htm = sum(1 for r, d, fs in os.walk(src) for x in fs if x.lower().endswith((".htm", ".html")))
jpg = sum(1 for r, d, fs in os.walk(src) for x in fs if x.lower().endswith(".jpg"))
print("源 htm/html 数:", htm, " 源 jpg 数:", jpg)
