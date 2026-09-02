# -*- coding: utf-8 -*-
import os, re
import _normalize_xph_7equip_all as M

D = M.D
for f in ["防具.tid", "灵冠.tid", "使用物品.tid"]:
    p = os.path.join(D, f)
    t = open(p, encoding="utf-8").read()
    m = M.TABLE_RE.search(t)
    out = M.norm_table(m.group(0))
    print("==== " + f + " ====")
    print(out[-220:] if len(out) > 220 else out)
    print()
