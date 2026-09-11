# -*- coding: utf-8 -*-
"""验证 convert_pilot.normalize_quotes 对各类引号实体/字符变体的转换。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_pilot as cp

S = (
    'A &#8220;hi&#8221; '          # 十进制实体
    'B &#x201C;c&#x201D; '         # 十六进制实体
    'C &quot;d&quot; '             # 命名实体
    "D &#39;e&#39; "               # 单引号实体
    'E \u201cf\u201d '             # 字符形态弯双引号
    'F \u2018g\u2019 '             # 字符形态弯单引号
    'G &#08220;pad&#08221;'        # 前导零变体
)
out = cp.normalize_quotes(S)
print("OUT:", out)
bad = [c for c in out if c in '\u201c\u201d\u201e\u2018\u2019\u201a\uff02\uff07']
print("残留弯引号/全角引号:", bad if bad else "无")
