# -*- coding: utf-8 -*-
"""转换 `11 其他资源` 系列（单本：文章与专栏/龙晶，38 篇平铺 htm 文章）。

流程：
1. ensure_mapping：若 final_mapping.csv 未含 `11 其他资源\\文章与专栏\\龙晶\\*.htm`，
   则扫描该目录、取每页 <title> 作为标题，生成映射行（标签 [[11 其他资源]] [[文章与专栏]]，
   标题形如 `xxx (文章与专栏)`，重名时加文件名消歧），追加进 final_mapping.csv。
   顺带把全表源路径分隔符统一规范为反斜杠（修复 `/` 与 `\\` 不一致导致 convert 选 0 的问题）。
2. convert：自包含转换循环（复用 convert_pilot 核心），按 `11 其他资源\\` 精确选中这 38 页
   （单子书，不会误吞），逐页转换写 tid。

用法：
  python run_qita.py --dry    # 仅打印选中页数
  python run_qita.py          # 正式转换
"""
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import convert_book as cb
import convert_pilot as cp

ROOT = cb.ROOT
WIKI_TIDDLERS = cb.WIKI_TIDDLERS
FM = cb.FINAL_MAPPING
SRC_DIR = os.path.join(ROOT, "11 其他资源", "文章与专栏", "龙晶")
PREFIX = "11 其他资源\\"


def ensure_mapping():
    rows = list(csv.DictReader(open(FM, encoding="utf-8-sig")))
    fieldnames = list(rows[0].keys())
    # 规范化所有行的源路径分隔符为反斜杠
    for r in rows:
        sp = r["源文件相对路径"].replace("/", "\\")
        if sp != r["源文件相对路径"]:
            r["源文件相对路径"] = sp
    existing = {r["源文件相对路径"]: r for r in rows}
    used_titles = {}
    for r in rows:
        used_titles[r["Tiddler标题"]] = used_titles.get(r["Tiddler标题"], 0) + 1

    new_count = 0
    for fn in sorted(os.listdir(SRC_DIR)):
        if not fn.lower().endswith(".htm"):
            continue
        rel = PREFIX + "文章与专栏\\龙晶\\" + fn
        if rel in existing:
            continue
        raw = cp.read_text(os.path.join(SRC_DIR, fn))
        mt = re.search(r"<title>(.*?)</title>", raw, re.I | re.S)
        base = (mt.group(1).strip() if mt else os.path.splitext(fn)[0])
        base = re.sub(r"^\[[^\]]+\]\s*", "", base).strip()
        title = f"{base} (文章与专栏)"
        if title in used_titles:
            stem = os.path.splitext(fn)[0]
            title = f"{base}({stem}) (文章与专栏)"
        used_titles[title] = used_titles.get(title, 0) + 1
        rows.append({
            "源文件相对路径": rel,
            "HHC标题": base,
            "Tiddler标题": title,
            "层级": "",
            "祖先路径": "",
            "一级": "11 其他资源",
            "二级": "文章与专栏",
            "标签": "[[11 其他资源]] [[文章与专栏]]",
            "所在目录": PREFIX + "文章与专栏\\龙晶",
        })
        new_count += 1

    with open(FM, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"mapping rows total={len(rows)} (新增 {new_count})")


def convert():
    mapping = cb.load_final_mapping()
    selected = [
        row for row in mapping.values()
        if row["源文件相对路径"].replace("/", "\\").startswith(PREFIX)
    ]
    print(f"selected pages: {len(selected)}")
    ok = 0
    for row in selected:
        rel = row["源文件相对路径"].replace("/", "\\")
        if (
            rel in cb.SKIP_SOURCES
            or any(rel.startswith(p) for p in cb.SKIP_SOURCE_PREFIXES)
            or ".files/" in rel
        ):
            print("SKIP:", rel)
            continue
        src_path = os.path.join(ROOT, rel)
        if not os.path.isfile(src_path):
            print("MISSING:", rel)
            continue
        try:
            text = cp.read_text(src_path)
            body = cp.extract_body(text)
            _parts = rel.split("\\")
            book = _parts[1] if _parts[0] == "0 核心三宝书" and len(_parts) > 1 else _parts[0]
            body = cp.clean_html(body, book)
            base_rel_dir = os.path.dirname(rel) if "\\" in rel else ""
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


def main():
    dry = "--dry" in sys.argv
    ensure_mapping()
    if dry:
        print("[dry] skip convert")
        return
    convert()


if __name__ == "__main__":
    main()
