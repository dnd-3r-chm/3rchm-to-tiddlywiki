# -*- coding: utf-8 -*-
"""合并相邻的同标签闭合+开启边界为单个连续区间：
  - </b><b>  ->  ""  （相邻加粗边界合并，连续加粗）
  - </i><i>  ->  ""  （相邻斜体边界合并，连续斜体）

规则（对齐用户决定）：
  - 仅合并非交叉嵌套：
      </b><b> 跳过前后为 <i> 的情况（避免 i/b 交叉）
      </i><i> 跳过前后为 <b> 的情况（避免 b/i 交叉）
  - 跳过系统/手工页：$__*.tid / 总目录.tid / CHM目录侧边栏.tid /
             标题配色.tid / cascading_stylesheet.css.tid / 版本历史.tid
  - 自动备份改动文件到 work/backup_btags_时间戳/

支持 --dry 预览。
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
# 安全合并：仅当相邻不是对方标签时合并，避免交叉嵌套
B_RE = re.compile(r"(?<!</i>)</b><b>(?!<i>)")
I_RE = re.compile(r"(?<!</b>)</i><i>(?!<b>)")


def is_system(name):
    return name.startswith("$__")


def process(text):
    new = B_RE.sub("", text)
    new = I_RE.sub("", new)
    return new


def count(text):
    return len(B_RE.findall(text)) + len(I_RE.findall(text))


def main():
    dry = "--dry" in sys.argv
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = os.path.join(P.WORK, "backup_btags_%s" % ts)
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
            n = count(text)
            if n == 0:
                continue
            new_text = process(text)
            files += 1
            total += n
            if not dry:
                bdest = os.path.join(backup_root, rel)
                os.makedirs(os.path.dirname(bdest), exist_ok=True)
                shutil.copy2(full, bdest)
                with open(full, "w", encoding="utf-8") as fh:
                    fh.write(new_text)

    mode = "DRY" if dry else "WRITE"
    print("[%s] 处理文件数: %d  合并处: %d" % (mode, files, total))
    if not dry and files:
        print("备份目录:", backup_root)


if __name__ == "__main__":
    main()
