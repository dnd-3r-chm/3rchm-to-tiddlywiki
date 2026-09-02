# -*- coding: utf-8 -*-
"""确认 XPH 被跳过，且 1 核心补充书籍 下其他书不受影响。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_book as cb

should_skip = [
    r"1 核心补充书籍\XPH扩展灵能手册\6显能\A.htm",
    r"1 核心补充书籍\XPH扩展灵能手册\8怪物\溶晶怪.htm",
    r"1 核心补充书籍\XPH扩展灵能手册\1种族\厄兰.htm",
    r"0 核心三宝书\PHB玩家手册\2种族\人类.htm",
    r"10 附录\版本历史.htm",
]
should_pass = [
    r"1 核心补充书籍\PHB2玩家手册2\玩家手册2.htm",
    r"1 核心补充书籍\DMG2城主指南2\城主指南2.htm",
    r"1 核心补充书籍\MM3怪物图鉴3\封面.htm",
    r"1 核心补充书籍\MM4怪物图鉴4\封面.htm",
    r"1 核心补充书籍\MM5怪物图鉴5\封面.htm",
    r"1 核心补充书籍\3e的核心补充内容\foo.htm",
    r"2 万物万法万律\MIC万物大全\封面.htm",
]


def is_skip(rel):
    return (rel in cb.SKIP_SOURCES
            or any(rel.startswith(p) for p in cb.SKIP_SOURCE_PREFIXES))


print("=== 应跳过 ===")
ok = True
for t in should_skip:
    r = is_skip(t)
    ok &= r
    print(f"{'SKIP ' if r else 'PASS '} {t}")
print("=== 不应跳过（后续还要搬运）===")
for t in should_pass:
    r = is_skip(t)
    ok &= not r
    print(f"{'SKIP ' if r else 'PASS '} {t}")
print("\n结论:", "全部符合预期" if ok else "!! 存在不符")
print("当前 SKIP_SOURCE_PREFIXES:")
for p in sorted(cb.SKIP_SOURCE_PREFIXES):
    print("   ", p)
