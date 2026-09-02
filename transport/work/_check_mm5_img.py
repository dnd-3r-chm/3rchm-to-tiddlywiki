# -*- coding: utf-8 -*-
import os, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
book = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", "MM5怪物图鉴5")
# 产物 tid 数
tids = [p for p in glob.glob(os.path.join(book, "**", "*.tid"), recursive=True) if "\\插图\\" not in p.replace("/", "\\")]
print("产物 tid 数:", len(tids))
# 插图
ill = os.path.join(book, "插图")
jpgs = [f for f in os.listdir(ill) if f.lower().endswith((".jpg", ".jpeg", ".png"))] if os.path.isdir(ill) else []
miss_meta = [f for f in jpgs if not os.path.isfile(os.path.join(ill, f + ".meta"))]
print("插图图片:", len(jpgs), " 缺meta:", len(miss_meta))
# 怪物子目录
mdir = os.path.join(book, "怪物")
print("怪物子目录:")
for d in sorted(os.listdir(mdir)):
    full = os.path.join(mdir, d)
    if os.path.isdir(full):
        print("  ", d, "->", len([x for x in os.listdir(full) if x.lower().endswith(('.tid','.htm','.html'))]), "文件")
    else:
        print("  [file]", d)
# 标题含全角括号情况
fw = "[（）]"
bad = []
for p in tids:
    t = open(p, encoding="utf-8").read()
    if re.search(fw, t):
        bad.append(os.path.relpath(p, ROOT))
print("含全角（）tid数:", len(bad))
for r in bad[:10]:
    print("   ", r)
