# -*- coding: utf-8 -*-
"""检测（只读，不修改）0 核心三宝书/PHB玩家手册 的噪音分布。

PHB 全本已排版完成（含 11法术/法术描述 手工重排），已整体加入 SKIP_SOURCE_PREFIXES，
故本次**只检测不清理**。用法：python run_audit_phb.py
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P
import _audit_books as ab

PHB = os.path.join(P.WIKI_TIDDLERS, "0 核心三宝书", "PHB玩家手册")

if __name__ == "__main__":
    st, iss = ab.audit_book(PHB)
    print("=" * 100)
    print("0 核心三宝书\\PHB玩家手册  检测（只读，不修改）")
    print("=" * 100)
    print(
        f"tid {st['tids']:>4}  可见字符 {st['chars']:>8}  图片 {st['imgs']:>3}"
        f"(缺meta {st['img_nometa']})  空正文 {st['empty']}  header缺空行 {st['no_blank']}"
    )
    detail = "  ".join(f"{k}={st['bad'][k]}" for k in ab.BAD_KEYS)
    print(
        f"噪音: {detail}  br(段落内,违规)={st['br_out']}"
        f"  br(表格内,合规)={st['br_in']}  br(列表/li内,合规)={st['br_li']}"
    )
    # 需处理 = 噪音 + 段落内 br；表格内 / li 内 br 按规范合规保留，不计入
    total = sum(st["bad"].values()) + st["br_out"]
    print()
    # 按目录汇总，便于判断是否需要分区处理
    by_dir = {}
    for k in ab.BAD_KEYS + ("br_out", "br_li"):
        for name, cnt in iss.get(k, []):
            d = os.path.dirname(name) or "(根目录)"
            e = by_dir.setdefault(d, {})
            e[k] = e.get(k, 0) + cnt
    if by_dir:
        print("按目录分布：")
        for d in sorted(by_dir):
            parts = ", ".join(f"{k}={v}" for k, v in sorted(by_dir[d].items()))
            print(f"  {d}: {parts}")
        print()
    for k in ab.BAD_KEYS + ("br_out", "br_li"):
        items = iss.get(k, [])
        if items:
            tag = "  [合规, 列/表内 br]" if k in ("br_li", "br_in") else ""
            print(f"[{k}]{tag} 共 {len(items)} 个文件：")
            for name, cnt in items[:15]:
                print(f"    {name}({cnt})")
            if len(items) > 15:
                print(f"    ...另 {len(items) - 15} 个文件")
    print("\n" + "=" * 100)
    print(
        f"合计需处理（不含表格内/li内 br）：{total} 处"
        f"  [另：表格内 br={st['br_in']}、li内 br={st['br_li']} 合规保留]"
        if total else "无噪音残留"
    )
    print("=" * 100)
