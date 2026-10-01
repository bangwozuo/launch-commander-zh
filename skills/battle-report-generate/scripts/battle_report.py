# -*- coding: utf-8 -*-
"""
发布战报生成 —— 指标汇总 / 达标判定 / 归因提示 / 产物生成。

职责边界：本脚本只做**确定性计算**（达标率、转化率、占比、排名）与产物生成。
归因分析、高光提炼、失误复盘由模型按 prompt.txt 完成（模型的强项）。

用法：
  python battle_report.py --input input.json --outdir out
  python battle_report.py --demo                # 用内置样例跑一遍

产物：
  out/发布战报.xlsx      关键指标 / 平台明细 / 归因提示 / 汇总
  out/平台流量对比.png    各平台 PV 柱状图
  out/当日流量曲线.png    发布日逐小时 PV 曲线（有数据时）
  out/battle_report.json 机器可读结果（供智能体/工作流读取）
"""
from __future__ import annotations

import argparse
import os
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

# 指标定义：(键, 名称, 达标线, 参考基准)
METRICS = [
    ("pv", "PV（页面访问）", 1.0, "独立开发者发布日全平台 PV 经验区间 3k-15k"),
    ("signups", "注册数", 1.0, "PV→注册转化基准 5%-12%，<3% 查落地页"),
    ("github_stars", "GitHub 星标", 1.0, "PH 首日 100+ 星属头部表现；<20 查 README 首屏"),
    ("waitlist", "waitlist 转化", 1.0, "waitlist 订阅 / PV 基准 3%-8%"),
    ("mentions", "媒体与社区提及", 1.0, "≥3 次独立提及（非转发）算有效传播"),
]


def achievement(cur, target):
    """达标判定：≥100% 达标 / 70-100% 部分达标 / <70% 未达标。"""
    if target in (None, 0):
        return "未设目标", 0.0
    r = cur / target
    if r >= 1.0:
        return "✅ 达标", r
    if r >= 0.7:
        return "🟡 部分达标", r
    return "🔴 未达标", r


def attribution_hints(agg, targets):
    """规则式归因提示（机器可判的部分；深度归因由模型完成）。"""
    hints = []
    pv, su = agg.get("pv", 0), agg.get("signups", 0)
    wl = agg.get("waitlist", 0)
    conv = su / pv if pv else 0
    wl_conv = wl / pv if pv else 0
    if pv and conv < 0.03:
        hints.append(f"PV→注册转化率 {conv:.1%} 低于 3% 下限——流量没问题，落地页有问题：查首屏卖点、加载速度、CTA 位置")
    if pv and 0.03 <= conv <= 0.12:
        hints.append(f"PV→注册转化率 {conv:.1%} 在 5%-12% 基准带内（按 3%-12% 宽口径）——转化链路正常")
    if pv and wl and wl_conv < 0.03:
        hints.append(f"waitlist 转化率 {wl_conv:.1%} 低于 3% 基准——钩子吸引力不足或表单门槛高，检查是否要填太多字段")
    t_signups = targets.get("signups")
    if t_signups and pv and su / t_signups < 0.7 and conv >= 0.03:
        hints.append("注册未达标但转化率正常——是流量缺口不是转化缺口：T+7 复盘重点看渠道结构，哪几个平台没跑出来")
    stars = agg.get("github_stars", 0)
    if su and stars and stars / su < 0.05:
        hints.append(f"GitHub 星标/注册 = {stars / su:.0%} 低于 5%——开发者受众占比低或 README 首屏缺代码截图")
    if agg.get("mentions", 0) >= 3:
        hints.append("媒体/社区提及 ≥3 次——把提及截图存档，T+7 复盘时评估哪类渠道带来自来水")
    if not hints:
        hints.append("未触发规则归因——各指标在基准带内或数据不足，深度归因由模型按 prompt.txt 完成")
    return hints


