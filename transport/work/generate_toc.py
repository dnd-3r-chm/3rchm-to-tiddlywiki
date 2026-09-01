#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""根据 Contents.hhc 生成总目录 Tiddler，并添加到右侧边栏。"""
import _paths as P
import csv
import html
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = P.ROOT
HHC_CSV = os.path.join(ROOT, "transport", "work", "hhc_mapping.csv")
FINAL_MAPPING = os.path.join(ROOT, "transport", "work", "final_mapping.csv")
WIKI_TIDDLERS = os.path.join(ROOT, "transport", "wiki", "tiddlers")

# 已合并/删除，不再出现在目录中的节点
SKIP_TITLES = {
    "为何改版 (DMG-城主指南)",
    "关于边栏 (DMG-城主指南)",
    "地下城主 (DMG-城主指南)",
    "如何使用本书 (DMG-城主指南)",
    "最后 (DMG-城主指南)",
    # 已合并入 "第一章：担任地下城主 (DMG-城主指南)"（源 DM是什么？.htm）并删除的节点
    "地下城主2 (DMG-城主指南)",
    "设计冒险任务 (DMG-城主指南)",
    "自创冒险任务 (DMG-城主指南)",
    "使用预设冒险任务 (DMG-城主指南)",
    "游戏教学 (DMG-城主指南)",
    "创造世界 (DMG-城主指南)",
    "裁判 (DMG-城主指南)",
    "运作游戏 (DMG-城主指南)",
    # 已合并入 "游戏风格 (DMG-城主指南)" 并删除的节点
    "破门砍杀型 (DMG-城主指南)",
    "叙事扮演型 (DMG-城主指南)",
    "中间路线 (DMG-城主指南)",
    "其他风格 (DMG-城主指南)",
    # 已合并入 "简介 (DMG-城主指南)" 并删除的节点
    "建议 (DMG-城主指南)",
    # 已合并入 "跑团 (DMG-城主指南)" 并删除的节点
    "了解玩家 (DMG-城主指南)",
    "即席规则 (DMG-城主指南)",
    "协调玩家 (DMG-城主指南)",
    "游戏外思考 (DMG-城主指南)",
    "了解玩家人物 (DMG-城主指南)",
    "了解冒险任务与其他资料 (DMG-城主指南)",
    "熟悉规则 (DMG-城主指南)",
    # 已合并入 "保持游戏平衡 (DMG-城主指南)" 并删除的节点
    "处理不平衡的玩家人物 (DMG-城主指南)",
    # 已合并入 "改变规则 (DMG-城主指南)" 并删除的节点
    "改得让游戏顺畅 (DMG-城主指南)",
    "丰富游戏 (DMG-城主指南)",
    "犯错 (DMG-城主指南)",
    # 已合并入 "布置舞台 (DMG-城主指南)" 并删除的节点
    "主持游戏所需的配备 (DMG-城主指南)",
    "前情提要 (DMG-城主指南)",
    "使用小模型 (DMG-城主指南)",
    "绘制地图 (DMG-城主指南)",
    "掌握节奏 (DMG-城主指南)",
    "查阅规则 (DMG-城主指南)",
    "发问 (DMG-城主指南)",
    "中场休息 (DMG-城主指南)",
    # 已合并入 "处理玩家人物的行动 (DMG-城主指南)" 并删除的节点
    "处理NPC的行动 (DMG-城主指南)",
    "人物被魔法控制 (DMG-城主指南)",
    "叙述动作 (DMG-城主指南)",
    "NPC的动作 (DMG-城主指南)",
    "让战斗有趣 (DMG-城主指南)",
    # 已合并入 "更多移动规则 (DMG-城主指南)"（第二章\更多移动规则\更多移动规则.htm）并删除的节点
    "移动与方格 (DMG-城主指南)",
    "移动与位置 (DMG-城主指南)",
    "度量与方格 (DMG-城主指南)",
    "斜向方格移动 (DMG-城主指南)",
    "防具与负重量 (DMG-城主指南)",
    "三维空间的移动 (DMG-城主指南)",
    "空中战术移动 (DMG-城主指南)",
    "逃逸与追赶 (DMG-城主指南)",
    "方格间的活动 (DMG-城主指南)",
    # 已合并入 "战斗 (DMG-城主指南)"（第二章\战斗\战斗.htm）并删除的节点
    "视线 (DMG-城主指南)",
    "遭遇开始 (DMG-城主指南)",
    "规则变化：每轮都掷先攻权 (DMG-城主指南)",
    "规则变化：聪慧的座骑 (DMG-城主指南)",
    "突袭轮 (DMG-城主指南)",
    "新加入的战斗者 (DMG-城主指南)",
    "推动游戏 (DMG-城主指南)",
    "同时行动 (DMG-城主指南)",
    "规则变化：失手时误中掩蔽物 (DMG-城主指南)",
    "战斗动作 (DMG-城主指南)",
    "判定未被定义过的新动作 (DMG-城主指南)",
    "战斗以外的战斗动作 (DMG-城主指南)",
    "规则变化：必然命中与防御检定 (DMG-城主指南)",
    "判定准备动作 (DMG-城主指南)",
    "幕后随谈：重击 (DMG-城主指南)",
    "重击 (DMG-城主指南)",
    "规则变化：依据体型定义巨创(MassiveDamage) (DMG-城主指南)",
    "规则变化：攻击特定部位 (DMG-城主指南)",
    "规则变化：等效武器 (DMG-城主指南)",
    "伤害(伤害)(0 核心三宝书\\DMG城主指南\\第二章\\战斗\\伤害.htm) (DMG-城主指南)",
    "武器大小的影响 (DMG-城主指南)",
    "投炸武器 (DMG-城主指南)",
    "规则变化：一击致死(InstantKill) (DMG-城主指南)",
    "区域型法术 (DMG-城主指南)",
    # 已合并入 "战斗中的生物体型大小 (DMG-城主指南)"（第二章\战斗\战斗中的生物体型大小.htm）并删除的节点
    "大生物 (DMG-城主指南)",
    "很小的生物 (DMG-城主指南)",
    "混合 (DMG-城主指南)",
    "挤过 (DMG-城主指南)",
    "站在狭窄之处 (DMG-城主指南)",
}

