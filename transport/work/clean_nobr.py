#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""移除指定节点内的 <br> 标签（用户要求：魔宠手册.tid 不要使用 <br>）。

策略：将 <br> / <br/> / <br /> 全部替换为空格，使相邻文字不粘连；
随后折叠多余空白（多个空格/换行合并为单空格），保留 <b>/<del> 等结构与全部文字。
严格保留 .tid 头部 4 行 metadata。运行前备份该文件。

用法：python clean_nobr.py [--dry] [相对 10附录 的文件名，默认 职业心得/魔宠手册.tid]
"""
import os
import re
import sys
import datetime
import shutil

import _paths as P

BASE = os.path.join(P.WIKI_TIDDLERS, "10 附录")
DEFAULT = os.path.join("职业心得", "魔宠手册.tid")

RE_BR = re.compile(r"<br\s*/?>", re.IGNORECASE)


def split_tid(content):
    m = re.match(r"^(title:.*\n tags:.*\n source:.*\n type:[^\n]*\n\n)", content, re.DOTALL)
    if m:
        return m.group(1), content[m.end():]
    parts = content.split("\n\n", 1)
    if len(parts) == 2:
        return parts[0] + "\n\n", parts[1]
    return content, ""


def process(body):
    body = RE_BR.sub(" ", body)
    # 折叠由 br 替换产生的多余空格与已有空白
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n[ \t]+", "\n", body)
    body = re.sub(r"[ \t]+\n", "\n", body)
    return body


def main():
    args = [a for a in sys.argv[1:] if a != "--dry"]
    dry = "--dry" in sys.argv
    rel = args[0] if args else DEFAULT
    full = os.path.join(BASE, rel)

    text = open(full, encoding="utf-8", errors="replace").read()
    header, body = split_tid(text)
    n_br = len(RE_BR.findall(body))
    if n_br == 0:
        print("无 <br>，无需处理:", rel)
        return
    new_body = process(body)
    new_body = re.sub(r"\n{3,}", "\n\n", new_body).strip()

    if dry:
        print("===== DRY:", rel, "(br=%d)" % n_br, "=====")
        # 打印首段替换效果示例
        print(new_body[:600])
        return

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = os.path.join(P.WORK, "backup_nobr_%s" % ts)
    os.makedirs(backup, exist_ok=True)
    shutil.copy2(full, os.path.join(backup, os.path.basename(full)))
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(header + new_body + "\n")
    print("CLEANED:", rel, "移除 <br> 数:", n_br, " 备份:", backup)


if __name__ == "__main__":
    main()
