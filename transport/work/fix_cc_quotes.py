# -*- coding: utf-8 -*-
# 将 CC 目录 .tid 中的弯引号/全角引号统一为半角直引号，幂等。
import os, shutil, datetime

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers\3 完美系列\CC完美斗士")
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "cc_quotes_" + ts)

MAP = {
    '\u201c': '"',   # " 左双弯引号 -> 半角
    '\u201d': '"',   # " 右双弯引号 -> 半角
    '\u2018': "'",   # ' 左单弯引号 -> 半角
    '\u2019': "'",   # ' 右单弯引号 -> 半角
    '\uff02': '"',   # " 全角双引号 -> 半角
    '\uff07': "'",   # ' 全角单引号 -> 半角
}

shutil.copytree(SRC, BAK)
print("backup ->", BAK)

n = 0
for root, _, files in os.walk(SRC):
    for f in files:
        if not f.endswith(".tid"):
            continue
        p = os.path.join(root, f)
        with open(p, "r", encoding="utf-8") as fh:
            s = fh.read()
        t = s
        for k, v in MAP.items():
            if k in t:
                t = t.replace(k, v)
        if t != s:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(t)
            n += 1
            print("fixed:", os.path.relpath(p, SRC))
print("total fixed:", n)
