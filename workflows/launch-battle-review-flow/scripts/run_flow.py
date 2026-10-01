# -*- coding: utf-8 -*-
"""
发布战报复盘流程 —— 端到端编排脚本。

编排逻辑（与 SKILL.md 的 DAG 一致）：
  发布日数据（各平台指标 + 目标 + 评论流）
    → 节点 1：[battle-report-generate] 五指标达标判定 + 平台结构 + 归因提示
              （scripts/battle_report.py）
    → 节点 2：[comment-emotion-detect] 评论情绪分布 + 风险处置统计
              （scripts/emotion_scan.py）
    → 节点 3：内置复盘合并——两份产物交叉出「复盘要点」：
      · 流量-情绪交叉（PV 高的平台 vs 负面/风险分布）
      · SLA 执行摘要（P0/P1 是否 30 分钟内处理——由值守记录提供，缺省标未记录）
      · 深度归因与行动建议由模型按 prompt.txt 撰写（≤3 条）
    → 产出：复盘报告.xlsx + review_result.json

失败处理：
  - 任一上游退出码 != 0 或产物缺失 → 中止并打印错误
  - metrics 缺失但评论在 → 只出情绪复盘并标注「指标缺失，补数据后复跑」
  - 评论缺失但 metrics 在 → 只出战报并标注「评论记录缺失」
  - 两者都缺 → 退出码 2
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

BATTLE_SCRIPT = os.path.join(REPO, "skills", "battle-report-generate", "scripts", "battle_report.py")
EMOTION_SCRIPT = os.path.join(REPO, "skills", "comment-emotion-detect", "scripts", "emotion_scan.py")


def main():
    ap = argparse.ArgumentParser(description="发布战报复盘流程")
    ap.add_argument("--input", help="流程输入 JSON（battle 段 + comments 段）")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()

    at.ensure_outdir(a.outdir)
    if a.demo:
        payload_path = os.path.join(a.outdir, "_demo_input.json")
        payload = {
            "battle": {
                "product": "ClipMate（剪贴板历史工具）",
                "launch_date": "2026-09-29",
                "targets": {"pv": 5000, "signups": 300, "github_stars": 100, "waitlist": 200, "mentions": 3},
                "platforms": [
                    {"name": "ProductHunt", "pv": 3200, "signups": 190, "github_stars": 76, "waitlist": 0, "mentions": 2, "note": "当日榜第 9"},
                    {"name": "V2EX", "pv": 980, "signups": 45, "github_stars": 12, "waitlist": 8, "mentions": 1, "note": "上午 10 点发"},
                    {"name": "X/Twitter", "pv": 540, "signups": 26, "github_stars": 9, "waitlist": 3, "mentions": 1, "note": "9 AM EST 第一峰"},
                    {"name": "即刻", "pv": 190, "signups": 11, "github_stars": 0, "waitlist": 0, "mentions": 0, "note": "晚 8 点"},
                ],
                "hourly_pv": [
                    {"hour": "00", "pv": 210}, {"hour": "01", "pv": 340}, {"hour": "02", "pv": 180},
                    {"hour": "03", "pv": 90}, {"hour": "04", "pv": 60}, {"hour": "05", "pv": 55},
                    {"hour": "06", "pv": 80}, {"hour": "07", "pv": 130}, {"hour": "08", "pv": 220},
                    {"hour": "09", "pv": 380}, {"hour": "10", "pv": 520}, {"hour": "11", "pv": 470},
                    {"hour": "12", "pv": 350}, {"hour": "13", "pv": 300}, {"hour": "14", "pv": 280},
                    {"hour": "15", "pv": 260}, {"hour": "16", "pv": 240}, {"hour": "17", "pv": 230},
                    {"hour": "18", "pv": 250}, {"hour": "19", "pv": 310}, {"hour": "20", "pv": 420},
                    {"hour": "21", "pv": 300}, {"hour": "22", "pv": 180}, {"hour": "23", "pv": 115},
                ],
            },
            "duty_log": {"p0_within_30min": 2, "p0_total": 2, "p1_within_30min": 0, "p1_total": 0,
                         "reply_total": 5, "comment_total": 41},
            "comments": [
                {"user": "maker_fan99", "platform": "ProductHunt", "text": "Congrats! Finally a clipboard manager that doesn't feel bloated. Love the search speed."},
                {"user": "dev_sarah", "platform": "ProductHunt", "text": "Does it support Windows 11 dark mode? And can I sync history across devices?"},
                {"user": "angry_bob", "platform": "ProductHunt", "text": "Crashed twice within 10 minutes. How do I get a refund?"},
                {"user": "skeptic_pete", "platform": "ProductHunt", "text": "This is just a copy of Paste with a new icon. Did you buy upvotes?"},
                {"user": "老王聊软件", "platform": "V2EX", "text": "搜索确实快，希望加上 OCR，要是能支持就好了"},
                {"user": "隐私控", "platform": "V2EX", "text": "剪贴板数据会上传服务器吗？"},
                {"user": "潜水员", "platform": "即刻", "text": "mark 一下"}
            ],
        }
        at.write_json(payload, payload_path)
    elif a.input:
        payload_path = a.input
        payload = at.read_json(a.input)
    else:
        ap.error("需要 --input / --demo 之一")

    battle = payload.get("battle") or {}
    comments = payload.get("comments") or []
    if not battle and not comments:
        print("[失败处理] battle 段与 comments 段均缺失，流程中止（退出码 2）。", file=sys.stderr)
        sys.exit(2)

    files, steps = [], []

    # --- 节点 1：战报 ---
    battle_json = None
    if battle:
        battle_in = os.path.join(a.outdir, "_battle_input.json")
        at.write_json(battle, battle_in)
        r = subprocess.run([sys.executable, BATTLE_SCRIPT, "--input", battle_in, "--outdir", a.outdir],
                           cwd=FLOW_DIR, capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            print(f"[失败处理] 上游技能 battle-report-generate 退出码 {r.returncode}，流程中止。", file=sys.stderr)
            print(r.stderr[-800:], file=sys.stderr)
            sys.exit(1)
        battle_json = os.path.join(a.outdir, "battle_report.json")
        if not os.path.exists(battle_json):
            print(f"[失败处理] 上游产物 {battle_json} 缺失，流程中止。", file=sys.stderr)
            sys.exit(1)
        files.append(battle_json)
        steps.append({"step": 1, "skill": "battle-report-generate", "status": "ok", "output": battle_json})

    # --- 节点 2：评论情绪 ---
    emotion_json = None
    if comments:
        emo_in = os.path.join(a.outdir, "_emotion_input.json")
        at.write_json({"comments": comments, "product": battle.get("product", "")}, emo_in)
        r = subprocess.run([sys.executable, EMOTION_SCRIPT, "--input", emo_in, "--outdir", a.outdir],
                           cwd=FLOW_DIR, capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            print(f"[失败处理] 上游技能 comment-emotion-detect 退出码 {r.returncode}，流程中止。", file=sys.stderr)
            print(r.stderr[-800:], file=sys.stderr)
            sys.exit(1)
        emotion_json = os.path.join(a.outdir, "emotion_scan.json")
        if not os.path.exists(emotion_json):
            print(f"[失败处理] 上游产物 {emotion_json} 缺失，流程中止。", file=sys.stderr)
            sys.exit(1)
        files.append(emotion_json)
        steps.append({"step": 2, "skill": "comment-emotion-detect", "status": "ok", "output": emotion_json})

    # --- 节点 3：复盘合并 ---
    summary = {"产品": battle.get("product", "未提供"), "发布日": battle.get("launch_date", "未提供")}
    review_rows = []

    if battle_json:
        b = at.read_json(battle_json)
        summary.update({
            "总 PV": b["summary"]["总 PV"], "总注册": b["summary"]["总注册"],
            "PV→注册转化率": b["summary"]["PV→注册转化率"],
            "达标指标": b["summary"]["达标指标"], "整体判定": b["summary"]["整体判定"],
        })
        # 流量-情绪交叉：情绪按平台聚合
        emo_by_plat = {}
        if emotion_json:
            e = at.read_json(emotion_json)
            for row in e.get("queue", []):
                plat = row["平台"]
                d = emo_by_plat.setdefault(plat, {"评论": 0, "风险": 0, "负面": 0})
                d["评论"] += 1
                if "风险" in row["情绪"]:
                    d["风险"] += 1
                if "负面" in row["情绪"]:
                    d["负面"] += 1
        for p in b.get("platforms", []):
            plat = p["平台"]
            emo = emo_by_plat.get(plat)
            review_rows.append({
                "平台": plat, "PV": p["PV"], "PV占比": p["PV占比"], "注册": p["注册"],
                "评论样本": emo["评论"] if emo else "—",
                "风险/负面": (f"{emo['风险']}/{emo['负面']}" if emo else "—"),
                "交叉观察": (
                    "流量主力且无风险——守住响应节奏" if emo and emo["风险"] == 0 and p["PV占比"] not in ("", "—") and int(str(p["PV占比"]).rstrip('%')) >= 50 else
                    "流量主力且有风险评论——优先清该平台风险" if emo and emo["风险"] > 0 and str(p["PV占比"]) not in ("—", "") and int(str(p["PV占比"]).rstrip('%')) >= 50 else
                    "有风险评论——按标准处置跟进" if emo and emo["风险"] > 0 else
                    "样本少，情绪结论不下" if emo and emo["评论"] < 3 else
                    "—"
                ),
            })
    else:
        summary["指标状态"] = "缺失——补各平台数据后复跑战报段"

    duty = payload.get("duty_log") or {}
    sla_row = "未记录（建议发布日值守记录 P0/P1 处理时长）"
    if duty:
        p0 = f"{duty.get('p0_within_30min', 0)}/{duty.get('p0_total', 0)}"
        sla_row = f"P0 30 分钟内处理 {p0}；全日回复 {duty.get('reply_total', 0)}/{duty.get('comment_total', 0)} 条"
    review_rows.append({"平台": "（值守执行）", "PV": "—", "PV占比": "—", "注册": "—",
                        "评论样本": duty.get("comment_total", "—"), "风险/负面": "—",
                        "交叉观察": sla_row})

    if emotion_json and not battle_json:
        summary["评论状态"] = "仅评论复盘——指标缺失"

    summary["深度归因与行动建议"] = "由模型按 prompt.txt 撰写（≤3 条，每条挂数据点），本脚本只出交叉观察"
    summary["说明"] = "达标/转化/分布为上游脚本计算；复盘要点为本流程交叉合并；深度归因人工+模型完成"

    xlsx = at.write_excel(
        os.path.join(a.outdir, "复盘报告.xlsx"),
        {
            "复盘要点": review_rows,
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        widths={"复盘要点": {"交叉观察": 46}},
    )
    js = at.write_json({"summary": summary, "review_rows": review_rows,
                        "generated_at": at.stamp(),
                        "note": "上游计算结果交叉合并；深度归因由模型按 prompt.txt 完成"},
                       os.path.join(a.outdir, "review_result.json"))
    files += [xlsx, js]
    steps.append({"step": 3, "skill": "（内置）复盘合并", "status": "ok", "output": xlsx})

    print(f"复盘包：{summary.get('整体判定', '—')}（达标 {summary.get('达标指标', '—')}），"
          f"交叉观察 {len(review_rows)} 条")
    for f in files:
        print(" 产物:", f)
    at.emit({"summary": summary, "steps": steps, "files": files})


if __name__ == "__main__":
    main()
