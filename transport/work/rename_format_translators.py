#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 译者名录1.1.tid 更名为 译者名录.tid，并把书名标题改为 [缩写]书名 格式。"""
import _paths as P
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

OLD = os.path.join(P.WIKI_TIDDLERS, "译者名录1.1.tid")
NEW = os.path.join(P.WIKI_TIDDLERS, "译者名录.tid")

# 根据 10 附录/出版书籍顺序.htm 中的缩写整理
HEADING_MAP = {
    "PHB2": "[PHB2] 玩家手册2",
    "DMG2": "[DMG2] 城主指南2",
    "xph（扩展灵能手册）": "[XPH] 扩展灵能手册",
    "MM3": "[MM3] 怪物图鉴3",
    "MM4": "[MM4] 怪物图鉴4",
    "MM5": "[MM5] 怪物图鉴5",
    "万物": "[MIC] 万物大全",
    "完美冒险": "[CAd] 完美冒险",
    "完美奥术": "[CAr] 完美奥术",
    "完美斗士": "[CC] 完美斗士",
    "完美神力": "[CD] 完美神力",
    "完美巫师": "[CM] 完美巫师",
    "完美灵能": "[CPsi] 完美灵能",
    "完美恶徒": "[CS] 完美恶徒",
    "完美战士": "[CW] 完美战士",
    "崇善之书": "[BoED] 崇善之书",
    "PH": "[PlH] 位面手册",
    "LM死灵之书": "[LM] 死灵之书",
    "FC1": "[FC1] 深渊堕群",
    "FC2": "[FC2] 九狱君王",
    "都市风貌": "[City] 城市风貌",
    "沙暴书": "[Sand] 沙暴书",
    "霜燃书": "[Frost] 霜燃书",
    "风暴书": "[Storm] 风暴书",
    "巨龙之书": "[Dra] 巨龙之书",
    "龙之魔法": "[DrM] 龙之魔法",
    "龙之族裔": "[RotD] 龙之族裔",
    "天命族裔": "[RoD] 天命族裔",
    "荒野族裔": "[RotW] 荒野族裔",
    "传古武器": "[WoL] 传古武器",
    "战斗、惊骇、模型": "[HoB] 战斗英雄 / [HoH] 惊骇英雄 / [MH] 模型手册",
    "艾伯伦": "[ECS] 艾伯伦",
    "其他：": "其他：",
    "校对：": "校对：",
    "报错达人：": "报错达人：",
    "牢北（报错10次以上）": "牢北（报错10次以上）",
}


def format_heading(text):
    return HEADING_MAP.get(text, text)


def main():
    if not os.path.exists(OLD):
        print("old file not found")
        return
    with open(OLD, "r", encoding="utf-8") as f:
        content = f.read()

    def repl(m):
        inner = m.group(1).strip()
        return f"<h3>{format_heading(inner)}</h3>"

    new_content = re.sub(r"<h3>(.*?)</h3>", repl, content, flags=re.S)

    # 把误设为 h3 的“牢北（报错10次以上）”改回普通段落
    new_content = new_content.replace(
        "<h3>牢北（报错10次以上）</h3>",
        "<p>牢北（报错10次以上）</p>",
    )

    with open(NEW, "w", encoding="utf-8") as f:
        f.write(new_content)
    os.remove(OLD)
    print(f"renamed: {OLD} -> {NEW}")


if __name__ == "__main__":
    main()
