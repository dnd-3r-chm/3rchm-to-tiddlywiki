# -*- coding: utf-8 -*-
import os, re
import _normalize_xph_7equip_all as M

D = M.D
total = 0
issues = []
for f in sorted(os.listdir(D)):
    if not f.endswith(".tid"):
        continue
    t = open(os.path.join(D, f), encoding="utf-8").read()
    blocks = list(M.TABLE_RE.finditer(t))
    if not blocks:
        continue
    total += len(blocks)
    for m in blocks:
        tb = m.group(0)
        if re.search(r"colgroup|tbody", tb, re.I):
            issues.append((f, "残留 colgroup/tbody"))
        if re.search(r"<td[^>]*\b(width|height|vAlign|align)\b", tb, re.I):
            issues.append((f, "残留 td 死属性"))
        if re.search(r"<table[^>]*\s+\w", tb, re.I):
            issues.append((f, "残留 table 属性"))
        if re.search(r"<p\b", tb, re.I):
            issues.append((f, "残留 <p>"))
        # 单元格内容前导空格检查（应与表7-5一致 <td>X</td>）
        if re.search(r"<td[^>]*>\s+\S", tb):
            issues.append((f, "td内容前导空格"))
        if re.search(r"\S\s{2,}</td>", tb):
            issues.append((f, "td内容尾随多空格"))
print("目录表格总数:", total)
if issues:
    for f, msg in issues:
        print("  !!", f, "->", msg)
else:
    print("复验通过：所有表格均为紧凑 <table><tr><td>..</td></tr>..</table>，无 colgroup/tbody/死属性/<p/前导尾随空格")
