# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
book = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", "MM3怪物图鉴3")
fw = "[Ａ-Ｚａ-ｚ０-９（）＂＇‘’]"
for p in glob.glob(os.path.join(book, "**", "*.tid"), recursive=True):
    if os.sep + "插图" + os.sep in p:
        continue
    t = open(p, encoding="utf-8").read()
    for m in re.finditer(fw, t):
        i = m.start()
        print(os.path.relpath(p, ROOT), "->", repr(t[max(0,i-15):i+15]), "char=", hex(ord(m.group())))
