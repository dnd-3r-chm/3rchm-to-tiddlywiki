# -*- coding: utf-8 -*-
import os, re
import _normalize_xph_7equip_all as M

D = M.D
t = open(os.path.join(D, "灵冠.tid"), encoding="utf-8").read()
blocks = list(M.TABLE_RE.finditer(t))
print("table blocks found:", len(blocks))
for i, m in enumerate(blocks):
    print(f"--- block {i} tbody={len(re.findall('tbody', m.group(0), re.I))} first80:", m.group(0)[:80])
# 检查 norm_table 输出
for i, m in enumerate(blocks):
    repl = M.norm_table(m.group(0))
    print(f"--- normed block {i} tbody={len(re.findall('tbody', repl, re.I))} first80:", repl[:80])
