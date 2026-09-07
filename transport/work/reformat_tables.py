# -*- coding: utf-8 -*-
"""表格排版重排（2026-09-04 规范）。

规范：
  - `<table>` 标签单起一行
  - `<tbody>` 标签单起一行（**仅当表格已有时**；不主动补 `<tbody>`）
  - 每个 `<tr>` 标签起一行；`<td>`/`<th>` 保持内联
  - `<thead>`/`<tfoot>` 同样分行（罕见，避免与 <tr> 粘连）
  - **只调整表格结构标签的换行，不剥离任何标签、不改动内容、不补 tbody**

安全设计（复用 clean_residual.py 思路）：
  - split_tid 分割 header/body，保留 tid 头部 4 行 metadata
  - 字符丢失自检：去标签 + 去所有空白后比对前后可见字符（纯换行改动必相等），
    异常文件跳过不写入（宁可不改也不错改）
  - --apply 前自动备份到 work/backup_tables_<时间戳>

用法：
  python reformat_tables.py            # 干跑
  python reformat_tables.py --apply    # 实际写入（先自动备份）
"""
import datetime
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P

ROOTS = [
    os.path.join(P.WIKI_TIDDLERS, "1 核心补充书籍"),
    os.path.join(P.WIKI_TIDDLERS, "2 万物万法万律"),
    os.path.join(P.WIKI_TIDDLERS, "3 完美系列"),
]
WORK = P.WORK
WIKI = P.WIKI_TIDDLERS

# 结构标签：仅当标签确实“粘连”在同一行内容中时才插入换行
#  - 开标签：前面是非空白字符（即与前面内容同行）才换行
STRUCT_OPEN = re.compile(r"(?<=\S)(<(?:table|thead|tbody|tfoot|tr)\b)", re.I)
#  - 闭标签：后面不是换行时才补换行
STRUCT_CLOSE = re.compile(r"(</(?:tr|thead|tbody|tfoot|table)>)(?!\n)", re.I)


def split_tid(raw):
    """按 tid 规范分割 header（开头连续的 `key: value` 行）与 body。"""
    m = re.match(r"((?:[A-Za-z_][\w-]*:[^\n]*\n)+)", raw)
    if m:
        return m.group(1), raw[m.end():]
    return "", raw


def strip_ws(s):
    """去标签 + 去所有空白，用于字符丢失自检。"""
    return re.sub(r"\s+", "", re.sub(r"</?[^>]+>", "", s))


def find_tables(text):
    """返回所有顶层 <table>...</table> 块的 (start, end)。

    支持嵌套：只取顶层；并且容忍**残缺表格**（WinCHM 导出常见：
    有 <table> 开标签但缺对应的 </table> 闭标签）——到文末仍未闭合的
    表格按「延伸到文本末尾」处理。重排只在标签边界插换行，不会删内容，
    故超出真实表格边界也安全。
    """
    results, stack = [], []
    for m in re.finditer(r"</?table\b", text, re.I):
        if m.group(0).lower() == "<table":
            stack.append(m.start())
        else:  # </table>
            if stack:
                start = stack[0]  # 顶层开标签位置（仍在栈中）
                stack.pop()
                if not stack:  # 顶层闭合完成
                    results.append((start, m.end()))
    if stack:  # 残缺：有未闭合的 <table>，延伸到文末
        results.append((stack[0], len(text)))
    return results


def reformat_one_table(blk):
    """对单个表格块重排结构标签换行（含内部嵌套表的标签一并处理）。

    仅当标签粘连同行才插入换行；已合规（每个标签已独占一行）的表格
    经此函数后字节不变，从而被后续「全等比较」判为跳过。
    """
    s = STRUCT_OPEN.sub(r"\n\1", blk)
    s = STRUCT_CLOSE.sub(r"\1\n", s)
    return s


def reformat_tables(text):
    """只重排表格块结构换行，绝不改动表格外内容。"""
    out = text
    for s, e in sorted(find_tables(text), reverse=True):
        blk = out[s:e]
        out = out[:s] + reformat_one_table(blk) + out[e:]
    return out


def walk_tids(book_dir):
    for root, dirs, fs in os.walk(book_dir):
        dirs[:] = [d for d in dirs if not d.endswith(".files")]
        for x in sorted(fs):
            if x.lower().endswith(".tid"):
                yield os.path.join(root, x)


def process(book_dirs, apply=False):
    stats = {"files": 0, "changed": 0, "skipped": 0, "tb": 0, "ta": 0}
    lost, per_book = [], {}
    for bdir in book_dirs:
        if not os.path.isdir(bdir):
            continue
        name = os.path.relpath(bdir, WIKI)
        bs = {"files": 0, "changed": 0}
        for path in walk_tids(bdir):
            raw = open(path, encoding="utf-8").read()
            header, body = split_tid(raw)
            stats["files"] += 1
            bs["files"] += 1
            new_body = reformat_tables(body)
            tb = strip_ws(body)
            ta = strip_ws(new_body)
            stats["tb"] += len(tb)
            stats["ta"] += len(ta)
            if ta != tb:
                lost.append((os.path.relpath(path, WIKI), len(tb), len(ta)))
                continue  # 字符不一致，异常跳过不写入
            if new_body == body:  # 已合规（含表格结构无变化），跳过
                stats["skipped"] += 1
                continue
            bs["changed"] += 1
            stats["changed"] += 1
            if apply:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(header.rstrip("\n") + "\n\n" + new_body.strip() + "\n")
        if bs["changed"]:
            per_book[name] = bs
    return stats, lost, per_book


def backup(book_dirs):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = os.path.join(WORK, f"backup_tables_{ts}")
    os.makedirs(bak, exist_ok=True)
    for bdir in book_dirs:
        if not os.path.isdir(bdir):
            continue
        for path in walk_tids(bdir):
            rel = os.path.relpath(path, WIKI)
            d2 = os.path.join(bak, os.path.dirname(rel))
            os.makedirs(d2, exist_ok=True)
            shutil.copy2(path, os.path.join(bak, rel))
    return bak


def collect_books(roots):
    books = []
    for tr in roots:
        base = os.path.join(WIKI, tr)
        if not os.path.isdir(base):
            continue
        for nm in sorted(os.listdir(base)):
            d = os.path.join(base, nm)
            if os.path.isdir(d):
                books.append(d)
    return books


def run(book_dirs, apply=False):
    if apply:
        print(f"[备份] -> {backup(book_dirs)}\n")
    stats, lost, per_book = process(book_dirs, apply=apply)
    print(
        f"文件 {stats['files']}  修改 {stats['changed']}  "
        f"跳过(已合规) {stats['skipped']}"
    )
    print(f"可见字符(去空白比对) {stats['tb']} -> {stats['ta']}")
    if lost:
        print(f"\n[!! 字符数异常，已跳过 {len(lost)} 个文件]")
        for f, b, a in lost[:10]:
            print(f"    {f}  {b} -> {a}")
    print()
    for name, bs in per_book.items():
        print(f"  {name}: 修改 {bs['changed']}/{bs['files']}")
    if not apply:
        print("\n（干跑，未写入。加 --apply 执行并自动备份）")


def main():
    apply = "--apply" in sys.argv
    run(collect_books(ROOTS), apply=apply)


if __name__ == "__main__":
    main()
