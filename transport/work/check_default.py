#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

html = urllib.request.urlopen("http://127.0.0.1:8080/", timeout=10).read().decode("utf-8")
print("has DefaultTiddlers:", "DefaultTiddlers" in html)
m = re.search(r'<script class="tiddlywiki-tiddler-store" type="application/json">(.*?)</script>', html, re.S)
if m:
    import json
    data = json.loads(m.group(1))
    for t in data:
        if t.get("title") == "$:/DefaultTiddlers":
            print(json.dumps(t, ensure_ascii=False, indent=2))
            break
    else:
        print("$:/DefaultTiddlers not in store")
else:
    print("store not found")
