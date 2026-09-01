#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按书/按目录批量转换 CHM HTML 到 TiddlyWiki .tid 文件。

用法：
    python convert_book.py "0 核心三宝书\\PHB玩家手册"
    python convert_book.py "0 核心三宝书"
"""
import csv
import datetime
import os
import sys

# 允许直接 import 同目录下的 convert_pilot.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import convert_pilot as cp

ROOT = cp.ROOT
WIKI_TIDDLERS = cp.WIKI_TIDDLERS
HHC_CSV = os.path.join(ROOT, "transport", "work", "hhc_mapping.csv")
FINAL_MAPPING = os.path.join(ROOT, "transport", "work", "final_mapping.csv")
LOG_DIR = os.path.join(ROOT, "transport", "logs")
LOG_FILE = os.path.join(LOG_DIR, "转换日志.log")


def log(msg):
    """追加一行到 logs/转换日志.log（搬运计划 §6 交付物）。

    与 print 的区别：print 只进 stdout，本函数持久化，便于回溯与回滚。
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

# 手动调整过的源文件，转换时一律跳过（防止重转复活被删节点 / 覆盖手动合并拆分后的版本）：
# 1) 已合并进其他节点并删除的源文件
# 2) 手动调整过（合并子节点/拆分内容）的父节点源文件——重转会覆盖手动版本
SKIP_SOURCES = {
    r"0 核心三宝书\DMG城主指南\第一章\地下城主2.htm",
    r"0 核心三宝书\DMG城主指南\第一章\设计冒险任务.htm",
    r"0 核心三宝书\DMG城主指南\第一章\自创冒险任务.htm",
    r"0 核心三宝书\DMG城主指南\第一章\使用预设冒险任务.htm",
    r"0 核心三宝书\DMG城主指南\第一章\游戏教学.htm",
    r"0 核心三宝书\DMG城主指南\第一章\创造世界.htm",
    r"0 核心三宝书\DMG城主指南\第一章\裁判.htm",
    r"0 核心三宝书\DMG城主指南\第一章\运作游戏.htm",
    r"0 核心三宝书\DMG城主指南\第一章\破门砍杀型.htm",
    r"0 核心三宝书\DMG城主指南\第一章\叙事扮演型.htm",
    r"0 核心三宝书\DMG城主指南\第一章\中间路线.htm",
    r"0 核心三宝书\DMG城主指南\第一章\其他风格.htm",
    r"0 核心三宝书\DMG城主指南\第一章\建议.htm",
    # 已合并入 "[DMG] 跑团"（第一章\跑团.htm）并删除的节点
    r"0 核心三宝书\DMG城主指南\第一章\了解玩家.htm",
    r"0 核心三宝书\DMG城主指南\第一章\即席规则.htm",
    r"0 核心三宝书\DMG城主指南\第一章\协调玩家.htm",
    r"0 核心三宝书\DMG城主指南\第一章\游戏外思考.htm",
    r"0 核心三宝书\DMG城主指南\第一章\了解玩家人物.htm",
    r"0 核心三宝书\DMG城主指南\第一章\了解冒险任务与其他资料.htm",
    r"0 核心三宝书\DMG城主指南\第一章\熟悉规则.htm",
    # 已合并入 "[DMG] 保持游戏平衡"（第一章\保持游戏平衡.htm）并删除的节点
    r"0 核心三宝书\DMG城主指南\第一章\处理不平衡的玩家人物.htm",
    # 已合并入 "[DMG] 改变规则"（第一章\改变规则.htm）并删除的节点
    r"0 核心三宝书\DMG城主指南\第一章\改得让游戏顺畅.htm",
    r"0 核心三宝书\DMG城主指南\第一章\丰富游戏.htm",
    r"0 核心三宝书\DMG城主指南\第一章\犯错.htm",
    # 已合并入 "[DMG] 布置舞台"（第一章\布置舞台.htm）并删除的节点
    r"0 核心三宝书\DMG城主指南\第一章\主持游戏所需的配备.htm",
    r"0 核心三宝书\DMG城主指南\第一章\前情提要.htm",
    r"0 核心三宝书\DMG城主指南\第一章\使用小模型.htm",
    r"0 核心三宝书\DMG城主指南\第一章\绘制地图.htm",
    r"0 核心三宝书\DMG城主指南\第一章\掌握节奏.htm",
    r"0 核心三宝书\DMG城主指南\第一章\查阅规则.htm",
    r"0 核心三宝书\DMG城主指南\第一章\发问.htm",
    r"0 核心三宝书\DMG城主指南\第一章\中场休息.htm",
    # 已合并入 "[DMG] 处理玩家人物的行动"（第一章\处理玩家人物的行动.htm）并删除的节点
    r"0 核心三宝书\DMG城主指南\第一章\处理NPC的行动.htm",
    r"0 核心三宝书\DMG城主指南\第一章\人物被魔法控制.htm",
    r"0 核心三宝书\DMG城主指南\第一章\叙述动作.htm",
    r"0 核心三宝书\DMG城主指南\第一章\NPC的动作.htm",
    r"0 核心三宝书\DMG城主指南\第一章\让战斗有趣.htm",
    # 已合并入 "更多移动规则"（第二章\更多移动规则\更多移动规则.htm）并删除的节点
    r"0 核心三宝书\DMG城主指南\第二章\更多移动规则\移动与方格.htm",
    r"0 核心三宝书\DMG城主指南\第二章\更多移动规则\移动与位置.htm",
    r"0 核心三宝书\DMG城主指南\第二章\更多移动规则\度量与方格.htm",
    r"0 核心三宝书\DMG城主指南\第二章\更多移动规则\斜向方格移动.htm",
    r"0 核心三宝书\DMG城主指南\第二章\更多移动规则\防具与负重量.htm",
    r"0 核心三宝书\DMG城主指南\第二章\更多移动规则\三维空间的移动.htm",
    r"0 核心三宝书\DMG城主指南\第二章\更多移动规则\空中战术移动.htm",
    r"0 核心三宝书\DMG城主指南\第二章\更多移动规则\逃逸与追赶.htm",
    r"0 核心三宝书\DMG城主指南\第二章\更多移动规则\方格间的活动.htm",
    # 已合并入 "战斗"（第二章\战斗\战斗.htm）并删除的节点
    r"0 核心三宝书\DMG城主指南\第二章\战斗\视线.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\遭遇开始.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\规则变化：每轮都掷先攻权.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\规则变化：聪慧的座骑.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\突袭轮.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\新加入的战斗者.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\推动游戏.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\同时行动.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\规则变化：失手时误中掩蔽物.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\战斗动作.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\判定未被定义过的新动作.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\战斗以外的战斗动作.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\规则变化：必然命中与防御检定.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\判定准备动作.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\幕后随谈：重击.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\重击.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\规则变化：依据体型定义巨创（MassiveDamage）.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\规则变化：攻击特定部位.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\规则变化：等效武器.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\伤害.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\武器大小的影响.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\投炸武器.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\规则变化：一击致死（InstantKill）.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\区域型法术.htm",
    # 已合并入 "战斗中的生物体型大小"（第二章\战斗\战斗中的生物体型大小.htm）并删除的节点
    r"0 核心三宝书\DMG城主指南\第二章\战斗\大生物.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\很小的生物.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\混合.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\挤过.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\站在狭窄之处.htm",
    # 手动调整过（合并/拆分）的父节点源文件，重转会覆盖手动版本
    r"0 核心三宝书\DMG城主指南\第一章\DM是什么？.htm",
    r"0 核心三宝书\DMG城主指南\第一章\游戏风格.htm",
    r"0 核心三宝书\DMG城主指南\第一章\简介.htm",
    r"0 核心三宝书\DMG城主指南\第一章\跑团.htm",
    r"0 核心三宝书\DMG城主指南\第一章\保持游戏平衡.htm",
    r"0 核心三宝书\DMG城主指南\第一章\改变规则.htm",
    r"0 核心三宝书\DMG城主指南\第一章\布置舞台.htm",
    r"0 核心三宝书\DMG城主指南\第一章\处理玩家人物的行动.htm",
    r"0 核心三宝书\DMG城主指南\第二章\更多移动规则\更多移动规则.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\战斗.htm",
    r"0 核心三宝书\DMG城主指南\第二章\战斗\战斗中的生物体型大小.htm",
}


