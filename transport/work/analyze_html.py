#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan all HTML files: encoding, structural markers, link/image counts."""
import _paths as P
import csv
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

ROOT = P.ROOT
INV_CSV = os.path.join(ROOT, "transport", "work", "inventory.csv")

markers = {
    "has_body": 0,
    "has_table": 0,
    "has_img": 0,
    "has_a": 0,
    "has_script": 0,
    "has_style": 0,
    "has_css_link": 0,
    "gb18030_ok": 0,
    "utf8_ok": 0,
}
ext_counter = Counter()
link_ext = Counter()
img_ext = Counter()
total = 0
errors = []

with open(INV_CSV, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rel = row["相对路径"]
        if row["扩展名"].lower() not in (".htm", ".html"):
            continue
        total += 1
        path = os.path.join(ROOT, rel)
        try:
            raw = open(path, "rb").read()
        except OSError as e:
            errors.append((rel, str(e)))
            continue

        try:
            raw.decode("gb18030")
            markers["gb18030_ok"] += 1
        except UnicodeDecodeError:
            pass
        try:
            raw.decode("utf-8")
            markers["utf8_ok"] += 1
        except UnicodeDecodeError:
            pass

        low = raw[:100000].lower()
        if b"<body" in low:
            markers["has_body"] += 1
        if b"<table" in low:
            markers["has_table"] += 1
        if b"<img" in low:
            markers["has_img"] += 1
        if b"<a " in low or b"<a>" in low:
            markers["has_a"] += 1
        if b"<script" in low:
            markers["has_script"] += 1
        if b"<style" in low:
            markers["has_style"] += 1
        if b".css" in low:
            markers["has_css_link"] += 1

        # Count href/src extensions from the first 100k bytes
        for m in re.finditer(rb'''href\s*=\s*["']([^"'#]+)''', low, re.I):
            href = m.group(1).decode("latin1")
            ext = os.path.splitext(href.split("?", 1)[0])[1].lower()
            link_ext[ext] += 1
        for m in re.finditer(rb'''src\s*=\s*["']([^"']+)''', low, re.I):
            src = m.group(1).decode("latin1")
            ext = os.path.splitext(src.split("?", 1)[0])[1].lower()
            img_ext[ext] += 1

print("total html files:", total)
print("markers:", markers)
print("link extensions:", link_ext.most_common(20))
print("src extensions:", img_ext.most_common(20))
print("errors:", len(errors))
for e in errors[:20]:
    print(e)
