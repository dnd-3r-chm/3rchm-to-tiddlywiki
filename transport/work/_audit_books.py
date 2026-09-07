# -*- coding: utf-8 -*-
"""已搬运书目全量审计（只读，不修改任何文件）。

检查 1 核心补充书籍 / 2 万物万法万律 / 3 完美系列 下所有书目：
  1. 规模：tid 数、可见字符、图片数、图片缺 .meta 数
  2. 噪音分类统计（按上下文区分是否合规）：
     - word 强噪音：mso- / o:p / xml:namespace / StartFragment / WinCHM  → 一律不合规
     - 属性残留：style= / class= / lang=                                → 一律不合规
     - 弱标签：span / div / font                                        → 一律不合规
     - 空白实体：&nbsp; / &#160; / &#xa0;                               → 一律不合规
     - br（表格外）：段落内 <br>，按全库「p 内 br 改 p」规范 → 不合规
     - br（表格内）：表格/单元格内 <br>，按规范「表格内 br 暂保留」→ 合规，仅统计
  3. header 合规：tid 开头连续 `key: value` 行后应有空行（缺失说明是早期
     「固定 5 行分割」bug 写出的文件，可能导致正文首段被跳过处理）
  4. 空正文（body 无可见内容）

用法：python _audit_books.py [目录名关键字...]
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _paths as P

TARGET_ROOTS = [
    "1 核心补充书籍",
    "2 万物万法万律",
    "3 完美系列",
]

TABLE_RE = re.compile(r"<table[^>]*>.*?</table>", re.S | re.I)
# 列表容器（ul/ol/dl）：其内部（含 <li>）的 <br> 按用户规范 2026-09-04 属合法保留
LIST_RE = re.compile(r"<(?:ul|ol|dl)\b[^>]*>.*?</(?:ul|ol|dl)>", re.S | re.I)

# 噪音模式（单行正则；注意本环境 search_content 跨行不可靠，故一律用脚本统计）
PATTERNS = {
    "word": re.compile(r"mso-|<o:p|o:p>|xml:namespace|StartFragment|EndFragment|WinCHM", re.I),
    "attr": re.compile(r"style\s*=|class\s*=|lang\s*=", re.I),
    "weak": re.compile(r"<\s*span|<\s*div|</?font", re.I),
    "nbsp": re.compile(r"&nbsp;|&#0*160;|&#x0*a0;", re.I),
    "br": re.compile(r"<br", re.I),
}
# 这些类别属「一律不合规」
BAD_KEYS = ("word", "attr", "weak", "nbsp")


def split_tid(raw):
    """按 tid 规范分割 header（开头连续的 `key: value` 行）与 body。"""
    m = re.match(r"((?:[A-Za-z_][\w-]*:[^\n]*\n)+)", raw)
    if m:
        return m.group(1), raw[m.end() :]
    return "", raw


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"</?[^>]+>", "", s)).strip()


def classify_br(body):
    """把 <br> 按上下文分为三类。

    - 表格内（<table>）：按规范「表格内 br 暂保留」→ 合规
    - 列表内（<ul>/<ol>/<dl>，含 <li> 内部）：用户 2026-09-04 明确「li 内 br 是合法的」→ 合规
    - 其余（段落 <p> 内等）：违反全库「p 内 br 改 p」规范 → 不合规

    返回 (违规数, 表格内合规数, 列表内合规数)。
    """
    spans = [(m.span(), "t") for m in TABLE_RE.finditer(body)]
    spans += [(m.span(), "l") for m in LIST_RE.finditer(body)]
    bad = in_tab = in_list = 0
    for m in PATTERNS["br"].finditer(body):
        s = m.start()
        kind = next((k for (a, b), k in spans if a <= s < b), None)
        if kind == "t":
            in_tab += 1
        elif kind == "l":
            in_list += 1
        else:
            bad += 1
    return bad, in_tab, in_list


def audit_file(path):
    raw = open(path, encoding="utf-8").read()
    header, body = split_tid(raw)
    r = {
        "chars": len(re.sub(r"\s+", "", strip_tags(body))),
        "bad": {k: 0 for k in BAD_KEYS},
        "br_out": 0,   # 表格/列表外的 br —— 不合规
        "br_in": 0,    # 表格内 br —— 合规保留
        "br_li": 0,    # 列表(ul/ol/dl,含 li)内 br —— 合规保留
        "no_blank": 0, # header 后缺空行
        "empty": 0,    # 空正文
    }
    for k in BAD_KEYS:
        r["bad"][k] = len(PATTERNS[k].findall(body))
    r["br_out"], r["br_in"], r["br_li"] = classify_br(body)
    # header 后是否紧跟空行（规范）
    if not raw.startswith(header.rstrip("\n") + "\n\n") and body.strip():
        # body 非空且 header 后无空行 → 缺空行
        if not re.match(r"^\s*\n", body):
            r["no_blank"] = 1
    if not strip_tags(body):
        r["empty"] = 1
    return r


def audit_book(book_dir):
    """审计单个书目目录，返回汇总与问题明细。"""
    stat = {
        "tids": 0, "chars": 0, "imgs": 0, "img_nometa": 0, "empty": 0, "no_blank": 0,
        "bad": {k: 0 for k in BAD_KEYS}, "br_out": 0, "br_in": 0, "br_li": 0,
    }
    issues = {k: [] for k in BAD_KEYS + ("br_out", "br_li", "no_blank", "empty")}
    for root, dirs, fs in os.walk(book_dir):
        dirs[:] = [d for d in dirs if not d.endswith(".files")]
        rel = os.path.relpath(root, book_dir)
        for x in sorted(fs):
            low = x.lower()
            if low.endswith(".tid"):
                p = os.path.join(root, x)
                a = audit_file(p)
                stat["tids"] += 1
                stat["chars"] += a["chars"]
                stat["br_out"] += a["br_out"]
                stat["br_in"] += a["br_in"]
                stat["br_li"] += a["br_li"]
                stat["no_blank"] += a["no_blank"]
                stat["empty"] += a["empty"]
                for k in BAD_KEYS:
                    if a["bad"][k]:
                        stat["bad"][k] += a["bad"][k]
                        issues[k].append((os.path.join(rel, x), a["bad"][k]))
                if a["br_out"]:
                    issues["br_out"].append((os.path.join(rel, x), a["br_out"]))
                if a["br_li"]:
                    issues["br_li"].append((os.path.join(rel, x), a["br_li"]))
                if a["no_blank"]:
                    issues["no_blank"].append(os.path.join(rel, x))
                if a["empty"]:
                    issues["empty"].append(os.path.join(rel, x))
            elif low.endswith((".jpg", ".jpeg", ".png", ".gif")):
                stat["imgs"] += 1
                if not os.path.exists(os.path.join(root, x) + ".meta"):
                    stat["img_nometa"] += 1
                    issues.setdefault("img_nometa", []).append(os.path.join(rel, x))
    return stat, issues


def main():
    keys = [k.lower() for k in sys.argv[1:]]
    books = []
    for tr in TARGET_ROOTS:
        base = os.path.join(P.WIKI_TIDDLERS, tr)
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            d = os.path.join(base, name)
            if os.path.isdir(d) and (not keys or any(k in d.lower() for k in keys)):
                books.append(d)

    print("=" * 100)
    print("已搬运书目审计（只读）")
    print("=" * 100)
    grand = {"tids": 0, "chars": 0, "imgs": 0}
    problem_books = []
    for d in books:
        st, iss = audit_book(d)
        grand["tids"] += st["tids"]
        grand["chars"] += st["chars"]
        grand["imgs"] += st["imgs"]
        rel = os.path.relpath(d, P.WIKI_TIDDLERS)
        bad_total = sum(st["bad"].values()) + st["br_out"]
        flag = "OK  " if bad_total == 0 and st["img_nometa"] == 0 else "!!  "
        issues = iss
        print(f"\n{flag}{rel}")
        print(
            f"    tid {st['tids']:>4}  可见字符 {st['chars']:>8}  图片 {st['imgs']:>3}"
            f"(缺meta {st['img_nometa']})  空正文 {st['empty']}  header缺空行 {st['no_blank']}"
        )
        detail = "  ".join(f"{k}={st['bad'][k]}" for k in BAD_KEYS)
        print(
            f"    噪音: {detail}  br(段落内,违规)={st['br_out']}"
            f"  br(表格内,合规)={st['br_in']}  br(列表/li内,合规)={st['br_li']}"
        )
        if bad_total or st["img_nometa"]:
            problem_books.append((rel, st, iss))
            for k in BAD_KEYS + ("br_out",):
                if st["bad"].get(k) or (k == "br_out" and st["br_out"]):
                    items = issues.get(k, [])
                    shown = ", ".join(f"{n}({c})" for n, c in items[:6])
                    more = f" ...共{len(items)}个文件" if len(items) > 6 else ""
                    print(f"      [{k}] {shown}{more}")
            if st["img_nometa"]:
                print(f"      [图片缺meta] {', '.join(issues.get('img_nometa', [])[:6])}")

    print("\n" + "=" * 100)
    print(f"合计：{len(books)} 个书目  tid {grand['tids']}  可见字符 {grand['chars']}  图片 {grand['imgs']}")
    if problem_books:
        print(f"\n[需处理] {len(problem_books)} 个书目存在噪音/缺 meta：")
        for rel, st, _ in problem_books:
            print(f"  - {rel}")
    else:
        print("\n[OK] 全部书目无噪音残留、图片 meta 齐全")
    print("=" * 100)


if __name__ == "__main__":
    main()
