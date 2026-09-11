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
    # 10 附录 已删除/已还原/已重排的源文件（2026-09-01 用户要求排除在自动搬运外）
    # 已还原节点（重转会覆盖手动排版版本）：
    r"10 附录\如何使用大不全.htm",
    # 已删除节点（源 htm 仍存在，重转会复活已删 tid）：
    r"10 附录\如何为扩展大全做出贡献.htm",
    r"10 附录\html教学\开始之前.htm",
    r"10 附录\html教学\标签与格式.htm",
}

# 已手动清洗/调整、重转会覆盖的整目录前缀（不仅是合并节点）
# 注意：convert_book 按"源文件相对路径"跳过，前缀需与 final_mapping.csv 的分隔符(\\)一致
# 规则（2026-09-02 用户明确）：任何「经过处理的书目」一律加入 SKIP 列表，
# 无论是否做过结构化重排。目的：防止日后对某目录全量重转时，用原始 CHM/Word
# 覆盖已搬运/已排版的 .tid（标签或标题规则若有变动会不一致，且白白重转）。
SKIP_SOURCE_PREFIXES = {
    # 0 核心三宝书/PHB玩家手册 全本已排版完成（含 11法术/法术描述 手工重排），
    # 后续搬运 PHB 一律跳过，避免重转覆盖已排版内容（2026-09-01 用户要求）
    "0 核心三宝书\\PHB玩家手册\\",
    # 10 附录 整目录已手动调整/重排/还原/删除（如何使用大不全还原、如何为扩展大全做出贡献删除、
    # 武器附魔测评重排改名、html教学清洗等），2026-09-01 用户要求整目录排除在自动搬运外
    "10 附录\\",
    # 11 其他资源 整目录已搬运并 clean（2026-09-09，run_qita.py + clean_qita.py，38/38）：
    # 重转会用原始 CHM 覆盖已排版 .tid，按「处理过的书目一律 SKIP」规则加入。
    "11 其他资源\\",
    # 1 核心补充书籍/XPH扩展灵能手册 已搬运并结构化重排（clean_xph.py，2026-09-02）：
    # 重转会用原始 Word 噪音（StartFragment/<o:p>/断裂 span/海量 &nbsp;）覆盖已重排内容，
    # 故整本跳过。注意只跳过 XPH，1 核心补充书籍 下其余书（PHB2/DMG2/MM3-5）不受影响。
    "1 核心补充书籍\\XPH扩展灵能手册\\",
    # 1 核心补充书籍/PHB2玩家手册2 已搬运完成（2026-09-02，run_phb2.py，43/43），
    # 虽为规范 CHM 标准转换、未手工重排，仍按「处理过的书目一律 SKIP」规则加入（2026-09-02 用户要求）。
    "1 核心补充书籍\\PHB2玩家手册2\\",
    # 1 核心补充书籍/DMG2城主指南2 已搬运完成（2026-09-02，run_dmg2.py，24/24），
    # 同理按「处理过的书目一律 SKIP」规则加入（2026-09-02 用户要求）。
    "1 核心补充书籍\\DMG2城主指南2\\",
    # 1 核心补充书籍/MM3怪物图鉴3 已搬运（2026-09-02，run_mm3.py，124/124）并结构化重排
    # （clean_mm3.py，表格字段化 + Word 噪音清零），按「处理过的书目一律 SKIP」加入。
    "1 核心补充书籍\\MM3怪物图鉴3\\",
    # 1 核心补充书籍/MM4怪物图鉴4 已搬运（2026-09-02，run_mm4.py，103/103）并结构化重排
    # （clean_mm4.py，表格字段化 + Word 噪音清零），按「处理过的书目一律 SKIP」加入。
    "1 核心补充书籍\\MM4怪物图鉴4\\",
    # 1 核心补充书籍/MM5怪物图鉴5 已搬运（2026-09-02，run_mm5.py，108/108）并结构化重排
    # （clean_mm5.py，表格字段化 + Word 噪音清零），按「处理过的书目一律 SKIP」加入。
    "1 核心补充书籍\\MM5怪物图鉴5\\",
    # 2 万物万法万律/MIC万物大全 已搬运（2026-09-02，run_wanwu.py，51/51）并结构化重排
    # （clean_mic.py，物品段落字段化 + Word 噪音清零），按「处理过的书目一律 SKIP」加入。
    "2 万物万法万律\\MIC万物大全\\",
    # 2 万物万法万律/RC万律大全 已搬运（2026-09-02，run_wanwu.py，1/1）并结构化重排
    # （clean_mic.py 覆盖），按「处理过的书目一律 SKIP」加入。
    "2 万物万法万律\\RC万律大全\\",
    # 2 万物万法万律/SpC万法大全 已搬运（2026-09-02，run_wanwu.py，1/1）并结构化重排
    # （clean_mic.py 覆盖），按「处理过的书目一律 SKIP」加入。
    "2 万物万法万律\\SpC万法大全\\",
    # 3 完美系列/CAd完美冒险 已搬运（2026-09-03，run_cad.py，49/49）并结构化重排
    # （clean_cad.py，Word 噪音清零 + 表格紧凑化），按「处理过的书目一律 SKIP」加入。
    "3 完美系列\\CAd完美冒险\\",
    # 3 完美系列/CC完美斗士 已搬运（2026-09-07，run_cc.py，55/55）并结构化重排
    # （clean_cc.py，WinCHM 噪音清零 + DND3R-FEEDBACK 区块删除 + 表格紧凑化 + 实体引号清除），
    # 按「处理过的书目一律 SKIP」加入。
    "3 完美系列\\CC完美斗士\\",
    # 3 完美系列/CD完美神力 已搬运（2026-09-08，run_cd.py，129/129）并结构化重排
    # （clean_cd.py，WinCHM 噪音清零 + DND3R-FEEDBACK 区块删除 + 表格紧凑化），
    # 按「处理过的书目一律 SKIP」加入。
    "3 完美系列\\CD完美神力\\",
    # 3 完美系列/CM完美巫师 已搬运（2026-09-08，run_cm.py，39/39）并结构化重排
    # （clean_cm.py，WinCHM 噪音清零 + DND3R-FEEDBACK 区块删除 + 表格紧凑化），
    # 按「处理过的书目一律 SKIP」加入。
    "3 完美系列\\CM完美巫师\\",
    # 3 完美系列/CPsi完美灵能 已搬运（2026-09-08，run_cpsi.py，51/51）并结构化重排
    # （clean_cpsi.py，WinCHM 噪音清零 + DND3R-FEEDBACK 区块删除 + 表格紧凑化），
    # 按「处理过的书目一律 SKIP」加入。
    "3 完美系列\\CPsi完美灵能\\",
    # 3 完美系列/CS完美恶徒 已搬运（2026-09-08，run_cs.py，40/40）并结构化重排
    # （clean_cs.py，WinCHM 噪音清零 + DND3R-FEEDBACK 区块删除 + 表格紧凑化），
    # 按「处理过的书目一律 SKIP」加入。
    "3 完美系列\\CS完美恶徒\\",
    # 3 完美系列/CW完美战力 已搬运（2026-09-08，run_cw.py，61/61）并结构化重排
    # （clean_cw.py，WinCHM 噪音清零 + DND3R-FEEDBACK 区块删除 + 表格紧凑化），
    # 按「处理过的书目一律 SKIP」加入。
    "3 完美系列\\CW完美战力\\",
    # 4 阵营和位面 4 本（BoED崇善之书/FC1深渊堕群/FC2九狱君王/PlH位面手册）已批量搬运
    # （2026-09-08，共 255 页）并结构化重排（clean 后处理 + 单 ? 乱码清理），
    # 按「处理过的书目一律 SKIP」规则加入（防止日后全量重转覆盖已排版内容）。
    "4 阵营和位面\\BoED崇善之书\\",
    "4 阵营和位面\\FC1深渊堕群\\",
    "4 阵营和位面\\FC2九狱君王\\",
    "4 阵营和位面\\PlH位面手册\\",
    # 5 环境和社会 5 本（City城市风貌/Dungeon地城风光/Frost霜燃之书/Sand沙暴之书/Storm风暴之书）
    # 已批量搬运（2026-09-08，共 276 页）并结构化重排（clean 后处理 + 单 ? 乱码清理），
    # 按「处理过的书目一律 SKIP」规则加入。
    "5 环境和社会\\City城市风貌\\",
    "5 环境和社会\\Dungeon地城风光\\",
    "5 环境和社会\\Frost霜燃之书\\",
    "5 环境和社会\\Sand沙暴之书\\",
    "5 环境和社会\\Storm风暴之书\\",
    # 8 战役引钩 3 本（WoL传古武器/EoE邪恶典范/EE上古邪物）
    # 已批量搬运（2026-09-08，共 73 页）并结构化重排（clean 后处理 + 单 ? 乱码清理），
    # 按「处理过的书目一律 SKIP」规则加入。
    "8 战役引钩\\WoL传古武器\\",
    "8 战役引钩\\EoE邪恶典范\\",
    "8 战役引钩\\EE上古邪物\\",
    # 6 种族书 / 7 扩展全新体系 / 9 世设 三系列（2026-09-08 批量搬运完成，共 2778 页）
    # 并按「处理过的书目一律 SKIP」规则加入，防止日后全量重转覆盖已排版内容。
    "6 种族书\\",
    "7 扩展全新体系\\",
    "9 世设\\",
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
        if (
            rel in SKIP_SOURCES
            or any(rel.startswith(p) for p in SKIP_SOURCE_PREFIXES)
            or ".files/" in rel
        ):
            print("SKIP(已合并/已清洗):", rel)
            log(f"SKIP(已合并/已清洗): {rel}")
            continue
        src_path = os.path.join(ROOT, rel)
        if not os.path.isfile(src_path):
            print("MISSING:", rel)
            log(f"MISSING(源文件不存在): {rel}")
            continue

        try:
            text = cp.read_text(src_path)
            body = cp.extract_body(text)
            # 构造「书」归属（与 strip_hooks.book_of 对齐）：
            # 0 核心三宝书\XXX\... -> XXX；10 附录\... -> 10 附录
            _parts = rel.split("\\")
            book = _parts[1] if _parts[0] == "0 核心三宝书" and len(_parts) > 1 else _parts[0]
            body = cp.clean_html(body, book)
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
