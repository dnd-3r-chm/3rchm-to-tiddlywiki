# -*- coding: utf-8 -*-
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", "MM4怪物图鉴4", "插图")
print("插图目录存在:", os.path.isdir(d))
print("文件数:", len(os.listdir(d)) if os.path.isdir(d) else 0)
# 统计 tid 中引用但缺 meta 的情况
import re, glob
tid_dir = os.path.join(ROOT, "transport", "wiki", "tiddlers", "1 核心补充书籍", "MM4怪物图鉴4")
imgs = set()
for p in glob.glob(os.path.join(tid_dir, "**", "*.tid"), recursive=True):
    t = open(p, encoding="utf-8").read()
    for m in re.findall(r"\[img\[([^\]]+)\]\]", t):
        imgs.add(m)
print("tid 引用图片数:", len(imgs))
miss = [i for i in imgs if not os.path.isfile(os.path.join(ROOT, "transport", "wiki", "tiddlers", i)) or
        not os.path.isfile(os.path.join(ROOT, "transport", "wiki", "tiddlers", i + ".meta"))]
print("缺物理图或meta数:", len(miss))
for i in miss[:10]:
    print("  ", i)
