# -*- coding: utf-8 -*-
"""
评论情绪识别 —— 词表加权打分 + 风险规则扫描器。

职责边界：本脚本只做**词表打分、规则分类、优先级排队与产物生成**（机器的强项）。
反讽识别、语境判断、刷量号复核由模型按 prompt.txt 完成（模型的强项）。

用法：
  python emotion_scan.py --input input.json --outdir out
  python emotion_scan.py --demo                # 用内置样例跑一遍
  python emotion_scan.py --text "这工具居然要订阅费？" --platform ProductHunt

产物：
  out/评论分类清单.xlsx   分类明细 / 优先级队列 / 汇总
  out/情绪分布.png        五类情绪占比饼图
  out/emotion_scan.json   机器可读结果（供智能体/工作流读取）
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(SKILL_DIR))
sys.path.insert(0, os.path.join(REPO, "lib"))

try:
    import assettools as at
except ImportError:  # pragma: no cover
    print("[错误] 未找到 lib/assettools.py。请确认技能位于 <repo>/skills/<slug>/scripts/ 下，"
          "且 <repo>/lib/assettools.py 存在。", file=sys.stderr)
    sys.exit(2)

# ---------------------------------------------------------------- 词表
# 正向词（权重 1）；负向词（权重 1，前置否定词翻转为正）
POS_WORDS = [
    "好用", "很棒", "太棒", "喜欢", "支持", "赞", "厉害", "惊艳", "精美", "顺手",
    "解决了", "效率", "省时间", "终于有人做", "刚需", "期待已久", "congratulations",
    "great", "awesome", "love", "amazing", "useful", "handy", "finally", "congrats",
    "brilliant", "impressive", "clean", "elegant", "game changer", "must-have",
]
NEG_WORDS = [
    "垃圾", "难用", "失望", "坑", "套路", "割韭菜", "太贵", "收费", "智商税",
    "卡顿", "崩溃", "闪退", "bug", "BUG", "报错", "打不开", "加载慢", "兼容",
    "广告", "烦人", "不如", "退订", "退款", "卸载", "抄袭", "山寨",
    "broken", "crash", "slow", "expensive", "disappoint", "waste", "buggy",
    "confusing", "bloated", "spammy", "ripoff", "overpriced",
]
NEGATION = ["不", "没那么", "并不", "没有", "not", "n't", "never", "no "]

# 风险子类规则（正则, 风险名, 处理动作）—— 风险优先于情绪
RISK_RULES = [
    (r"刷榜|买量|互赞群|upvote\s*群|拉票|vote\s*4\s*vote", "刷榜指控",
     "立即自查并公开说明推广方式；PH 禁止 incentivized upvote，不删帖不辩解"),
    (r"隐私|数据收集|上传了什么|权限|telemetry|tracking", "安全/隐私质疑",
     "2 小时内回复数据流向说明，链接隐私政策；必要时补 security note"),
    (r"退款|退钱|chargeback|refund|要回.{0,4}钱", "退款诉求",
     "30 分钟内私信响应，按退款政策处理，公开评论回复处理进度"),
    (r"抄袭|copy\s*of|山寨|套壳|就是\s*\S+\s*换皮", "抄袭/竞品指控",
     "承认相似点+列差异表；不攻击竞品；引用独立评测"),
    (r"跑路|关停|还能活多久|abandonware", "存续质疑",
     "回复开发计划与更新日志链接；独立开发者直面回答比公关稿有效"),
    (r"假评论|水军|刷评论|fake\s*review", "水军指控",
     "不反驳个体，公布真实用户获取渠道与数据口径"),
]

# 问题类（疑问词或问号）
QUESTION_PAT = re.compile(r"？|\?|能不能|可不可以|支持.{0,6}吗|有没有|为什么|how|can\s|does\s|why\s|is\s+there", re.I)
FEATURE_PAT = re.compile(r"希望|建议|能不能加|求支持|要是.{0,8}就好了|would\s+be\s+nice|please\s+add|feature\s+request", re.I)

SLA = {"ProductHunt": "30 分钟（首日评论影响排名）", "V2EX": "60 分钟", "Reddit": "60 分钟",
       "X": "60 分钟", "即刻": "60 分钟", "微博": "120 分钟", "公众号": "120 分钟", "通用": "60 分钟"}


def scan_comment(text: str, platform: str):
    """返回 (情绪, 风险名/空, 疑问bool, 功能请求bool, 命中词列表, 得分)"""
    hits, score = [], 0.0
    lower = text.lower()
    for w in POS_WORDS:
        for m in re.finditer(re.escape(w), lower):
            pre = lower[max(0, m.start() - 12):m.start()]  # 否定窗口：中文 2 字 / 英文短语
            if any(n in pre for n in NEGATION):
                continue  # 否定前缀命中不加分
            hits.append(("pos", w))
            score += 1
    for w in NEG_WORDS:
        for m in re.finditer(re.escape(w.lower()), lower):
            pre = lower[max(0, m.start() - 12):m.start()]
            if any(n in pre for n in NEGATION):
                continue  # 「doesn't feel bloated」是否定差评词=好评
            hits.append(("neg", w))
            score -= 1
    risk = ""
    for pat, name, _ in RISK_RULES:
        if re.search(pat, text, re.I):
            risk = name
            break
    is_q = bool(QUESTION_PAT.search(text))
    is_f = bool(FEATURE_PAT.search(text))

    if risk:
        emo = "🔴 风险"
    elif score <= -1:
        emo = "⚠️ 负面"
    elif score >= 2:
        emo = "🟢 正面"
    elif score == 1 and not is_f:
        emo = "🟢 正面"
    elif score == 1 and is_f:
        emo = "⚪ 中性"  # 「希望加上 X」属建设性建议，不算真实好评
    elif is_q:
        emo = "🔵 疑问"
    else:
        emo = "⚪ 中性"
    return emo, risk, is_q, is_f, hits, score


def priority(emo, risk, is_q, idx):
    """优先级队列：风险 > 负面 > 疑问 > 正面 > 中性。返回 (P级, SLA, 建议动作)。"""
    if emo == "🔴 风险":
        return "P0", "30 分钟", RISK_ACTION.get(risk, "人工复核")
    if emo == "⚠️ 负面":
        return "P1", SLA.get(platform_sla_key(idx), "60 分钟"), "承认+给方案：先确认问题属实，给时间点或替代方案；不删帖不争论"
    if emo == "🔵 疑问":
        return "P2", "2 小时", "对照 FAQ 库回答；FAQ 没有的问题记录下来补进 FAQ（faq-pregenerate）"
    if emo == "🟢 正面":
        return "P3", "24 小时", "感谢+追问使用场景（真实好评是素材，截图须获用户同意）"
    return "P4", "48 小时", "观察即可，不逐条回复"


RISK_ACTION = {
    "刷榜指控": "公开说明推广方式；自查有无 incentivized upvote；不删帖不辩解",
    "安全/隐私质疑": "2 小时内回复数据流向说明，链接隐私政策",
    "退款诉求": "30 分钟内私信响应，公开回复处理进度",
    "抄袭/竞品指控": "承认相似点+列差异表，不攻击竞品",
    "存续质疑": "回复开发计划与更新日志链接",
    "水军指控": "公布真实用户获取渠道与数据口径",
}

platform_sla_key = lambda c: c.get("platform", "通用")


def build(payload, outdir):
    comments = payload.get("comments", [])
    if isinstance(comments, str):  # 兼容纯文本输入
        comments = [{"user": "匿名", "platform": payload.get("platform", "通用"), "text": comments}]

    rows, risk_n = [], 0
    counts = {"🟢 正面": 0, "⚠️ 负面": 0, "⚪ 中性": 0, "🔵 疑问": 0, "🔴 风险": 0}
    for i, c in enumerate(comments, 1):
        text = str(c.get("text", ""))
        platform = c.get("platform", payload.get("platform", "通用"))
        emo, risk, is_q, is_f, hits, score = scan_comment(text, platform)
        p, sla, action = priority(emo, risk, is_q, c)
        counts[emo] += 1
        risk_n += 1 if risk else 0
        rows.append({
            "序号": i,
            "用户": c.get("user", "匿名"),
            "平台": platform,
            "评论摘录": text[:40] + ("…" if len(text) > 40 else ""),
            "情绪": emo,
            "得分": score,
            "风险子类": risk or "—",
            "疑问": "是" if is_q else "",
            "功能请求": "是" if is_f else "",
            "命中词": "、".join(f"{k}:{w}" for k, w in hits[:4]) or "—",
            "优先级": p,
            "响应SLA": sla,
            "建议动作": action,
            "状态": "待人工确认",
        })

    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
    rows.sort(key=lambda r: (order[r["优先级"]], r["序号"]))
    for i, r in enumerate(rows, 1):
        r["队列位"] = i

    total = len(rows) or 1
    summary = {
        "评论总数": len(rows),
        "正面": counts["🟢 正面"], "负面": counts["⚠️ 负面"], "中性": counts["⚪ 中性"],
        "疑问": counts["🔵 疑问"], "风险": counts["🔴 风险"],
        "正面占比": f"{counts['🟢 正面'] / total:.0%}",
        "负面占比": f"{counts['⚠️ 负面'] / total:.0%}",
        "健康线": "正面占比 ≥60% 且 风险=0 为健康；负面 >20% 触发「承认+给方案」集中响应",
        "P0/P1 数量": sum(1 for r in rows if r["优先级"] in ("P0", "P1")),
        "说明": "词表机器打分结果；反讽与语境由模型按 prompt.txt 复核，动作全部待人工确认",
    }

    at.ensure_outdir(outdir)
    xlsx = at.write_excel(
        os.path.join(outdir, "评论分类清单.xlsx"),
        {
            "优先级队列": rows,
            "分类明细": sorted(rows, key=lambda r: r["序号"]),
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"优先级队列": {"情绪": "contains:风险", "状态": "contains:待人工确认"}},
        widths={"优先级队列": {"评论摘录": 34, "命中词": 24, "建议动作": 46},
                "分类明细": {"评论摘录": 34, "命中词": 24, "建议动作": 46}},
    )
    png = at.pie_chart(
        os.path.join(outdir, "情绪分布.png"),
        [k.strip("🟢⚠️⚪🔵🔴 ") for k in counts if counts[k]],
        [v for v in counts.values() if v],
        title="发布日评论情绪分布",
    )
    js = at.write_json({"summary": summary, "queue": rows,
                        "generated_at": at.stamp(),
                        "note": "词表扫描结果；反讽/语境/刷量号由模型按 prompt.txt 复核"},
                       os.path.join(outdir, "emotion_scan.json"))
    return {"files": [xlsx, png, js], "summary": summary, "queue": rows}


DEMO = {
    "product": "ClipMate（剪贴板历史工具）",
    "comments": [
        {"user": "maker_fan99", "platform": "ProductHunt", "text": "Congrats on the launch! Finally a clipboard manager that doesn't feel bloated. Love the search speed."},
        {"user": "dev_sarah", "platform": "ProductHunt", "text": "Does it support Windows 11 dark mode? And can I sync history across devices?"},
        {"user": "angry_bob", "platform": "ProductHunt", "text": "Crashed twice within 10 minutes on Windows 10. How do I get a refund?"},
        {"user": "skeptic_pete", "platform": "ProductHunt", "text": "Another clipboard app? This is just a copy of Paste with a new icon. Also weird how all the upvotes came in the first hour, did you buy upvotes?"},
        {"user": "老王聊软件", "platform": "V2EX", "text": "用了两天，搜索确实快，但希望加上 OCR 截图取词，要是能支持就好了"},
        {"user": "隐私控", "platform": "V2EX", "text": "剪贴板数据会上传服务器吗？涉及密码片段的话权限范围是什么？"},
        {"user": "潜水员", "platform": "即刻", "text": "mark 一下"},
    ],
}


def main():
    ap = argparse.ArgumentParser(description="评论情绪识别 —— 词表加权打分 + 风险规则")
    ap.add_argument("--input", help="输入 JSON（comments[]）")
    ap.add_argument("--text", help="直接传单条评论")
    ap.add_argument("--platform", default="通用")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--demo", action="store_true", help="用内置样例跑一遍")
    a = ap.parse_args()

    if a.demo:
        payload = DEMO
    elif a.input:
        payload = at.read_json(a.input)
    elif a.text:
        payload = {"comments": [{"user": "匿名", "platform": a.platform, "text": a.text}]}
    else:
        ap.error("需要 --input / --text / --demo 之一")

    r = build(payload, a.outdir)
    s = r["summary"]
    print(f"评论 {s['评论总数']} 条：正 {s['正面']} / 负 {s['负面']} / 中 {s['中性']} / 疑 {s['疑问']} / 风险 {s['风险']}"
          f" —— P0+P1 共 {s['P0/P1 数量']} 条需优先处理")
    for f in r["files"]:
        print(" 产物:", f)
    at.emit(r)


if __name__ == "__main__":
    main()