def load_final_mapping():
    mapping = {}
    with open(FINAL_MAPPING, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            mapping[row["源文件相对路径"]] = row
    return mapping


def convert_book(prefix):
    prefix = prefix.replace("/", "\\")
    mapping = load_final_mapping()
    selected = [
        row for row in mapping.values()
        if row["源文件相对路径"].startswith(prefix + "\\")
    ]
    print(f"selected pages: {len(selected)}")

    os.makedirs(WIKI_TIDDLERS, exist_ok=True)
    ok = 0
    log(f"=== 开始转换：{prefix}，选中 {len(selected)} 页 ===")
    for row in selected:
        rel = row["源文件相对路径"]
        if rel in SKIP_SOURCES:
            print("SKIP(已合并):", rel)
            log(f"SKIP(已合并): {rel}")
            continue
        src_path = os.path.join(ROOT, rel)
        if not os.path.isfile(src_path):
            print("MISSING:", rel)
            log(f"MISSING(源文件不存在): {rel}")
            continue

        try:
            text = cp.read_text(src_path)
            body = cp.extract_body(text)
            body = cp.clean_html(body)
            base_rel_dir = os.path.dirname(rel) if "\\" in rel else ""
            body = cp.rewrite_images(body, base_rel_dir)
            body = cp.rewrite_links(body, mapping, base_rel_dir)

            title = row["Tiddler标题"]
            tags = row["标签"]
            source = rel.replace("\\", "/")

            tid = f"""title: {title}
tags: {tags}
source: {source}
type: text/vnd.tiddlywiki

{body}
"""
            tid_rel = os.path.splitext(rel)[0] + ".tid"
            out_path = os.path.join(WIKI_TIDDLERS, tid_rel)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(tid)
        except Exception as e:
            # 单页失败不中断整批，记录后继续
            print(f"[ERROR] {rel}: {e}")
            log(f"[ERROR] {rel}: {e}")
            continue

        ok += 1
        print(f"[OK] {title} -> {out_path}")
        log(f"[OK] {title} -> {tid_rel}")

    print(f"converted: {ok}/{len(selected)}")
    log(f"=== 完成转换：{prefix}，成功 {ok}/{len(selected)} ===")
    return ok


def build_toc(book_label, prefix):
    """从 HHC 主目录树生成一本书的目录 Tiddler。"""
    prefix = prefix.replace("/", "\\")
    with open(HHC_CSV, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    # 自动找到这本书在 HHC 主树中的根节点：
    # 根节点通常是“封面.htm”且标题形如 [XXX] 书名
    root = None
    for r in rows:
        local = (r["源文件相对路径"] or "").replace("/", "\\")
        if not local.startswith(prefix + "\\"):
            continue
        if r["标题"].startswith("[") and os.path.basename(local).lower() in ("封面.htm", "封面.html"):
            root = r
            break

    if root is None:
        # 退而求其次：取 prefix 下第一个带 [ 的节点
        for r in rows:
            local = (r["源文件相对路径"] or "").replace("/", "\\")
            if local.startswith(prefix + "\\") and r["标题"].startswith("["):
                root = r
                break

    if root is None:
        print(f"[TOC] 未找到 {book_label} 的 HHC 根节点")
        return

    root_key = root["祖先路径"] + " / " + root["标题"] if root["祖先路径"] else root["标题"]
    main_rows = [
        r for r in rows
        if r["祖先路径"] == root_key or r["祖先路径"].startswith(root_key + " / ")
    ]

    mapping = load_final_mapping()
    children = {}
    for r in main_rows:
        parent = r["祖先路径"]
        children.setdefault(parent, []).append(r)

    def node_path(r):
        if r["祖先路径"]:
            return r["祖先路径"] + " / " + r["标题"]
        return r["标题"]

    def render(parent_key, depth):
        lines = []
        for r in children.get(parent_key, []):
            title = r["标题"]
            local = r["源文件相对路径"]
            bullet = "*" * (depth + 1)
            if local:
                mapped = mapping.get(local)
                if mapped:
                    lines.append(f"{bullet} [[{title}|{mapped['Tiddler标题']}]]")
                else:
                    lines.append(f"{bullet} {title}")
            else:
                lines.append(f"{bullet} **{title}**")
            lines.extend(render(node_path(r), depth + 1))
        return lines

    toc_lines = render(root_key, 0)

    toc_title = f"{book_label} - 目录"
    toc_content = "\n".join(toc_lines) if toc_lines else "(空目录)"
    toc_tid = f"""title: {toc_title}
tags: [[0 核心三宝书]] [[{book_label}]] [[目录]]
type: text/vnd.tiddlywiki

{toc_content}
"""
    out_path = os.path.join(WIKI_TIDDLERS, prefix, f"{toc_title}.tid")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(toc_tid)
    print(f"[TOC] {toc_title} -> {out_path}")


def main():
    if len(sys.argv) > 1:
        prefix = sys.argv[1]
    else:
        prefix = r"0 核心三宝书\PHB玩家手册"

    # 根据 prefix 推断 book_label，例如 ...\PHB玩家手册 -> PHB玩家手册
    book_label = prefix.replace("/", "\\").split("\\")[-1]
    # 右侧边栏已有全局目录，不再为每本书生成“书名 - 目录”Tiddler
    convert_book(prefix)
    # build_toc(book_label, prefix)  # 已停用


if __name__ == "__main__":
    main()
