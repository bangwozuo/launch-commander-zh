# -*- coding: utf-8 -*-
"""
当日评论值守流程 —— 端到端编排脚本。

编排逻辑（与 SKILL.md 的 DAG 一致）：
  新评论流（PH/V2EX/X/即刻…）→ [comment-emotion-detect] 五类情绪 + 六类风险 + P0-P4 排队
    → 内置值守加工：
      P0/P1 → 回复任务卡（30 分钟 SLA，负面骨架「承认+给方案+留渠道」由模型按 reply-drafting 撰写）
      P2    → FAQ 匹配任务（faq-pregenerate 口径库命中关键词）
      P3/P4 → 观察名单（不逐条回）
    → 值守看板（本轮 SLA 风险数 / 待回队列 / 升级清单）+ 值守清单.xlsx

失败处理：
  - 上游 comment-emotion-detect 退出码 != 0 或产物缺失 → 中止并打印错误
  - 评论流为空 → 输出「本轮 0 新评论」看板并正常退出（发布日 0 评论要查发布链接）
  - 情绪覆盖异常（全部中性）→ 汇总标红「疑似抓取不全，人工核对平台评论数」
  - FAQ 库缺失 → P2 任务照常生成，备注「无口径库，回复前须人工确认事实」

用法：
  python run_flow.py --input input.json --outdir out
  python run_flow.py --demo
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLOW_DIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(FLOW_DIR))
sys.path.insert(0, os.path.join(REPO, "lib"))

try:
    import assettools as at
except ImportError:  # pragma: no cover
    print("[错误] 未找到 lib/assettools.py", file=sys.stderr)
    sys.exit(2)

EMOTION_SCRIPT = os.path.join(REPO, "skills", "comment-emotion-detect", "scripts", "emotion_scan.py")

# FAQ 口径库关键词（来自 faq-pregenerate；演示口径随 demo 提供，实际由用户定稿）
DEMO_FAQ = {
    "dark mode|深色": "支持 Win11 深色模式，自动跟随系统",
    "sync|同步": "Pro 功能，端到端加密，可选开启，默认只存本机",
    "refund|退款": "14 天无理由退款，走网站 /refund",
    "privacy|隐私|上传": "内容只存本机 SQLite，无上传代码路径，断网可用",
    "OCR|取字|截图": "OCR 已上线（Pro），更新到 2.1",
    "价格|收费|pricing|贵": "免费版完整（搜索+3个月历史）；Pro $8/月（OCR/无限历史/同步）",
}


def match_faq(text, faq=None):
    import re
    faq = faq or DEMO_FAQ
    for pat, answer in faq.items():
        if re.search(pat, text, re.I):
            return pat, answer
    return "", ""


REPLY_SKELETON = {
    "P0": "风险处置：按风险子类标准口径（刷榜=公开说明推广方式；退款=政策+私信渠道；隐私=数据流向+政策链接）",
    "P1": "负面三段骨架：承认（不辩解开头）→ 给方案（要信息/给时间点，未授权不承诺日期）→ 留渠道（DM/issue）",
    "P2": "疑问直答：第一句就是答案（对照 FAQ 口径）→ 一句话支撑 → 钩子续对话",
    "P3": "感谢 + 追问使用场景（好评引用外用须授权）",
    "P4": "观察不逐条回",
}


def main():
    ap = argparse.ArgumentParser(description="当日评论值守流程")
    ap.add_argument("--input", help="流程输入 JSON（launch_day/faq/comments）")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()

    at.ensure_outdir(a.outdir)
    if a.demo:
        payload_path = os.path.join(a.outdir, "_demo_input.json")
        payload = {
            "launch_day": True,
            "product": "ClipMate（剪贴板历史工具）",
            "comments": [
                {"user": "maker_fan99", "platform": "ProductHunt", "text": "Congrats! Finally a clipboard manager that doesn't feel bloated. Love the search speed."},
                {"user": "dev_sarah", "platform": "ProductHunt", "text": "Does it support Windows 11 dark mode? And can I sync history across devices?"},
                {"user": "angry_bob", "platform": "ProductHunt", "text": "Crashed twice within 10 minutes on Windows 10. How do I get a refund?"},
                {"user": "skeptic_pete", "platform": "ProductHunt", "text": "This is just a copy of Paste with a new icon. Weird how all the upvotes came in the first hour, did you buy upvotes?"},
                {"user": "老王聊软件", "platform": "V2EX", "text": "用了两天搜索确实快，希望加上 OCR 截图取字，要是能支持就好了"},
                {"user": "潜水员", "platform": "即刻", "text": "mark 一下，看着不错"}
            ],
        }
        at.write_json(payload, payload_path)
    elif a.input:
        payload_path = a.input
        payload = at.read_json(a.input)
    else:
        ap.error("需要 --input / --demo 之一")

    # --- 步骤 1：上游情绪识别与排队 ---
    r = subprocess.run(
        [sys.executable, EMOTION_SCRIPT, "--input", payload_path, "--outdir", a.outdir],
        cwd=FLOW_DIR, capture_output=True, text=True, timeout=180,
    )
    if r.returncode != 0:
        print(f"[失败处理] 上游技能 comment-emotion-detect 退出码 {r.returncode}，流程中止。", file=sys.stderr)
        print(r.stderr[-800:], file=sys.stderr)
        sys.exit(1)
    scan_js = os.path.join(a.outdir, "emotion_scan.json")
    if not os.path.exists(scan_js):
        print(f"[失败处理] 上游产物 {scan_js} 缺失，流程中止。", file=sys.stderr)
        sys.exit(1)
    scan = at.read_json(scan_js)

    # --- 步骤 2：值守加工（回复任务卡 + FAQ 匹配 + 看板） ---
    queue = scan.get("queue", [])
    launch_day = bool(payload.get("launch_day", False))
    faq = payload.get("faq") or DEMO_FAQ
    full_text = {c.get("user", ""): str(c.get("text", "")) for c in payload.get("comments", [])}

    tasks, watch = [], []
    for row in queue:
        p = row["优先级"]
        if p in ("P0", "P1", "P2"):
            kw, answer = match_faq(full_text.get(row.get("用户", ""), str(row.get("评论摘录", ""))), faq)
            tasks.append({
                "队列位": row["队列位"], "优先级": p, "平台": row["平台"], "用户": row["用户"],
                "评论摘录": row["评论摘录"], "情绪": row["情绪"], "风险子类": row["风险子类"],
                "SLA": row["响应SLA"],
                "回复骨架": REPLY_SKELETON.get(p, ""),
                "FAQ命中": (kw or "（无口径命中——回复前须人工确认事实，缺口回填 faq-pregenerate）"),
                "FAQ口径": answer or "—",
                "草拟": "reply-drafting 按骨架撰写，人工确认后发布",
                "状态": "待人工确认",
            })
        else:
            watch.append({"队列位": row["队列位"], "平台": row["平台"], "用户": row["用户"],
                          "评论摘录": row["评论摘录"], "情绪": row["情绪"],
                          "处置": "观察不逐条回" if p == "P4" else "感谢+追问场景（引用须授权）"})

    s = scan["summary"]
    sla_risk = sum(1 for t in tasks if t["优先级"] in ("P0",) or (t["优先级"] == "P1" and launch_day))
    empty_flow = len(queue) == 0
    all_neutral = (s["中性"] == s["评论总数"] and s["评论总数"] > 0)

    board = {
        "产品": payload.get("product", "未提供"),
        "轮次类型": "发布日值守（每 15 分钟一轮）" if launch_day else "日常值守",
        "本轮新评论": s["评论总数"],
        "正/负/中/疑/风险": f"{s['正面']}/{s['负面']}/{s['中性']}/{s['疑问']}/{s['风险']}",
        "待回任务（P0-P2）": len(tasks),
        "30 分钟 SLA 风险": sla_risk,
        "健康判定": s["健康线"],
        "升级提示": "P0 全部升级开发者本人；同一用户负面第二回合转私信；媒体/大V询问升级人工",
        "异常标注": ("发布日 0 评论——检查发布链接与平台审核状态" if empty_flow else
                   ("全部中性——疑似抓取不全，人工核对平台评论数" if all_neutral else "正常")),
        "说明": "情绪/排队由上游脚本计算；回复草稿由 reply-drafting 撰写并经人工确认",
    }

    xlsx = at.write_excel(
        os.path.join(a.outdir, "值守清单.xlsx"),
        {
            "回复任务卡": tasks or [{"队列位": "—", "备注": "本轮无 P0-P2 任务"}],
            "观察名单": watch or [{"队列位": "—", "备注": "（无）"}],
            "值守看板": [{"项": k, "内容": str(v)} for k, v in board.items()],
        },
        highlights={"回复任务卡": {"优先级": "contains:P0", "状态": "contains:待人工确认"}},
        widths={"回复任务卡": {"评论摘录": 32, "回复骨架": 50, "FAQ口径": 40},
                "值守看板": {"内容": 60}},
    )

    result = {
        "flow": "daily-comment-duty-flow",
        "steps": [
            {"step": 1, "skill": "comment-emotion-detect", "status": "ok", "output": scan_js},
            {"step": 2, "skill": "（内置）值守加工 + reply-drafting 撰写位", "status": "ok", "output": xlsx},
        ],
        "board": board,
        "tasks": tasks,
        "files": [xlsx, scan_js],
        "generated_at": at.stamp(),
    }
    at.write_json(result, os.path.join(a.outdir, "duty_flow_result.json"))
    print(f"本轮 {s['评论总数']} 条新评论：待回 {len(tasks)}（30 分钟 SLA {sla_risk} 条），观察 {len(watch)}")
    for f in result["files"] + [os.path.join(a.outdir, 'duty_flow_result.json')]:
        print(" 产物:", f)
    at.emit(result)


if __name__ == "__main__":
    main()
