#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _paths as P
import shutil, os

backup_dir = os.path.join(P.WORK, "backup_nobr_20260901_181603")
src = os.path.join(backup_dir, "魔宠手册.tid")
dst = os.path.join(P.WIKI_TIDDLERS, "10 附录", "职业心得", "魔宠手册.tid")
shutil.copy2(src, dst)
print("RESTORED:", dst)
