#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理 10 附录/职业心得/精华法术指南.tid 中残余的 <u1:P> 损坏标签。

<u1:P> 是 Word 命名空间(urn:schemas-microsoft-com:office:word)段落标记的损坏残留，
均为无内容的空标签（如 <p>文字<u1:P></p> / <p>文字<u1:P> </p>），直接删除即可。

规则：
  1) 删除所有 <u1:P>、<u1:p>、</u1:P>、</u1:p> 及其自闭合变体（不区分大小写）。
  2) 严格保留 .tid 头部 4 行 metadata（title/tags/source/type）。
  3) 运行前备份。
范围：d:/.../wiki/tiddlers/10 附录（含子目录，仅精华法术指南.tid 命中）
支持 --dry 预览。
"""
import os
import re
import sys
import datetime
import shutil

import _paths as P

BASE = os.path.join(P.WIKI_TIDDLERS, "10 附录")
RE_U1P = re.compile(r"</?u1:[Pp]\b[^>]*>", re.IGNORECASE)

SKIP_FILES = set()


def split_tid(content):
    m = re.match(r"^(title:.*\n tags:.*\n source:.*\n type:[^\n]*\n\n)", content, re.DOTALL)
    if m:
        return m.group(1), content[m.end():]
    parts = content.split("\n\n", 1)
    if len(parts) == 2:
        return parts[0] + "\n\n", parts[1]
    return content, ""


def process(body):
    return RE_U1P.sub("", body)


def main():
    dry = "--dry" in sys.argv
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = os.path.join(P.WORK, "backup_u1p_%s" % ts)
    files = 0
    total = 0
    for dp, dn, fn in os.walk(BASE):
        for f in fn:
            if not f.endswith(".tid"):
                continue
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, BASE)
            if rel in SKIP_FILES:
                continue
            text = open(full, encoding="utf-8", errors="replace").read()
            header, body = split_tid(text)
            n = len(RE_U1P.findall(body))
            if n == 0:
                continue
            new_body = process(body)
            new_body = re.sub(r"\n{3,}", "\n\n", new_body).strip()
            total += n
            files += 1
            if dry:
                print("===== DRY:", rel, "(u1:P=%d)" % n, "=====")
                continue
            bdest = os.path.join(backup_root, rel)
            os.makedirs(os.path.dirname(bdest), exist_ok=True)
            shutil.copy2(full, bdest)
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(header + new_body + "\n")

    mode = "DRY" if dry else "WRITE"
    print("[%s] 处理文件数: %d  移除 <u1:P> 标签总数: %d" % (mode, files, total))
    if not dry and files:
        print("备份目录:", backup_root)


if __name__ == "__main__":
    main()
