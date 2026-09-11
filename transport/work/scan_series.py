# -*- coding: utf-8 -*-
"""探查 6 种族书 / 7 扩展全新体系 / 9 世设 三系列：
  a) 从 final_mapping.csv 提取每本书前缀（书级目录）与映射页数
  b) 扫描源下所有 模板/封面类文件（新建项目*/封面*/fengmian/cover），输出大小+中文字符数，
     以便判断空模板（跳过）vs 真内容（转换）
"""
import csv
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

SRC_ROOT = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki"
WORK = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/work"
SERIES = ["6 种族书", "7 扩展全新体系", "9 世设"]

# ---------- a) 书前缀 ----------
books = defaultdict(int)
with open(os.path.join(WORK, "final_mapping.csv"), encoding="utf-8-sig") as f:
    r = csv.reader(f)
    next(r)
    for row in r:
        if not row:
            continue
        src = row[0]
        top = src.split("\\")[0]
        if top not in SERIES:
            continue
        parts = src.split("\\")[:-1]
        if top == "9 世设":
            book = "\\".join(parts[:3]) if len(parts) >= 3 else "\\".join(parts[:2])
        else:
            book = "\\".join(parts[:2])
        books[book] += 1

print("=== 书前缀（来自 final_mapping） ===")
for b in sorted(books):
    print(f"{books[b]:4d}  {b}")
print(f"\n书数={len(books)}  映射行={sum(books.values())}")

# ---------- b) 模板/封面文件 ----------
print("\n=== 模板/封面文件扫描（size + 中文字符数） ===")
pat = ("新建项目", "封面", "fengmian", "cover", "新建")
for key in SERIES:
    base = os.path.join(SRC_ROOT, key)
    for root, dirs, fs in os.walk(base):
        for x in fs:
            if any(p in x for p in pat):
                fp = os.path.join(root, x)
                try:
                    data = open(fp, encoding="utf-8", errors="ignore").read()
                except Exception:
                    data = ""
                cn = len(re.findall(r"[一-鿿]", data))
                size = os.path.getsize(fp)
                rel = os.path.relpath(fp, SRC_ROOT)
                print(f"{size:9d}B cn={cn:5d}  {rel}")
