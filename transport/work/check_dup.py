# -*- coding: utf-8 -*-
import csv
from collections import Counter

FMP = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/work/final_mapping.csv"
SER = ["6 种族书", "7 扩展全新体系", "9 世设"]

src = [
    r["源文件相对路径"]
    for r in csv.DictReader(open(FMP, encoding="utf-8-sig"))
    if r["源文件相对路径"].split("\\")[0] in SER
]
c = Counter(src)
print("总行", len(src), "唯一", len(set(src)))
dups = [(k, v) for k, v in c.items() if v > 1]
print("重复源数", len(dups))
for k, v in dups[:20]:
    print(f"DUP x{v}: {k}")
