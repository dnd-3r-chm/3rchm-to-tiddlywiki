# -*- coding: utf-8 -*-
"""从 wiki_period_20260907_202414 备份回滚 13 个文件（修正编号列表误判后重跑用）。"""
import os, shutil

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, "backups", "wiki_period_20260907_202414")
DST = os.path.join(BASE, "wiki", "tiddlers")

n = 0
for root, _, fs in os.walk(SRC):
    for f in fs:
        p = os.path.join(root, f)
        rel = os.path.relpath(p, SRC)
        dst = os.path.join(DST, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(p, dst)
        n += 1
        print("restored:", rel)
print("total restored:", n)
