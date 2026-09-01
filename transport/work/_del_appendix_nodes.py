#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _paths as P
import shutil, os

base = P.WIKI_TIDDLERS
html_teach = os.path.join(base, "10 附录", "html教学")
how_to = os.path.join(base, "10 附录", "如何使用大不全.tid")

removed = []
if os.path.isdir(html_teach):
    shutil.rmtree(html_teach)
    removed.append(html_teach)
if os.path.isfile(how_to):
    os.remove(how_to)
    removed.append(how_to)

for p in removed:
    print("REMOVED:", p)
if not removed:
    print("无内容移除（可能已删）")
