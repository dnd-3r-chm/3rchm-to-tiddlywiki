# -*- coding: utf-8 -*-
"""把 wiki/tiddlers 下所有用户 .tid 的全角 ＆(U+FF06) 替换为 &amp;（渲染为 &）。

复用 convert_pilot.normalize_ampersand，与搬运管线行为完全一致（幂等）。
跳过系统 tiddler；仅备份受影响文件。
"""
import os, shutil, datetime, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import convert_pilot as cp

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers")
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "wiki_amp_" + TS)

count = 0
for root, _, files in os.walk(SRC):
    for f in files:
        if not f.endswith(".tid"):
            continue
        p = os.path.join(root, f)
        with open(p, "r", encoding="utf-8") as fh:
            s = fh.read()
        # 跳过系统 tiddler
        title_line = ""
        for line in s.split("\n", 5):
            if line.startswith("title:"):
                title_line = line
                break
        if "$:/" in title_line:
            continue
        if "\uff06" not in s:
            continue
        rel = os.path.relpath(p, SRC)
        dst = os.path.join(BAK, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(p, dst)
        t = cp.normalize_ampersand(s)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(t)
        count += 1
        print("fixed:", rel)
print("total fixed:", count)