# 按 hhc 标题跳过（这些节点的 Tiddler标题 与别的节点相同，无法用 SKIP_TITLES）
SKIP_HHC_TITLES = {
    # 标准度量 与 更多移动规则 同源（更多移动规则.htm），无独立内容
    "标准度量",
}

# 手动新建节点（无 hhc 源文件）：父祖先路径 -> [(label, Tiddler标题)]
MANUAL_CHILDREN = {
    # 用户从 战斗.tid 拆出 攻击.tid（战斗的下级节点）
    "核心三宝书 / [DMG] 城主指南 / 第二章：运用规则 / 战斗": [
        ("攻击", "攻击 (DMG-城主指南)"),
    ],
}


def load_mapping():
    mapping = {}
    with open(FINAL_MAPPING, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            mapping[r["源文件相对路径"]] = r
    return mapping


def collect_nonempty_titles():
    """收集 wiki/tiddlers 下所有有正文的 Tiddler 标题。"""
    titles = set()
    for dirpath, _, names in os.walk(WIKI_TIDDLERS):
        for name in names:
            if not name.lower().endswith(".tid"):
                continue
            path = os.path.join(dirpath, name)
            content = open(path, encoding="utf-8").read()
            parts = re.split(r"\r?\n\r?\n", content, maxsplit=1)
            if len(parts) != 2 or not parts[1].strip():
                continue
            m = re.search(r"^title:\s*(.+)$", parts[0], re.M)
            if m:
                titles.add(m.group(1).strip())
    return titles


def build_toc_html():
    with open(HHC_CSV, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    mapping = load_mapping()
    children = {}
    for r in rows:
        parent = r["祖先路径"]
        children.setdefault(parent, []).append(r)

    def node_path(r):
        if r["祖先路径"]:
            return r["祖先路径"] + " / " + r["标题"]
        return r["标题"]

    def render(parent_key, depth):
        chunks = []
        indent = f' style="margin-left:{depth * 0.5}em;"' if depth > 0 else ""
        for r in children.get(parent_key, []):
            title = r["标题"]
            local = r["源文件相对路径"]
            mapped = mapping.get(local) if local else None

            # 跳过已合并/删除的节点（按 Tiddler标题 或 hhc 标题）
            if mapped and mapped["Tiddler标题"] in SKIP_TITLES:
                continue
            if title in SKIP_HHC_TITLES:
                continue

            if mapped:
                # 使用 TiddlyWiki 链接语法：[[显示名|目标Tiddler]]
                label = f"[[{html.escape(title)}|{mapped['Tiddler标题']}]]"
            else:
                label = html.escape(title)

            # 不需要“卷首资料”这一层，直接把它的子级提升上来
            if not local and title == "卷首资料":
                chunks.append(render(node_path(r), depth))
                continue

            child_html = render(node_path(r), depth + 1)
            # 手动新建节点（无 hhc 源，如用户从父节点拆出的子 tiddler）
            manual = MANUAL_CHILDREN.get(node_path(r), [])
            manual_html = "\n".join(
                f'<div style="margin-left:{(depth + 1) * 0.5}em;">[[{html.escape(label)}|{title}]]</div>'
                for label, title in manual
            )
            if child_html or manual_html:
                chunks.append(
                    f"<details{indent}><summary>{label}</summary>\n{child_html}\n{manual_html}\n</details>"
                )
            else:
                chunks.append(f"<div{indent}>{label}</div>")
        return "\n".join(chunks)

    return render("", 0)


def postprocess_toc(text):
    """对生成的目录做手动同步调整：清理空 details。

    说明：DMG 简介/第一章下被合并删除的节点已全部由 SKIP_TITLES 处理，
    不再需要节点移动逻辑。
    """
    # 简介已合并为单个节点，不应再是可折叠空目录
    old_empty = '<details style="margin-left:1.0em;"><summary>[[简介|[DMG] 简介]]</summary>\n</details>'
    new_plain = '<div style="margin-left:1.0em;">[[简介|[DMG] 简介]]</div>'
    text = text.replace(old_empty, new_plain, 1)
    return text


def write_tiddler(rel_path, title, tags, body):
    out_path = os.path.join(WIKI_TIDDLERS, rel_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    content = f"""title: {title}
tags: {tags}
type: text/vnd.tiddlywiki

{body}
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] {title} -> {out_path}")


def main():
    toc_body = postprocess_toc(build_toc_html())
    print(f"TOC HTML length: {len(toc_body)}")

    # 1. 总目录 Tiddler
    write_tiddler(
        "总目录.tid",
        "总目录",
        "[[目录]]",
        toc_body or "(空目录)",
    )

    # 2. 右侧边栏“目录”标签页
    write_tiddler(
        "CHM目录侧边栏.tid",
        "CHM目录侧边栏",
        "$:/tags/SideBar",
        "{{总目录}}",
    )
    # caption 需要通过字段写入，因此单独再处理一次
    sidebar_path = os.path.join(WIKI_TIDDLERS, "CHM目录侧边栏.tid")
    with open(sidebar_path, "r", encoding="utf-8") as f:
        text = f.read()
    text = text.replace("tags: $:/tags/SideBar", "tags: $:/tags/SideBar\ncaption: 目录", 1)
    with open(sidebar_path, "w", encoding="utf-8") as f:
        f.write(text)

    # 注意：$:/tags/SideBar（标签页顺序）与 $:/DefaultTiddlers（默认首页）
    # 均为手动维护文件，本脚本不再写入/覆盖。


if __name__ == "__main__":
    main()
