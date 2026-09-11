# -*- coding: utf-8 -*-
# 清理 CC 目录 .tid 中的 HTML 实体噪音(Word 智能标点等)，幂等。
import os, re, shutil, datetime, collections

BASE = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
SRC = os.path.join(BASE, r"wiki\tiddlers\3 完美系列\CC完美斗士")
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BAK = os.path.join(BASE, "backups", "cc_entities_" + ts)

MAP = {
    '&#8220;': '\u201c', '&#8221;': '\u201d', '&#8222;': '\u201e',
    '&#8216;': '\u2018', '&#8217;': '\u2019',
    '&#8211;': '\u2013', '&#8212;': '\u2014', '&#8230;': '\u2026',
    '&quot;': '"', '&#39;': "'",
}

entity_re = re.compile(r'&[a-zA-Z#][a-zA-Z0-9#]*;')

shutil.copytree(SRC, BAK)
print("backup ->", BAK)

total_changed = 0
for root, _, files in os.walk(SRC):
    for f in files:
        if not f.endswith(".tid"):
            continue
        p = os.path.join(root, f)
        with open(p, "r", encoding="utf-8") as fh:
            orig = fh.read()
        all_entities = entity_re.findall(orig)
        uncovered = [e for e in all_entities if e not in MAP]
        new = orig
        for ent, ch in MAP.items():
            if ent in new:
                new = new.replace(ent, ch)
        if new != orig:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
            total_changed += 1
            rel = os.path.relpath(p, SRC)
            uc = collections.Counter(uncovered)
            print("fixed: %s" % rel)
            if uc:
                print("  未覆盖实体(需人工确认): %s" % dict(uc))
print("total fixed:", total_changed)
