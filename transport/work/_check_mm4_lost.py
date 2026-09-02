# -*- coding: utf-8 -*-
import re, os, difflib
import clean_mm4 as c

def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"</?[^>]+>", "", s)).strip()

# 遍历所有 target dir，找变化较大的文件逐个 diff
for d in c.TARGET_DIRS:
    dd = os.path.join(c.MM3, d)
    if not os.path.isdir(dd):
        continue
    for f in sorted(os.listdir(dd)):
        if not f.lower().endswith(".tid"):
            continue
        path = os.path.join(dd, f)
        raw = open(path, encoding="utf-8").read()
        lines = raw.split("\n")
        header, body = "\n".join(lines[:5]), "\n".join(lines[5:])
        new = c.clean_body(body, f)
        tb = strip_tags(c.normalize(body))
        ta = strip_tags(new)
        if abs(len(ta) - len(tb)) <= max(30, len(tb) * 0.02):
            continue
        # 只看减少（疑似丢失）
        if len(ta) >= len(tb):
            continue
        sm = difflib.ndiff(list(tb), list(ta))
        minus = "".join(ch[2:] for ch in sm if ch.startswith("- "))
        print(f"=== {d}\\{f} === 原 {len(tb)} 新 {len(ta)} 减 {len(minus)}")
        print("  减少:", minus[:60])
        print()
