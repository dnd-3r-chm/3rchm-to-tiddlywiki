# -*- coding: utf-8 -*-
"""只读审计：1/2/3 三类目录中表格是否遵循排版规范。

规范（2026-09-04）：
  - `<table>` 标签单起一行（独占该行）
  - `<tbody>` 标签单起一行（独占该行）；若表格无 tbody 则不补
  - 每个 `<tr>` 标签起一行（作为该行首个非空白内容；其后可接 <td>）

仅统计，不改文件。用法：python run_audit_tables.py
"""
import os
import re

sys = __import__("sys")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P

ROOTS = [
    os.path.join(P.WIKI_TIDDLERS, "1 核心补充书籍"),
    os.path.join(P.WIKI_TIDDLERS, "2 万物万法万律"),
    os.path.join(P.WIKI_TIDDLERS, "3 完美系列"),
]

TABLE_RE = re.compile(r"<table\b[^>]*>", re.I)
TBODY_RE = re.compile(r"<tbody\b[^>]*>", re.I)
TR_RE = re.compile(r"<tr\b[^>]*>", re.I)
TABLE_END_RE = re.compile(r"</table>", re.I)


def audit_tables(text):
    """返回该文件内表格的合规统计。"""
    lines = text.split("\n")
    # 预计算每个字符偏移所在行号
    line_starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(i + 1)

    def line_of(pos):
        # 二分找最后一个 <= pos 的 line_start
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo

    tables = []
    pos = 0
    while True:
        m = TABLE_RE.search(text, pos)
        if not m:
            break
        end = TABLE_END_RE.search(text, m.end())
        if not end:
            break
        region = text[m.start(): end.end()]
        # table 标签是否独占一行
        lt = line_of(m.start())
        open_tag = m.group(0).strip()
        table_alone = (lines[lt].strip() == open_tag)
        # tbody / tr 检查
        has_tbody = False
        tbody_ok = True
        tr_ok = True
        tr_count = 0
        for tm in TBODY_RE.finditer(region):
            has_tbody = True
            tl = line_of(m.start() + tm.start())
            tbody_ok = tbody_ok and (lines[tl].strip() == tm.group(0).strip())
        for trm in TR_RE.finditer(region):
            tr_count += 1
            tl = line_of(m.start() + trm.start())
            tr_ok = tr_ok and lines[tl].lstrip().lower().startswith(trm.group(0).strip().lower())
        conform = table_alone and (not has_tbody or tbody_ok) and tr_ok
        tables.append({
            "conform": conform,
            "has_tbody": has_tbody,
            "tr_count": tr_count,
        })
        pos = end.end()

    return tables


def main():
    grand = {"files_with_table": 0, "tables": 0, "conform": 0,
             "need": 0, "with_tbody": 0, "bare": 0}
    per_book = {}
    for root in ROOTS:
        for book in sorted(os.listdir(root)):
            bdir = os.path.join(root, book)
            if not os.path.isdir(bdir):
                continue
            bstat = {"files_with_table": 0, "tables": 0, "conform": 0,
                     "need": 0, "with_tbody": 0, "bare": 0}
            non_conform_files = []
            for r, dirs, fs in os.walk(bdir):
                dirs[:] = [d for d in dirs if not d.endswith(".files")]
                for x in sorted(fs):
                    if not x.lower().endswith(".tid"):
                        continue
                    p = os.path.join(r, x)
                    tables = audit_tables(open(p, encoding="utf-8").read())
                    if tables:
                        bstat["files_with_table"] += 1
                    for t in tables:
                        bstat["tables"] += 1
                        bstat["with_tbody"] += 1 if t["has_tbody"] else 0
                        bstat["bare"] += 1 if not t["has_tbody"] else 0
                        if t["conform"]:
                            bstat["conform"] += 1
                        else:
                            bstat["need"] += 1
                            rel = os.path.relpath(p, bdir)
                            if rel not in non_conform_files:
                                non_conform_files.append(rel)
            if bstat["tables"]:
                per_book[book] = (bstat, non_conform_files[:8])
                for k in grand:
                    grand[k] += bstat[k]

    print("=" * 100)
    print("表格排版规范审计（只读，不修改）  ROOTS: 1 核心补充书籍 / 2 万物万法万律 / 3 完美系列")
    print("=" * 100)
    for book, (st, examples) in per_book.items():
        print(f"\n{book}")
        print(
            f"    含表格文件 {st['files_with_table']:>3}  表格总数 {st['tables']:>4}"
            f"  已合规 {st['conform']:>4}  需重排 {st['need']:>4}"
        )
        print(
            f"    含 <tbody> 的表格 {st['with_tbody']:>4}   裸 <table>(无tbody) {st['bare']:>4}"
        )
        if examples:
            print(f"    需重排示例: {', '.join(examples)}")
    print("\n" + "=" * 100)
    print(
        f"合计: 含表格文件 {grand['files_with_table']}  表格总数 {grand['tables']}"
        f"  已合规 {grand['conform']}  需重排 {grand['need']}"
    )
    print(
        f"      其中 含<tbody> {grand['with_tbody']}   裸<table> {grand['bare']}"
    )
    print("=" * 100)


if __name__ == "__main__":
    main()
