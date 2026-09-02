# -*- coding: utf-8 -*-
import os
import clean_mm5 as c

for name in ["封面.tid", "怪物专长.tid"]:
    p = os.path.join(c.MM3, name)
    if not os.path.isfile(p):
        print(name, "不存在，跳过")
        continue
    raw = open(p, encoding="utf-8").read()
    lines = raw.split("\n")
    header, body = "\n".join(lines[:5]), "\n".join(lines[5:])
    new = c.normalize(body)
    if new != body:
        with open(p, "w", encoding="utf-8") as f:
            f.write(header + "\n" + new)
        print(name, "已清理")
    else:
        print(name, "无变化")
