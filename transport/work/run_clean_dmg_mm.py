# -*- coding: utf-8 -*-
"""清理 0 核心三宝书 下的 MM怪物图鉴 与 DMG城主指南（常量路径，规避中文传参乱码）。

排除 DMG 的 简介 / 第一章 / 第二章：这三章含大量人工合并、拆分、排版过的节点
（见 convert_book.py 的 SKIP_SOURCES，如「跑团」「战斗」「更多移动规则」等
合并节点及其父节点），清理脚本会重写全文，有覆盖人工成果的风险，故整棵子树跳过。

用法：
  python run_clean_dmg_mm.py            # 干跑
  python run_clean_dmg_mm.py --apply    # 实际写入（先自动备份到 work/）
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P
import clean_residual as cr

MM = os.path.join(P.WIKI_TIDDLERS, "0 核心三宝书", "MM怪物图鉴")
DMG = os.path.join(P.WIKI_TIDDLERS, "0 核心三宝书", "DMG城主指南")

BOOK_DIRS = [MM, DMG]
# DMG 的人工调整章节（整棵子树排除，防覆盖手动合并/排版成果）
EXCLUDE_MAP = {
    DMG: ["简介", "第一章", "第二章"],
}

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    print("处理书目：")
    for d in BOOK_DIRS:
        print(f"  - {os.path.relpath(d, P.WIKI_TIDDLERS)}")
        for e in EXCLUDE_MAP.get(d, ()):
            print(f"      排除子目录：{e}/（人工调整过，防覆盖）")
    print()
    cr.run(BOOK_DIRS, EXCLUDE_MAP, apply=apply)
