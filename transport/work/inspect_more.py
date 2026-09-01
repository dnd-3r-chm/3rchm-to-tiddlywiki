#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _paths as P
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = P.ROOT
INV_CSV = os.path.join(ROOT, "transport", "work", "inventory.csv")

# Find a page that contains a table and links, preferably under PHB
target = None
with open(INV_CSV, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        rel = row["相对路径"]
        if not rel.lower().endswith((".htm", ".html")):
            continue
        if "PHB" in rel and "表" in row["文件名"]:
            target = rel
            break

if not target:
    print("no target found")
    sys.exit(1)

print("target:", target)
path = os.path.join(ROOT, target)
raw = open(path, "rb").read()
try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    text = raw.decode("gb18030", errors="replace")
print("length:", len(text))
print(text[:5000])