def build(payload, outdir):
    product = payload.get("product", "未命名产品")
    targets = payload.get("targets", {})
    platforms = payload.get("platforms", [])
    hourly = payload.get("hourly_pv", [])

    # --- 平台明细 ---
    plat_rows = []
    agg = {}
    for p in platforms:
        for k in ("pv", "signups", "github_stars", "waitlist", "mentions"):
            agg[k] = agg.get(k, 0) + p.get(k, 0)
    for p in sorted(platforms, key=lambda x: -x.get("pv", 0)):
        pv = p.get("pv", 0)
        plat_rows.append({
            "平台": p.get("name", "?"),
            "PV": pv,
            "PV占比": f"{pv / agg['pv']:.0%}" if agg["pv"] else "—",
            "注册": p.get("signups", 0),
            "注册转化率": f"{p.get('signups', 0) / pv:.1%}" if pv else "—",
            "GitHub 星": p.get("github_stars", 0),
            "waitlist": p.get("waitlist", 0),
            "提及": p.get("mentions", 0),
            "备注": p.get("note", ""),
        })

    # --- 关键指标达标表 ---
    metric_rows, hit_n, total_n = [], 0, 0
    for key, name, _, bench in METRICS:
        cur = agg.get(key, 0)
        tgt = targets.get(key)
        verdict, ratio = achievement(cur, tgt)
        if tgt not in (None, 0):
            total_n += 1
            hit_n += 1 if ratio >= 1.0 else 0
        metric_rows.append({
            "指标": name,
            "实际": cur,
            "目标": tgt if tgt is not None else "未设",
            "达标率": f"{ratio:.0%}" if tgt not in (None, 0) else "—",
            "判定": verdict,
            "参考基准": bench,
        })

    overall = "—"
    if total_n:
        if hit_n == total_n:
            overall = "✅ 全部达标"
        elif hit_n / total_n >= 0.6:
            overall = "🟡 大部分达标"
        else:
            overall = "🔴 多数未达标"

    hints = attribution_hints(agg, targets)

    summary = {
        "产品": product,
        "发布日": payload.get("launch_date", "未提供"),
        "总 PV": agg.get("pv", 0),
        "总注册": agg.get("signups", 0),
        "PV→注册转化率": f"{agg.get('signups', 0) / agg['pv']:.1%}" if agg.get("pv") else "—",
        "GitHub 星标": agg.get("github_stars", 0),
        "waitlist": agg.get("waitlist", 0),
        "提及数": agg.get("mentions", 0),
        "达标指标": f"{hit_n}/{total_n}" if total_n else "未设目标",
        "整体判定": overall,
        "归因提示数": len(hints),
        "说明": "达标率/转化率/占比为脚本计算；高光与失误的深度归因由模型按 prompt.txt 完成",
    }

    at.ensure_outdir(outdir)
    files = []
    files.append(at.write_excel(
        os.path.join(outdir, "发布战报.xlsx"),
        {
            "关键指标": metric_rows,
            "平台明细": plat_rows or [{"平台": "（无平台数据）"}],
            "归因提示": [{"#": i + 1, "提示": h} for i, h in enumerate(hints)],
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"关键指标": {"判定": "contains:未达标"}},
        widths={"关键指标": {"参考基准": 44}, "归因提示": {"提示": 70}, "平台明细": {"备注": 26}},
    ))

    if platforms:
        files.append(at.bar_chart(
            os.path.join(outdir, "平台流量对比.png"),
            [p.get("name", "?") for p in platforms],
            [p.get("pv", 0) for p in platforms],
            title=f"{product} 发布日各平台 PV",
            ylabel="PV",
        ))
    if len(hourly) >= 2:
        files.append(at.line_chart(
            os.path.join(outdir, "当日流量曲线.png"),
            [h.get("hour", i) for i, h in enumerate(hourly)],
            {"PV": [h.get("pv", 0) for h in hourly]},
            title="发布日逐小时 PV（对照各平台发布时点）",
            xlabel="小时",
            ylabel="PV",
        ))

    js = at.write_json({"summary": summary, "metrics": metric_rows, "platforms": plat_rows,
                        "attribution_hints": hints,
                        "generated_at": at.stamp(),
                        "note": "确定性计算结果；深度归因由模型按 prompt.txt 完成"},
                       os.path.join(outdir, "battle_report.json"))
    files.append(js)
    return {"files": files, "summary": summary, "hints": hints}


DEMO = {
    "product": "ClipMate（剪贴板历史工具）",
    "launch_date": "2026-09-29",
    "targets": {"pv": 5000, "signups": 300, "github_stars": 100, "waitlist": 200, "mentions": 3},
    "platforms": [
        {"name": "ProductHunt", "pv": 3200, "signups": 190, "github_stars": 76, "waitlist": 0, "mentions": 2, "note": "当日榜第 9，00:01 PT 发布"},
        {"name": "V2EX", "pv": 980, "signups": 45, "github_stars": 12, "waitlist": 8, "mentions": 1, "note": "上午 10 点发，进首页 4 小时"},
        {"name": "X/Twitter", "pv": 540, "signups": 26, "github_stars": 9, "waitlist": 3, "mentions": 1, "note": "9 AM EST 双峰第一条"},
        {"name": "即刻", "pv": 190, "signups": 11, "github_stars": 0, "waitlist": 0, "mentions": 0, "note": "晚 8 点发布"},
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
}


def main():
    ap = argparse.ArgumentParser(description="发布战报生成 —— 指标汇总与达标判定")
    ap.add_argument("--input", help="输入 JSON（product/targets/platforms/hourly_pv）")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--demo", action="store_true", help="用内置样例跑一遍")
    a = ap.parse_args()

    payload = DEMO if a.demo else at.read_json(a.input) if a.input else None
    if payload is None:
        ap.error("需要 --input / --demo 之一")

    r = build(payload, a.outdir)
    s = r["summary"]
    print(f"{s['产品']} 发布战报：PV {s['总 PV']}，注册 {s['总注册']}（{s['PV→注册转化率']}），"
          f"GitHub {s['GitHub 星标']} 星 —— 达标 {s['达标指标']}，{s['整体判定']}")
    for f in r["files"]:
        print(" 产物:", f)
    at.emit(r)


if __name__ == "__main__":
    main()
