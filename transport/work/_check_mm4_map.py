# -*- coding: utf-8 -*-
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fm = os.path.join(ROOT, "transport", "work", "final_mapping.csv")
rows = list(csv.DictReader(open(fm, encoding="utf-8-sig")))
prefix = "1 核心补充书籍\\MM4怪物图鉴4"
mm4 = [r for r in rows if r["源文件相对路径"].startswith(prefix)]
print("final_mapping MM4 rows:", len(mm4))
for r in mm4[:6]:
    print(" ", r["源文件相对路径"], "->", r["Tiddler标题"])
