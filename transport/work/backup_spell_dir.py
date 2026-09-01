#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _paths as P
import shutil, os, datetime

src = os.path.join(P.WIKI_TIDDLERS, "0 核心三宝书", "PHB玩家手册", "11法术", "法术描述")
dst = src + "_backup_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(src, dst)
print("BACKUP OK ->", dst)
