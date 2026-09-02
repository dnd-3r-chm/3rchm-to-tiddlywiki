# -*- coding: utf-8 -*-
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", "MM4怪物图鉴4")
# 全角 A-Z a-z 0-9 （） “” ‘’
fw = "[Ａ-Ｚａ-ｚ０-９（）＂＇‘’]"
bad = []
for p in glob.glob(os.path.join(d, "**", "*.tid"), recursive=True):
    t = open(p, encoding="utf-8").read()
    for m in re.finditer(fw, t):
        bad.append((os.path.relpath(p, ROOT), m.group()))
        break
print("全角ASCII违规文件数:", len(bad))
for r, ch in bad[:20]:
    print("  ", r, repr(ch))
