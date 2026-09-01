#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

url = "http://127.0.0.1:8080/"
html = urllib.request.urlopen(url, timeout=30).read().decode("utf-8")
m = re.search(r'<script class="tiddlywiki-tiddler-store" type="application/json">(.*?)</script>', html, re.S)
if not m:
    print("no store")
    sys.exit(1)
data = json.loads(m.group(1))
print("tiddlers in store:", len(data))
for t in data:
    title = t.get("title", "")
    if title in ("[DMG] 城主指南", "0 核心三宝书/DMG城主指南/封面.jpg"):
        print("=====", title)
        print(json.dumps(t, ensure_ascii=False, indent=2)[:2000])
