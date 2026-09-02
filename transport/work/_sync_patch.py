# -*- coding: utf-8 -*-
norm_tail_old = '    return body.replace("&nbsp;", " ").replace("\\r", "")'
norm_tail_new = (
    '    # 标签尖括号内多余空格/属性残留： <p > <p class="" > -> <p>\n'
    '    body = re.sub(r"<(\\w+)\\s*/?>", r"<\\1>", body, flags=re.I)\n'
    '    body = re.sub(r"<(/?\\w+)\\s+>", r"<\\1>", body, flags=re.I)\n'
    '    return body.replace("&nbsp;", " ").replace("\\r", "")'
)
collapse_fn = (
    "def collapse_ws(s):\n"
    '    """压掉标签内部的多余空白（含跨行空行），保留单空格分隔。"""\n'
    '    return re.sub(r"\\s*\\n\\s*", " ", s).strip()\n'
)
strip_tags_old = 'def strip_tags(s):\n    return re.sub(r"\\s+", " ", re.sub(r"</?[^>]+>", "", s)).strip()\n'
strip_tags_new = strip_tags_old + "\n\n" + collapse_fn

for fn in ["clean_mm4.py", "clean_mm5.py"]:
    p = "transport/work/" + fn
    t = open(p, encoding="utf-8").read()
    assert norm_tail_old in t, f"{fn}: norm_tail not found"
    t = t.replace(norm_tail_old, norm_tail_new)
    if "def collapse_ws" not in t:
        assert strip_tags_old in t, f"{fn}: strip_tags not found"
        t = t.replace(strip_tags_old, strip_tags_new)
    t = t.replace('out.append(f"<p>{txt}</p>")\n            continue',
                  'out.append(f"<p>{collapse_ws(txt)}</p>")\n            continue')
    t = t.replace("val = strip_tags(val_cell).strip()",
                  "val = collapse_ws(strip_tags(val_cell))")
    t = t.replace('combined = strip_tags(name_cell + " " + val_cell).strip()',
                  'combined = collapse_ws(strip_tags(name_cell + " " + val_cell))')
    t = t.replace('out.append(f"<p>{inner.strip()}</p>")',
                  'out.append(f"<p>{collapse_ws(inner)}</p>")')
    t = t.replace('out.append(f"<p>{plain}</p>")\n    return out',
                  'out.append(f"<p>{collapse_ws(plain)}</p>")\n    return out')
    t = t.replace('return "\\n\\n".join(c for c in chunks if c and c.strip())',
                  'return "\\n".join(c for c in chunks if c and c.strip())')
    open(p, "w", encoding="utf-8").write(t)
    print(fn, "patched OK")
