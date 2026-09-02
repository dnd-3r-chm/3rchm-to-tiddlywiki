# -*- coding: utf-8 -*-
"""诊断 clean_mic.py 的 6 个字符数异常文件：输出被删除的具体内容样本。"""
import os, re, sys, difflib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P
from clean_mic import MIC, clean_body

TARGETS = [
    "穿戴物/身体.tid",
    "穿戴物/头部.tid",
    "武器/附魔/+1.tid",
]
for rel in TARGETS:
    p = os.path.join(MIC, *rel.split("/"))
    if not os.path.exists(p):
        print(f"--- {rel}: 不存在")
        continue
    raw = open(p, encoding="utf-8").read()
    lines = raw.split("\n")
    body = "\n".join(lines[5:])
    new = clean_body(body)
    old_norm = re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", body))
    new_norm = re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", new))
    print(f"=== {rel} ===  {len(old_norm)} -> {len(new_norm)}  (差 {len(new_norm)-len(old_norm)})")
    # 找出新文本中缺失的字符序列：用最长公共子串法粗略定位
    sm = difflib.SequenceMatcher(None, old_norm, new_norm, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("delete", "replace"):
            seg = old_norm[i1:i2]
            if len(seg) > 3:
                print(f"   [{tag}] 删除片段({len(seg)}字): {seg[:120]}")
    print()
