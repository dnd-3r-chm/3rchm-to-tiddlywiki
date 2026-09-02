# -*- coding: utf-8 -*-
"""只读预览 HBG 转换结果（不写文件），验证 title/body 格式。"""
import convert_pilot as cp
from convert_hbg import SRC_DIR, derive_title, BOOK

import os
htmls = sorted(f for f in os.listdir(SRC_DIR) if f.lower().endswith(".html"))
print("文件数:", len(htmls))
print("title 样例:")
for f in htmls[:5]:
    print("  ", derive_title(f))

# 转换一个内容页验证 body
fname = "人类.html"
text = cp.read_text(os.path.join(SRC_DIR, fname))
body = cp.extract_body(text)
body = cp.clean_html(body, BOOK)
body = cp.rewrite_images(body, "1 核心补充书籍/HBG英雄构筑指南")
print("\n=== 人类.html body 前 600 字符 ===")
print(body[:600])
print("\n含 <br>:", "<br" in body.lower())
print("含 DND3R-FEEDBACK:", "DND3R-FEEDBACK" in body)
print("含全角Ａ:", "Ａ" in body)
