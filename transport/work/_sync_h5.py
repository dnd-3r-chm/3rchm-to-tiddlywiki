# -*- coding: utf-8 -*-
old = (
    "    base = filename[:-4] if filename.lower().endswith(\".tid\") else filename\n"
    "    fm = re.match(r\"^([A-Za-z][\\w\\s'\\-,\\./]*?)\\s+([\\u4e00-\\u9fff·]+.*)$\", base)\n"
    "    if fm:\n"
    "        return f\"<h5>{fm.group(2)}({fm.group(1).strip()})</h5>\"\n"
    "    fc = re.match(r\"^([\\u4e00-\\u9fff·]+)[（(]([^）)]*)[）)]\", base)\n"
    "    if fc:\n"
    "        return f\"<h5>{fc.group(1)}({fc.group(2)})</h5>\"\n"
    "    return f\"<h5>{base}</h5>\"\n"
)
new = (
    "    base = filename[:-4] if filename.lower().endswith(\".tid\") else filename\n"
    "    fm = re.match(r\"^([A-Za-z][\\w\\s'\\-,\\./]*?)\\s+([\\u4e00-\\u9fff·]+.*)$\", base)\n"
    "    if fm:\n"
    "        h = f\"<h5>{fm.group(2)}({fm.group(1).strip()})</h5>\"\n"
    "    else:\n"
    "        fc = re.match(r\"^([\\u4e00-\\u9fff·]+)[（(]([^）)]*)[）)]\", base)\n"
    "        if fc:\n"
    "            h = f\"<h5>{fc.group(1)}({fc.group(2)})</h5>\"\n"
    "        else:\n"
    "            h = f\"<h5>{base}</h5>\"\n"
    "    # 全角括号统一转半角（遵守 tid 内禁全角（）规则）\n"
    "    return h.replace(\"（\", \"(\").replace(\"）\", \")\")\n"
)
for fn in ["clean_mm4.py", "clean_mm5.py"]:
    p = "transport/work/" + fn
    t = open(p, encoding="utf-8").read()
    assert old in t, f"{fn}: make_title_h5 not found"
    t = t.replace(old, new)
    open(p, "w", encoding="utf-8").write(t)
    print(fn, "synced")
