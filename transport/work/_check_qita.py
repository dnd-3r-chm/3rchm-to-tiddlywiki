import csv, os, re

base = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
fm = os.path.join(base, "work", "final_mapping.csv")
hm = os.path.join(base, "work", "hhc_mapping.csv")

for name, p in (("final_mapping", fm), ("hhc_mapping", hm)):
    rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
    m = [r for r in rows if r.get("源文件相对路径") and any(
        k in r["源文件相对路径"] for k in ("11 其他资源", "文章与专栏", "龙晶"))]
    print(name, "total", len(rows), "matches", len(m))
    for r in m[:3]:
        print("   ", r.get("源文件相对路径"), "|", r.get("标题"))

# read one htm title/body to understand structure
f = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/11 其他资源/文章与专栏/龙晶/龙之预言.htm"
raw = open(f, encoding="gb18030", errors="replace").read()
mt = re.search(r"<title>(.*?)</title>", raw, re.I | re.S)
print("TITLE:", mt.group(1) if mt else None)
mb = re.search(r"<body[^>]*>(.*)", raw, re.I | re.S)
print("BODY head:", (mb.group(1)[:200] if mb else None))
