# -*- coding: utf-8 -*-
import os, re
import _clean_all_noise as cn

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TID = os.path.join(ROOT, "transport", "wiki", "tiddlers")

# 检查几个表格文件处理前后表格结构完整性
tests = [
    os.path.join(TID, "0 核心三宝书", "DMG城主指南", "所有DMG表格", "表3-11：设置地下城.tid"),
    os.path.join(TID, "10 附录", "如何使用大不全.tid"),
    os.path.join(TID, "1 核心补充书籍", "MM5怪物图鉴5", "封面.tid"),
    os.path.join(TID, "1 核心补充书籍", "PHB2玩家手册2", "职业", "魔剑客.tid"),
    os.path.join(TID, "1 核心补充书籍", "XPH扩展灵能手册", "7装备", "武器.tid"),
]
for p in tests:
    if not os.path.isfile(p):
        print("MISS", p); continue
    raw = open(p, encoding="utf-8").read()
    lines = raw.split("\n")
    body = "\n".join(lines[5:])
    new = cn.normalize(body)
    # 检查关键结构是否保留
    checks = {
        "table存在": "<table" in new,
        "tr存在": "<tr" in new,
        "td存在": "<td" in new,
        "width属性保留": 'width=' in new or 'width="' in new,
        "无o:p残留": "<o:p>" not in new and "<o:P>" not in new,
        "无span残留": "<span" not in new,
        "无style残留": "style=" not in new,
        "无class残留": "class=" not in new,
        "无&nbsp;残留": "&nbsp;" not in new,
        "无全角直引号ff02": "\uff02" not in new,
    }
    print("===", os.path.relpath(p, TID))
    for k, v in checks.items():
        print(f"   {k}: {v}")
    # 展示表格首行
    m = re.search(r"<table.*?</table>", new, re.S)
    if m:
        print("   表格片段:", repr(m.group(0)[:160]))
