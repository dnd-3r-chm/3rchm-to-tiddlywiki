#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _paths as P
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

path = os.path.join(P.ROOT, "10 附录", "出版书籍顺序.htm")
raw = open(path, "rb").read()
try:
    text = raw.decode("utf-8")
except UnicodeDecodeError:
    text = raw.decode("gb18030", errors="replace")

rows = re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S | re.I)
for row in rows:
    cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S | re.I)
    if len(cells) >= 4:
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
        # 时间, 英文, 缩写, 中文
        print(cells)
