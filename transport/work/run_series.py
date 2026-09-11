# -*- coding: utf-8 -*-
"""一次性转换 6 种族书 / 7 扩展全新体系 / 9 世设 三系列（46 本，约 2778 页）。

从 final_mapping 提取每本书的「精确 source 列表」分组，复用 convert_book 核心逻辑逐页转换。
不使用 convert_book(prefix) 的 startswith 筛选——9 世设存在 depth-2 前缀（如 9 世设\FR、
9 世设\灰鹰）会误吞其下全部子书，故改为按分组精确逐页转换。

封面.htm / 新建主题.htm 等默认文件名页均含真实内容（标题取自 HHC，tid 标题正确），统一转换。

用法：
  python run_series.py --dry     # 仅打印每本书选中页数 + MISSING，不写文件
  python run_series.py           # 正式转换
"""
import csv
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
import convert_book as cb
import convert_pilot as cp

ROOT = cb.ROOT
WIKI_TIDDLERS = cb.WIKI_TIDDLERS
SERIES = ["6 种族书", "7 扩展全新体系", "9 世设"]


def book_key_of(src):
    parts = src.split("\\")
    parts_dir = parts[:-1]
    top = parts[0]
    if top == "9 世设":
        if len(parts_dir) >= 3:
            return "\\".join(parts_dir[:3])
        return "\\".join(parts_dir[:2])
    return "\\".join(parts_dir[:2])


def main():
    dry = "--dry" in sys.argv
    mapping = cb.load_final_mapping()
    groups = {}
    with open(cb.FINAL_MAPPING, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            src = row["源文件相对路径"]
            top = src.split("\\")[0]
            if top not in SERIES:
                continue
            groups.setdefault(book_key_of(src), []).append(row)

    total_ok = total_sel = 0
    missing = []
    for bk in sorted(groups):
        rows = groups[bk]
        selected = []
        for row in rows:
            rel = row["源文件相对路径"]
            if (
                rel in cb.SKIP_SOURCES
                or any(rel.startswith(p) for p in cb.SKIP_SOURCE_PREFIXES)
                or ".files/" in rel
            ):
                print("SKIP:", rel)
                continue
            selected.append(row)
        if not selected:
            continue
        total_sel += len(selected)
        print(f"\n=== {bk} 选中 {len(selected)} 页（共 {len(rows)}） ===")
        ok = 0
        for row in selected:
            rel = row["源文件相对路径"]
            src_path = os.path.join(ROOT, rel.replace("/", "\\"))
            if not os.path.isfile(src_path):
                print("MISSING:", rel)
                missing.append(rel)
                continue
            if dry:
                ok += 1
                continue
            try:
                text = cp.read_text(src_path)
                body = cp.extract_body(text)
                _parts = rel.split("\\")
                book = _parts[1] if _parts[0] == "0 核心三宝书" and len(_parts) > 1 else _parts[0]
                body = cp.clean_html(body, book)
                base_rel_dir = os.path.dirname(rel).replace("/", "\\") if "\\" in rel else ""
                body = cp.rewrite_images(body, base_rel_dir)
                body = cp.rewrite_links(body, mapping, base_rel_dir)
                title = row["Tiddler标题"]
                tags = row["标签"]
                source = rel.replace("\\", "/")
                tid = (
                    f"title: {title}\n"
                    f"tags: {tags}\n"
                    f"source: {source}\n"
                    f"type: text/vnd.tiddlywiki\n\n"
                    f"{body}\n"
                )
                tid_rel = os.path.splitext(rel)[0] + ".tid"
                out_path = os.path.join(WIKI_TIDDLERS, tid_rel)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "w", encoding="utf-8") as fh:
                    fh.write(tid)
                ok += 1
            except Exception as e:
                print(f"[ERROR] {rel}: {e}")
                continue
        print(f"converted: {ok}/{len(selected)}")
        total_ok += ok
    print(f"\n总计：选中 {total_sel} 页，成功 {total_ok} 页，共 {len(groups)} 本书")
    if missing:
        print(f"[MISSING] {len(missing)} 个源文件不存在（见上）")


if __name__ == "__main__":
    main()
