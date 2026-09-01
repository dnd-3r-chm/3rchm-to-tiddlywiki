#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _paths as P
import shutil, os, datetime

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
dst = os.path.join(P.WORK, "backup_del_appendix_%s" % ts)
os.makedirs(dst, exist_ok=True)

# 备份整个 10 附录
src_appendix = os.path.join(P.WIKI_TIDDLERS, "10 附录")
shutil.copytree(src_appendix, os.path.join(dst, "10 附录"))

# 备份根目录导航文件
for name in ["总目录.tid", "CHM目录侧边栏.tid"]:
    p = os.path.join(P.WIKI_TIDDLERS, name)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(dst, name))

print("BACKUP OK ->", dst)
