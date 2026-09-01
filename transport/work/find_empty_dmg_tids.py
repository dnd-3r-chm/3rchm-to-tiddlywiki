#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _paths as P
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

dirs = [
    os.path.join(P.DMG_TIDDLERS, "第一章"),
    os.path.join(P.DMG_TIDDLERS, "简介"),
]

for d in dirs:
    print("===", d)
    for name in sorted(os.listdir(d)):
        if not name.endswith(".tid"):
            continue
        path = os.path.join(d, name)
        content = open(path, encoding="utf-8").read()
        parts = content.split("\n\n", 1)
        body = parts[1].strip() if len(parts) == 2 else ""
        if not body:
            print("EMPTY:", name)
