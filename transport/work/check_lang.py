#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

html = urllib.request.urlopen("http://127.0.0.1:8080/", timeout=10).read().decode("utf-8")
m = re.search(r'<script class="tiddlywiki-tiddler-store" type="application/json">(.*?)</script>', html, re.S)
data = json.loads(m.group(1))
for t in data:
    title = t.get("title", "")
    if "zh-Hans" in title or title == "$:/language":
        print(title, "=>", json.dumps(t, ensure_ascii=False)[:300])
