# -*- coding: utf-8 -*-
"""对比 HBG 当前 tid 与其 .bak_ 备份，输出首个差异位置与上下文。"""
import os, re, difflib

D = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍/HBG英雄构筑指南"
TARGETS = ["半兽人", "名字列表", "人类"]

for name in TARGETS:
    cur_p = os.path.join(D, name + ".tid")
    baks = [f for f in os.listdir(D) if f.startswith(name + ".tid.bak_")]
    if not baks:
        print(f"--- {name}: 无备份")
        continue
    bak_p = os.path.join(D, sorted(baks)[-1])
    cur = open(cur_p, encoding="utf-8").read()
    bak = open(bak_p, encoding="utf-8").read()
    print(f"=== {name} ===  当前 {len(cur)} 字符, 备份 {len(bak)} 字符")
    if cur == bak:
        print("  完全相同")
        continue
    # 找首个差异
    i = 0
    while i < min(len(cur), len(bak)) and cur[i] == bak[i]:
        i += 1
    print(f"  首个差异位置: {i}")
    print(f"  备份[旧]上下文: ...{bak[max(0,i-60):i+80]!r}")
    print(f"  当前[新]上下文: ...{cur[max(0,i-60):i+80]!r}")
    # 统计差异行数
    dl = list(difflib.unified_diff(bak.split("\n"), cur.split("\n"), lineterm="", n=0))
    print(f"  diff 行数: {len(dl)}")
    for line in dl[:8]:
        print("   ", line[:150])
    print()
