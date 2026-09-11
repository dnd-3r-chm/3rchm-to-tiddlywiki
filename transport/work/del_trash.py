# -*- coding: utf-8 -*-
import os

p = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/6 种族书/LoM异怪之书/8怪物/督军之眼.files/夺躯怪绳股.tid"
if os.path.exists(p):
    os.remove(p)
    print("deleted:", p)
else:
    print("not found (已删除或不存在):", p)
