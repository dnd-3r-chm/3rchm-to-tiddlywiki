# -*- coding: utf-8 -*-
"""校验：全库 [[链接]] 目标是否存在（重命名后防断链）。

扫描 .tid **正文**中的 [[显示文字|目标Tiddler]] 链接，校验目标是否存在，
并输出 logs/link-report.csv（搬运计划 §4.6 交付物）。

与旧版相比的两处修正：
1. 只扫描正文，不再把头部 tags: 字段里的 [[标签]] 误当作链接统计。
2. 校验前剥离 #锚点，避免 [[标题#小节]] 被误判为失效。

用法：
    python _verify_links.py
"""
import csv
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

WIKI = r"E:\dnd3r_full\transport\wiki\tiddlers"
LOG_DIR = r"E:\dnd3r_full\transport\logs"
REPORT = os.path.join(LOG_DIR, "link-report.csv")

LINK_RE = re.compile(r"\[\[([^\[\]|]+)(?:\|([^\[\]]+))?\]\]")

# 目录/导航类 Tiddler 由 generate_toc.py 生成，其中的链接不纳入统计
NAV_TITLES = {"总目录", "CHM目录侧边栏"}

FIELDS = [
    "源文件",
    "源Tiddler标题",
    "显示文字",
    "链接目标",
    "目标Tiddler标题",
    "锚点",
    "是否失效",
]


def split_tid(content):
    """拆分 .tid 的头部字段与正文，返回 (正文, 标题)。"""
    lines = content.splitlines()
    title = ""
    body_start = len(lines)
    for i, line in enumerate(lines):
        m = re.match(r"^title:\s*(.+)$", line)
        if m and not title:
            title = m.group(1).strip()
        if line.strip() == "":
            body_start = i + 1
            break
    return "\n".join(lines[body_start:]), title


def collect_titles():
    titles = set()
    for dp, _, ns in os.walk(WIKI):
        for n in ns:
            if not n.lower().endswith(".tid"):
                continue
            with open(os.path.join(dp, n), encoding="utf-8") as f:
                head = f.read(4000)
            m = re.search(r"^title:\s*(.+)$", head, re.M)
            if m:
                titles.add(m.group(1).strip())
    return titles


def main():
    titles = collect_titles()

    rows = []
    for dp, _, ns in os.walk(WIKI):
        for n in sorted(ns):
            if not n.lower().endswith(".tid") or n.startswith("$__"):
                continue
            path = os.path.join(dp, n)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            body, src_title = split_tid(content)
            if src_title in NAV_TITLES:
                continue
            rel = os.path.relpath(path, WIKI)

            for m in LINK_RE.finditer(body):
                raw = (m.group(2) or m.group(1)).strip()
                if not raw:
                    continue
                # 语法：[[显示文字|目标Tiddler]]，目标在管道右侧
                target, _, anchor = raw.partition("#")
                target = target.strip()
                ok = target in titles
                rows.append({
                    "源文件": rel,
                    "源Tiddler标题": src_title,
                    "显示文字": m.group(1).strip() if m.group(2) else "",
                    "链接目标": raw,
                    "目标Tiddler标题": target,
                    "锚点": anchor,
                    "是否失效": "否" if ok else "是",
                })

    missing = [r for r in rows if r["是否失效"] == "是"]

    os.makedirs(LOG_DIR, exist_ok=True)
    with open(REPORT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"titles: {len(titles)}, links: {len(rows)}, missing: {len(missing)}")
    print(f"report -> {REPORT}")
    for r in missing[:50]:
        print(f"  MISSING: {r['链接目标']}  <- {r['源文件']}")
    if len(missing) > 50:
        print(f"  ... 另有 {len(missing) - 50} 条，详见 CSV")


if __name__ == "__main__":
    main()
