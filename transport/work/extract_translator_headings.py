#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _paths as P
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = os.path.join(P.WIKI_TIDDLERS, "译者名录1.1.tid")
text = open(path, encoding="utf-8").read()
for m in re.finditer(r"<h3>(.*?)</h3>", text, re.S):
    print(m.group(1))
