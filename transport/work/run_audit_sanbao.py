# -*- coding: utf-8 -*-
"""审计 0 核心三宝书（常量路径，规避 PowerShell 中文传参乱码）。

用法：python run_audit_sanbao.py
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P
import _audit_books as ab

BOOKS = [
    os.path.join(P.WIKI_TIDDLERS, "0 核心三宝书", "MM怪物图鉴"),
    os.path.join(P.WIKI_TIDDLERS, "0 核心三宝书", "DMG城主指南"),
]

if __name__ == "__main__":
    print("=" * 100)
    print("0 核心三宝书 审计（只读）")
    print("=" * 100)
    grand = {"tids": 0, "chars": 0, "imgs": 0}
    for d in BOOKS:
        st, iss = ab.audit_book(d)
        grand["tids"] += st["tids"]
        grand["chars"] += st["chars"]
        grand["imgs"] += st["imgs"]
        rel = os.path.relpath(d, P.WIKI_TIDDLERS)
        bad = sum(st["bad"].values()) + st["br_out"]
        flag = "OK  " if bad == 0 and st["img_nometa"] == 0 else "!!  "
        print(f"\n{flag}{rel}")
        print(
            f"    tid {st['tids']:>4}  可见字符 {st['chars']:>8}  图片 {st['imgs']:>3}"
            f"(缺meta {st['img_nometa']})  空正文 {st['empty']}  header缺空行 {st['no_blank']}"
        )
        detail = "  ".join(f"{k}={st['bad'][k]}" for k in ab.BAD_KEYS)
        print(f"    噪音: {detail}  br(段落内)={st['br_out']}  br(表格内,合规)={st['br_in']}")
        for k in ab.BAD_KEYS + ("br_out",):
            items = iss.get(k, [])
            if items:
                shown = ", ".join(f"{n}({c})" for n, c in items[:8])
                more = f" ...共{len(items)}个文件" if len(items) > 8 else ""
                print(f"      [{k}] {shown}{more}")
    print("\n" + "=" * 100)
    print(f"合计：tid {grand['tids']}  可见字符 {grand['chars']}  图片 {grand['imgs']}")
    print("=" * 100)
