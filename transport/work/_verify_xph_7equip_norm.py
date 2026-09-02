# -*- coding: utf-8 -*-
import os, re
import _normalize_xph_7equip_all as M

D = M.D
for f in ["灵物.tid", "防具.tid", "灵能物品说明.tid", "灵冠.tid"]:
    p = os.path.join(D, f)
    t = open(p, encoding="utf-8").read()
    m = M.TABLE_RE.search(t)
    print("==== " + f + " ====")
    print(M.norm_table(m.group(0)))
    print()
