# -*- coding: utf-8 -*-
import os, re
D = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍/HBG英雄构筑指南"
BR = re.compile(r"<br\s*/?>", re.I)
FF = re.compile(r"[\uff01-\uff5e\u3000-\u303f]")  # 全角标点/ASCII区
TABLE = re.compile(r"<table", re.I)
P_BLOCK = re.compile(r"<p\b[^>]*>.*?</p>", re.S | re.I)

files = sorted(f for f in os.listdir(D) if f.endswith(".tid") and not f.endswith(".bak"))
print("tid 文件数:", len(files))
br = ff = tbl = dup = 0
bad_title = []
for f in files:
    t = open(os.path.join(D, f), encoding="utf-8").read()
    # 头4行
    head = "\n".join(t.split("\n")[:4])
    if " (HBG-HBG-" in t[:120]:
        bad_title.append(f)
    br += len(BR.findall(t))
    ff += len(FF.findall(t))
    tbl += len(TABLE.findall(t))
print("含 <br>:", br)
print("含全角标点/ASCII:", ff)
print("含 <table>:", tbl)
print("错误双HBG标题:", len(bad_title), bad_title[:5])

# 图片
imgs = [f for f in os.listdir(D) if f.lower().endswith((".jpeg", ".jpg", ".png"))]
metas = [f for f in os.listdir(D) if f.endswith(".meta")]
print("图片文件:", imgs)
print("meta文件:", metas)
