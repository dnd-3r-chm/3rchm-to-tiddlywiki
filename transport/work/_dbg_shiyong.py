# -*- coding: utf-8 -*-
import _normalize_xph_7equip_all as M
D = M.D
import os
t = open(os.path.join(D, "使用物品.tid"), encoding="utf-8").read()
m = M.TABLE_RE.search(t)
orig = m.group(0)
print("ORIG tbody count:", len(re.findall(r"tbody", orig, re.I)))
repl = M.norm_table(orig)
print("REPL tbody count:", len(re.findall(r"tbody", repl, re.I)))
print("REPL first 200:", repl[:200])
