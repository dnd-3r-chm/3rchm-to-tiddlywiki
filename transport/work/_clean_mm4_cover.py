# -*- coding: utf-8 -*-
import os, re
import clean_mm4 as c

p = os.path.join(c.MM3, "封面.tid")
raw = open(p, encoding="utf-8").read()
lines = raw.split("\n")
header, body = "\n".join(lines[:5]), "\n".join(lines[5:])
new = c.normalize(body)
if new != body:
    with open(p, "w", encoding="utf-8") as f:
        f.write(header + "\n" + new)
    print("封面.tid 已清理")
else:
    print("封面.tid 无变化")
