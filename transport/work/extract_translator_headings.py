#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = r"E:\dnd3r_full\transport\wiki\tiddlers\译者名录1.1.tid"
text = open(path, encoding="utf-8").read()
for m in re.finditer(r"<h3>(.*?)</h3>", text, re.S):
    print(m.group(1))
