# -*- coding: utf-8 -*-
import os, difflib, re
import clean_mm5 as c

def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"</?[^>]+>", "", s)).strip()

rel = ["加恩格拉斯巨兽.tid", "大地精.tid", "寇涛鱼人.tid", "攻城甲虫.tid", "狂猎.tid",
       os.path.join("龙的伟大游戏", "沙文特龙.tid")]
for r in rel:
    path = os.path.join(c.MM3, "怪物", r)
    raw = open(path, encoding="utf-8").read()
    lines = raw.split("\n")
    body = "\n".join(lines[5:])
    new = c.clean_body(body, os.path.basename(r))
    tb = strip_tags(c.normalize(body))
    ta = strip_tags(new)
    sm = difflib.ndiff(list(tb), list(ta))
    minus = "".join(ch[2:] for ch in sm if ch.startswith("- "))
    print(f"=== {r} === 减 {len(minus)}")
    print("  减少:", minus[:80])
    print()
