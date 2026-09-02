# -*- coding: utf-8 -*-
import os, re

D = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍/XPH扩展灵能手册/7装备"
for f in sorted(os.listdir(D)):
    if not f.endswith(".tid"):
        continue
    t = open(os.path.join(D, f), encoding="utf-8").read()
    n = len(re.findall(r"<table", t))
    if n == 0:
        continue
    cg = len(re.findall(r"colgroup", t))
    tb = len(re.findall(r"tbody", t))
    inp = sum(1 for m in re.finditer(r"<table>.*?</table>", t, re.S | re.I) if "<p" in m.group(0))
    w = len(re.findall(r"<td[^>]*width", t))
    print("{:16s} 表{} colgroup={} tbody={} 表内p={} tdwidth={}".format(f, n, cg, tb, inp, w))
