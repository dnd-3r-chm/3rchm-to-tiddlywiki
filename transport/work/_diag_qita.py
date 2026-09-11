import csv, os

base = r"d:/Users/v_jrchchen/Documents/3rchm-to-tiddlywiki/transport"
fm = os.path.join(base, "work", "final_mapping.csv")
hm = os.path.join(base, "work", "hhc_mapping.csv")

for name, p in (("final_mapping", fm), ("hhc_mapping", hm)):
    rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
    m = [r for r in rows if "11 其他资源" in r.get("源文件相对路径", "")]
    print(f"[{name}] total={len(rows)} matches={len(m)}")
    for r in m[:4]:
        rel = r["源文件相对路径"]
        print("   ", repr(rel),
              "bs:", rel.startswith("11 其他资源\\"),
              "fs:", rel.startswith("11 其他资源/"))
    if m:
        print("   sample tags:", m[0].get("标签"), "| title:", m[0].get("Tiddler标题"))
