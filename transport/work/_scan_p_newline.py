#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

base = r"d:\Users\v_jrchchen\Documents\3rchm-to-tiddlywiki\transport\wiki\tiddlers\10 附录"

# 三类 p 内换行形态
rx_tag_break = re.compile(r"<p[^>]*\n")          # <p 后属性未闭合就换行
rx_after_gt  = re.compile(r"<p[^>]*>\s*\n")        # <p> 后紧跟换行(内容前)
rx_inside    = re.compile(r"<p[^>]*>[\s\S]*?\n[\s\S]*?</p>")  # <p>..换行..</p> 多行内容

total = {"tag_break":0,"after_gt":0,"inside":0}
samples = []
for root, dirs, files in os.walk(base):
    for fn in files:
        if not fn.lower().endswith(".tid"):
            continue
        p = os.path.join(root, fn)
        with open(p, encoding="utf-8") as f:
            txt = f.read()
        c1 = len(rx_tag_break.findall(txt))
        c2 = len(rx_after_gt.findall(txt))
        c3 = len(rx_inside.findall(txt))
        if c1 or c2 or c3:
            rel = os.path.relpath(p, base)
            total["tag_break"] += c1
            total["after_gt"] += c2
            total["inside"] += c3
            # 取一个样例
            m = rx_tag_break.search(txt) or rx_after_gt.search(txt) or rx_inside.search(txt)
            if m and len(samples) < 8:
                seg = m.group(0)
                samples.append((rel, seg[:200].replace("\n","\\n")))

print("TOTAL:", total)
for rel, seg in samples:
    print("----", rel)
    print(seg)
