# -*- coding: utf-8 -*-
"""校验 XPH 搬运产物：tid 数量、图片 .meta、标题/标签完整性。"""
import _paths as P
import csv
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = P.ROOT
WIKI_TID = P.WIKI_TIDDLERS
FIN = os.path.join(P.WORK, "final_mapping.csv")

PREFIX = "1 核心补充书籍\\XPH扩展灵能手册"
XPH_WIKI = os.path.join(WIKI_TID, PREFIX)

# 1. 映射 vs 实际 tid
fin = list(csv.DictReader(open(FIN, encoding="utf-8-sig")))
sel = [r for r in fin if r["源文件相对路径"].startswith(PREFIX + "\\")]
print("映射中 XPH 行数:", len(sel))

tids = []
for dirpath, dirnames, filenames in os.walk(XPH_WIKI):
    for f in filenames:
        if f.lower().endswith(".tid"):
            tids.append(os.path.join(os.path.relpath(dirpath, XPH_WIKI), f))
print("实际生成 tid 数:", len(tids))

# 缺失检查
expect = set()
for r in sel:
    rel = r["源文件相对路径"][len(PREFIX) + 1:]
    expect.add(os.path.splitext(rel)[0] + ".tid")
missing = sorted(expect - set(tids))
print("缺失 tid:", len(missing))
for m in missing[:20]:
    print("   MISSING:", m)

# 2. 图片与 .meta
imgs, metas, no_meta = [], [], []
for dirpath, dirnames, filenames in os.walk(XPH_WIKI):
    for f in filenames:
        low = f.lower()
        full = os.path.join(dirpath, f)
        if low.endswith((".jpg", ".png", ".gif", ".jpeg")):
            imgs.append(os.path.relpath(full, XPH_WIKI))
            if os.path.isfile(full + ".meta"):
                metas.append(f)
            else:
                no_meta.append(f)
print(f"\n图片数: {len(imgs)}  有 .meta: {len(metas)}  缺 .meta: {len(no_meta)}")
for n in no_meta[:20]:
    print("   NO_META:", n)

# 3. 每个 tid 的标题/标签/正文完整性
bad = []
empty = []
for rel in tids:
    full = os.path.join(XPH_WIKI, rel)
    txt = open(full, encoding="utf-8").read()
    lines = txt.split("\n")
    title = lines[0][len("title: "):] if lines[0].startswith("title: ") else None
    tags = lines[1][len("tags: "):] if lines[1].startswith("tags: ") else None
    if not title or not title.strip():
        bad.append((rel, "无 title"))
        continue
    if "XPH-扩展灵能手册" not in title:
        bad.append((rel, f"标题缺书后缀: {title}"))
    if not tags or "XPH扩展灵能手册" not in tags:
        bad.append((rel, f"标签异常: {tags}"))
    body = "\n".join(lines[5:]).strip()
    if len(body) < 30:
        empty.append((rel, len(body)))
print("\n标题/标签异常:", len(bad))
for b in bad[:20]:
    print("   ", b)
print("正文过短(<30字符):", len(empty))
for e in empty[:20]:
    print("   ", e)

# 4. 残留噪音抽查
noise_keys = ("<script", "<style", "onclick", "<o:p", "layout-grid", "<font")
noise = {}
for rel in tids:
    body = "\n".join(open(os.path.join(XPH_WIKI, rel), encoding="utf-8").read().split("\n")[5:])
    for k in noise_keys:
        if k in body.lower():
            noise.setdefault(k, []).append(rel)
print("\n残留噪音统计:")
for k, v in noise.items():
    print(f"   {k}: {len(v)} 文件")
    for r in v[:5]:
        print("      ", r)

# 5. 图片引用是否指向已复制的图片
img_titles = {("1 核心补充书籍/XPH扩展灵能手册/" + p.replace("\\", "/")) for p in imgs}
broken_refs = []
for rel in tids:
    body = "\n".join(open(os.path.join(XPH_WIKI, rel), encoding="utf-8").read().split("\n")[5:])
    if "[img[" in body:
        for seg in body.split("[img[")[1:]:
            ref = seg.split("]")[0]
            if ref.startswith("1 核心补充书籍/XPH扩展灵能手册/") and ref not in img_titles:
                broken_refs.append((rel, ref))
print("\n断裂图片引用:", len(broken_refs))
for b in broken_refs[:20]:
    print("   ", b)
