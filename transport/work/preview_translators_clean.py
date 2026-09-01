#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clean_spell_tids as cst

path = r"E:\dnd3r_full\transport\wiki\tiddlers\译者名录1.1.tid"
content = open(path, encoding="utf-8").read()
parts = content.split("\n\n", 1)
body = parts[1]
cleaned = cst.clean_body(body)
print(cleaned[:6000])
