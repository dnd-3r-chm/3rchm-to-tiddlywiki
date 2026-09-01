# -*- coding: utf-8 -*-
"""清理 <p> 标签内部的多余空格和换行：
  - <p \n>          ->  <p>
  - <p  >           ->  <p>
  - <p class="x" \n> ->  <p class="x">
  - <p \n class="x"> ->  <p class="x">

规则：
  1) <p 与属性间的换行/空白：<p 换行 -> <p (保留一个空格，避免与属性粘连)
  2) 纯空白型：<p 空白 > -> <p
  3) 带属性尾随空白：<p 属性 空白> -> <p 属性>  (只去 > 前尾随空白，保留属性)

不触碰属性值内部的合法空格（如 style="font-size: 14px;"）。
跳过系统/手工页：$__*.tid / 总目录.tid / CHM目录侧边栏.tid /
        标题配色.tid / cascading_stylesheet.css.tid / 版本历史.tid
自动备份到 work/backup_ptags_时间戳/。支持 --dry。
"""
import os
import re
import sys
import datetime
import shutil

import _paths as P

WIKI = P.WIKI_TIDDLERS
SKIP_FILES = {
    "CHM目录侧边栏.tid",
    "总目录.tid",
    "标题配色.tid",
    "cascading_stylesheet.css.tid",
    "版本历史.tid",
}
# 1) <p 与属性/属性与> 间的换行 -> <p (补一个空格)
RE_NL = re.compile(r"<p\s*\n")
# 2) 纯空白型 <p  > / <p \n>
RE_PURE = re.compile(r"<p\s+>")
# 3) 带属性且 > 前有多余空白
RE_ATTR = re.compile(r"<p([^>]+?)\s+>")


def is_system(name):
    return name.startswith("$__")


def process(text):
    text = RE_NL.sub("<p ", text)
    text = RE_ATTR.sub(r"<p\1>", text)
    text = RE_PURE.sub("<p>", text)
    return text


def count(text):
    t = RE_NL.sub("<p ", text)
    t = RE_ATTR.sub(r"<p\1>", t)
    return len(RE_PURE.findall(t)) + (len(RE_ATTR.findall(t)) - 0)


def main():
    dry = "--dry" in sys.argv
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = os.path.join(P.WORK, "backup_ptags_%s" % ts)
    files = 0
    total = 0
    for dp, dn, fn in os.walk(WIKI):
        for f in fn:
            if not f.endswith(".tid"):
                continue
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, WIKI)
            if f in SKIP_FILES or is_system(f):
                continue
            try:
                text = open(full, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            new_text = process(text)
            n = len(text) - len(new_text)
            if n == 0:
                continue
            files += 1
            total += n
            if not dry:
                bdest = os.path.join(backup_root, rel)
                os.makedirs(os.path.dirname(bdest), exist_ok=True)
                shutil.copy2(full, bdest)
                with open(full, "w", encoding="utf-8") as fh:
                    fh.write(new_text)

    mode = "DRY" if dry else "WRITE"
    print("[%s] 处理文件数: %d  清理处(约): %d" % (mode, files, total))
    if not dry and files:
        print("备份目录:", backup_root)


if __name__ == "__main__":
    main()
