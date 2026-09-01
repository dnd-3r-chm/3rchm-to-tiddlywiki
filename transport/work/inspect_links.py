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

found = 0
with open(INV_CSV, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        rel = row["相对路径"]
        if not rel.lower().endswith((".htm", ".html")):
            continue
        path = os.path.join(ROOT, rel)
        raw = open(path, "rb").read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("gb18030", errors="replace")
        hrefs = re.findall(r'''href\s*=\s*["']([^"']+)["']''', text, re.I)
        htm_hrefs = [h for h in hrefs if ".htm" in h.lower() or ".html" in h.lower()]
        if htm_hrefs:
            print("FILE:", rel)
            print("TITLE:", re.search(r"<title>(.*?)</title>", text, re.S).group(1).strip() if re.search(r"<title>(.*?)</title>", text, re.S) else "")
            for h in htm_hrefs[:15]:
                print("  HREF:", h)
            print()
            found += 1
            if found >= 5:
                break
print("found files:", found)
