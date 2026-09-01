# -*- coding: utf-8 -*-
"""将全库 .tid 中的 &#9; (Tab 实体) 统一替换为空格。

规则（对齐用户决定）：
  - &#9; -> 单个空格 " "
  - 跳过系统/手工页：$__*.tid / 总目录.tid / CHM目录侧边栏.tid /
             标题配色.tid / cascading_stylesheet.css.tid / 版本历史.tid
  - 自动备份改动文件到 work/backup_tab_时间戳/

支持 --dry 预览。
"""
import os
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


def is_system(name):
    return name.startswith("$__")


def main():
    dry = "--dry" in sys.argv
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = os.path.join(P.WORK, "backup_tab_%s" % ts)
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
            n = text.count("&#9;")
            if n == 0:
                continue
            files += 1
            total += n
            if not dry:
                bdest = os.path.join(backup_root, rel)
                os.makedirs(os.path.dirname(bdest), exist_ok=True)
                shutil.copy2(full, bdest)
                new_text = text.replace("&#9;", " ")
                with open(full, "w", encoding="utf-8") as fh:
                    fh.write(new_text)

    mode = "DRY" if dry else "WRITE"
    print("[%s] 处理文件数: %d  替换处: %d" % (mode, files, total))
    if not dry and files:
        print("备份目录:", backup_root)


if __name__ == "__main__":
    main()
