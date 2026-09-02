# -*- coding: utf-8 -*-
"""将 XPH扩展灵能手册/7装备 目录下（除 武器.tid 已清理）所有节点的表格
规范为与武器.tid 表7-5一致的紧凑格式：
  <table><tr><td>内容</td>...</tr>...</table>
  - <table>/<tr> 去全部属性
  - <td> 仅保留 rowspan/colspan，去除 width/height/vAlign 等死属性
  - 去除 <colgroup>/<col>/<tbody>
  - 单元格内 <p>...</p> 去标签，内容压平为单空格分隔
  - 整块折叠为单行
内容丢失自检：去标签后字符数对比（normalize 前后）。
"""
import datetime
import os
import re
import shutil
import sys

D = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport/wiki/tiddlers/1 核心补充书籍/XPH扩展灵能手册/7装备"
SKIP = {"武器.tid"}
TABLE_RE = re.compile(r"<table[^>]*>.*?</table>", re.S | re.I)
COLGRP_RE = re.compile(r"<colgroup>.*?</colgroup>", re.S | re.I)
TBODY_RE = re.compile(r"</?tbody[^>]*>", re.I)
P_RE = re.compile(r"</?p[^>]*>", re.I)
TR_RE = re.compile(r"<tr\b[^>]*>", re.I)
TABLE_OPEN_RE = re.compile(r"<table\b[^>]*>", re.I)
TD_OPEN_RE = re.compile(r"<td\b([^>]*)>", re.I)
SPAN_RE = re.compile(r"(colspan|rowspan)\s*=\s*[\"']?\d+[\"']?", re.I)


def strip_inner_p(block):
    """去除单元格内 <p> 标签并将内容压平（保留跨标签内部文本）。"""
    # 先去掉 <p ...> 和 </p>
    return P_RE.sub("", block)


def norm_td(m):
    attrs = m.group(1)
    spans = SPAN_RE.findall(attrs)
    # SPAN_RE 只取名字，需要完整属性串；重写：
    kept = []
    for sm in SPAN_RE.finditer(attrs):
        kept.append(sm.group(0))
    if kept:
        return "<td " + " ".join(kept) + ">"
    return "<td>"


def norm_table(block):
    b = COLGRP_RE.sub("", block)
    b = TBODY_RE.sub("", b)
    b = TABLE_OPEN_RE.sub("<table>", b)
    b = TR_RE.sub("<tr>", b)
    b = TD_OPEN_RE.sub(norm_td, b)
    b = strip_inner_p(b)
    # 折叠空白为单行：先按标签切，保留标签，压内容
    # 简单做法：去掉所有换行，再将标签间空白压为无（td内容已无p标签）
    b = b.replace("\n", " ")
    # 去除标签之间的多余空格： <td> 内容 </td> -> <td>内容</td>
    b = re.sub(r">\s+<", "><", b)
    # td 内容内多空格压为单空格
    b = b.strip()
    # 去除 <td> 内容与标签之间的前导/尾随空格：<td> 内容</td> -> <td>内容</td>
    b = re.sub(r"<td([^>]*)>\s+", r"<td\1>", b)
    b = re.sub(r"\s+</td>", "</td>", b)
    # 全局压缩连续空格（含 &nbsp; 残留、对齐空格、<br> 后多余空格）
    b = re.sub(r"\s{2,}", " ", b)
    return b


def char_count(s):
    return len(re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", s)))


def main():
    apply = "--apply" in sys.argv
    files = sorted(f for f in os.listdir(D) if f.endswith(".tid") and f not in SKIP)
    total_changed = 0
    lost = []
    for f in files:
        p = os.path.join(D, f)
        raw = open(p, encoding="utf-8").read()
        blocks = list(TABLE_RE.finditer(raw))
        if not blocks:
            continue
        new = raw
        file_changed = 0
        for m in blocks:
            orig = m.group(0)
            # 内容丢失自检
            before = char_count(orig)
            repl = norm_table(orig)
            after = char_count(repl)
            if orig != repl:
                file_changed += 1
                new = new.replace(orig, repl, 1)
            if before != after:
                lost.append((f, before, after))
        if file_changed:
            total_changed += 1
            if apply:
                with open(os.path.join(D, f), "w", encoding="utf-8") as fh:
                    fh.write(new)
                print(f"[OK ] {f}  修改 {file_changed} 个表格")
            else:
                print(f"[DRY] {f}  将修改 {file_changed} 个表格")
    if lost:
        print("\n[!! 内容字符数变化] " + "; ".join(f"{f} {b}->{a}" for f, b, a in lost))
    else:
        print("\n[自检] 所有表格可见字符数前后一致，无内容丢失")
    if apply:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = os.path.join(D, f"_bak_tables_{ts}")
        os.makedirs(bak, exist_ok=True)
        for f in files:
            p = os.path.join(D, f)
            if TABLE_RE.search(open(p, encoding="utf-8").read()):
                shutil.copy2(p, os.path.join(bak, f))
        print(f"备份目录 -> {bak}")
    else:
        print("\n（干跑，未写入。加 --apply 执行并自动备份）")


if __name__ == "__main__":
    main()
