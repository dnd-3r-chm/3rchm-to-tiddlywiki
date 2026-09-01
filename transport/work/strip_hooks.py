# -*- coding: utf-8 -*-
"""Phase 2 钩子清理：移除 class / id / 指定内联 style / <o:p> / <font>，并升级伪标题为 h3。

规则（对齐已确认决策）：
  - class：全删，白名单 subhead/noindent/noidt 保留
  - id：全删
  - 内联 style：
      * MM怪物图鉴、DMG城主指南：全部删除
      * PHB玩家手册、10 附录、根目录页：仅删含 mso- 或全大写 CSS 属性名的
        （maroon 强调 / <summary> 折叠 / decimal 列表等小写属性保留）
  - <o:p> 空标签：全删
  - <font>：全库 unwrap，仅跳过 版本历史.tid；
             <p><font color=... size=4><b>x</b></font></p> -> <h3>x</h3>
  - 跳过文件：$__*.tid / 标题配色.tid / cascading_stylesheet.css.tid /
             CHM目录侧边栏.tid / 总目录.tid / 版本历史.tid（整体保留）

支持 --dry 预览与自动备份。
"""
import os
import re
import shutil
import sys
import datetime

import _paths as P

WIKI = P.WIKI_TIDDLERS
WHITELIST_CLASS = {"subhead", "noindent", "noidt"}
SKIP_FILES = {
    "CHM目录侧边栏.tid",
    "总目录.tid",
    "标题配色.tid",
    "cascading_stylesheet.css.tid",
    "版本历史.tid",
}
UPPER_PROP_RE = re.compile(r'(?:^|;)\s*[A-Z][A-Z0-9-]*\s*:')
STYLE_ATTR_RE = re.compile(r'\sstyle\s*=\s*"[^"]*"')
CLASS_ATTR_RE = re.compile(r'\sclass\s*=\s*("([^"]*)"|\'([^\']*)\'|([^\s>]+))')
ID_ATTR_RE = re.compile(r'\sid\s*=\s*("([^"]*)"|\'([^\']*)\'|([^\s>]+))')
OP_RE = re.compile(r'<o:p>\s*</o:p>|<o:p\s*[^>]*>\s*</o:p>')
FONT_RE = re.compile(r'<font[^>]*>(.*?)</font>', re.IGNORECASE | re.DOTALL)
# <p><font color=... size=4><b>xxx</b></font></p> -> <h3>xxx</h3>
PSEUDO_TITLE_RE = re.compile(
    r'<p[^>]*>\s*<font[^>]*color[^>]*size\s*=\s*["\']?\s*4\b[^>]*>\s*<b[^>]*>(.*?)</b>\s*</font>\s*</p>',
    re.IGNORECASE | re.DOTALL,
)


def is_system(name):
    return name.startswith("$__")


def book_of(rel):
    parts = rel.split(os.sep)
    if not parts:
        return "(root)"
    if parts[0] == "0 核心三宝书" and len(parts) > 1:
        return parts[1]
    return parts[0]


def style_should_clear(book, sval):
    if book in ("MM怪物图鉴", "DMG城主指南"):
        return True  # 全清
    # 其他书：仅清 mso- 或全大写属性
    return ("mso-" in sval.lower()) or bool(UPPER_PROP_RE.search(sval))


def process_body(body, book, dry=False):
    """返回 (新body, 改动数)。"""
    changed = 0

    # 1. id 全删
    new_body, n = ID_ATTR_RE.subn("", body)
    changed += n
    body = new_body

    # 2. class 删（白名单保留）；先按属性出现处理
    def class_repl(m):
        val = (m.group(2) or m.group(3) or m.group(4) or "").strip()
        keep = [c for c in val.split() if c in WHITELIST_CLASS]
        if keep:
            return ' class="%s"' % " ".join(keep)
        return ""
    new_body, n = CLASS_ATTR_RE.subn(class_repl, body)
    changed += n
    body = new_body

    # 3. style：按书+属性判定逐个删除
    def style_repl(m):
        full = m.group(0)
        sval = re.search(r'"([^"]*)"', full)
        sv = sval.group(1) if sval else ""
        if style_should_clear(book, sv):
            return ""
        return full
    new_body, n = STYLE_ATTR_RE.subn(style_repl, body)
    changed += n
    body = new_body

    # 4. <o:p> 删除
    new_body, n = OP_RE.subn("", body)
    changed += n
    body = new_body

    # 5. 伪标题 <p><font size=4 ...><b>x</b></font></p> -> <h3>x</h3>
    new_body, n = PSEUDO_TITLE_RE.subn(lambda m: "<h3>%s</h3>" % m.group(1), body)
    changed += n
    body = new_body

    # 6. <font> unwrap（保留文字）
    new_body, n = FONT_RE.subn(lambda m: m.group(1), body)
    changed += n
    body = new_body

    return body, changed


def main():
    dry = "--dry" in sys.argv
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = os.path.join(P.WORK, "backup_strip_hooks_%s" % ts)
    total_files = 0
    total_changes = 0

    for dp, dn, fn in os.walk(WIKI):
        for f in fn:
            if not f.endswith(".tid"):
                continue
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, WIKI)
            if f in SKIP_FILES or is_system(f):
                continue
            book = book_of(rel)
            text = open(full, encoding="utf-8", errors="replace").read()
            if "\n" in text:
                head, body = text.split("\n", 1)
            else:
                head, body = "", text
            new_body, n = process_body(body, book, dry)
            if n == 0:
                continue
            total_files += 1
            total_changes += n
            if not dry:
                if not os.path.exists(backup_root):
                    os.makedirs(backup_root)
                # 备份原文件（保持相对结构）
                bdest = os.path.join(backup_root, rel)
                os.makedirs(os.path.dirname(bdest), exist_ok=True)
                shutil.copy2(full, bdest)
                with open(full, "w", encoding="utf-8") as fh:
                    fh.write(head + "\n" + new_body)

    mode = "DRY" if dry else "WRITE"
    print("[%s] 处理文件数: %d  改动处: %d" % (mode, total_files, total_changes))
    if not dry and total_files:
        print("备份目录:", backup_root)


if __name__ == "__main__":
    main()
