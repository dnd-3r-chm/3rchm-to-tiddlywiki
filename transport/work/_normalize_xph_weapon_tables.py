# -*- coding: utf-8 -*-
"""将 XPH扩展灵能手册/7装备/武器.tid 内所有表格（除已清理的表7-5外）
规范为与表7-5一致的紧凑单行格式：
  <table><tr><td>内容</td>...</tr>...</table>
  - 去掉 <colgroup>/<col>/<tbody> 等死标签
  - 去掉 td 的 width 等属性
  - 去掉单元格内部 <p>/</p>（内容压平为纯文本）
  - 修复跨单元格错乱 <p>中等</td><td>高等</p></td>
  - 表格整体单行（无内部换行）

用法：
  python _normalize_xph_weapon_tables.py            # 干跑预览
  python _normalize_xph_weapon_tables.py --apply    # 写入（先自动备份）
"""
import datetime
import os
import re
import shutil
import sys

PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "wiki", "tiddlers",
    "1 核心补充书籍", "XPH扩展灵能手册", "7装备", "武器.tid"
))

TABLE_RE = re.compile(r"<table[^>]*>[\s\S]*?</table>", re.I)
CELL_RE = re.compile(r"<td[^>]*>([\s\S]*?)</td>", re.I)


def norm_table(block):
    rows = re.split(r"</?tr[^>]*>", block, flags=re.I)
    out_rows = []
    for r in rows:
        cells = CELL_RE.findall(r)
        if not cells:
            continue
        clean = [
            re.sub(r"\s+", " ", re.sub(r"</?p[^>]*>", "", c, flags=re.I)).strip()
            for c in cells
        ]
        out_rows.append("<tr>" + "".join(f"<td>{t}</td>" for t in clean) + "</tr>")
    if not out_rows:
        return block
    return "<table>" + "".join(out_rows) + "</table>"


def main():
    apply = "--apply" in sys.argv
    raw = open(PATH, encoding="utf-8").read()
    blocks = list(TABLE_RE.finditer(raw))
    print(f"发现表格 {len(blocks)} 个")
    new = raw
    for i, m in enumerate(blocks):
        orig = m.group(0)
        repl = norm_table(orig)
        if orig == repl:
            print(f"  表格[{i+1}] 无需改动")
            continue
        print(f"\n----- 表格[{i+1}] 规范化前 -----")
        print(orig[:300] + ("..." if len(orig) > 300 else ""))
        print(f"----- 表格[{i+1}] 规范化后 -----")
        print(repl[:400] + ("..." if len(repl) > 400 else ""))
        new = new.replace(orig, repl, 1)

    if not apply:
        print("\n（干跑，未写入。加 --apply 执行并自动备份）")
        return
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = PATH + f".bak_{ts}"
    shutil.copy2(PATH, bak)
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"\n已写入。备份 -> {bak}")


if __name__ == "__main__":
    main()
