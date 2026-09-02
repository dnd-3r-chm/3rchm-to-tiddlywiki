# -*- coding: utf-8 -*-
import os, re
BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍"
f = r"DMG2城主指南2\数据资料格式.tid"
t = open(os.path.join(BASE, f), encoding="utf-8").read()
print("总 br:", len(re.findall(r"<br\s*/?>", t, re.I)))
print("样本前400:")
print(t[:400])
