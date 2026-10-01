# -*- coding: utf-8 -*-
"""
发布日历排期流程 —— 端到端编排脚本。

编排逻辑（与 SKILL.md 的 DAG 一致）：
  发布日 T0 + 本地时区 → [publish-schedule SOP 规则内置]
    → 节点 1：倒排日历（T-7 预热 → T-3 定稿 → T-1 预检 → T-0 发布 → T+1 战报 → T+7 复盘）
    → 节点 2：T-0 分时区时点表（PH 00:01 PT / X 双峰 / Reddit 工作日 / V2EX 上午10点 / 中文社区晚峰）
              各平台时点换算为本地时间并标 PH 黄金窗口冲突
    → 节点 3：T-1 十项检查清单（可勾选状态由人工回填）
    → 产出：发布日历.xlsx + 发布日 T-0 时间轴.png + publish_calendar.json

失败处理：
  - launch_date 缺失/非法 → 退出码 2 并打印修复提示，不编造日期
  - 发布日为周六/周日 → Reddit 节点自动顺延到周一并在备注标注（工作日规则）
  - 平台名不在支持列表 → 保留在日历但时点表标「需人工补充时点」

用法：
  python run_flow.py --input input.json --outdir out
  python run_flow.py --demo
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
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

# ---------------------------------------------------------------- SOP 规则

# 各平台 T-0 时点（平台本地时间，24h 制）。来源：publish-schedule SOP 时点表。
# PT=UTC-7(夏令时 PDT)，EST=UTC-4(夏令时 EDT)。以官方为准，此处为排期基线。
PLATFORM_SLOTS = {
    "ProductHunt": [("00:01 PT", "上线 + 30 分钟内发 maker comment", -7)],
    "X": [("09:00 EST", "第一峰 thread（链接放回复）", -4), ("20:00 EST", "第二峰带图追推，联动 PH 冲榜", -4)],
    "Reddit": [("09:00 EST", "经验分享帖 + I made this 披露（工作日 8-10AM 带内）", -4)],
    "V2EX": [("10:00 CST", "分享节点发帖（上午 10 点，进首页 4-6 小时有效）", 8)],
    "即刻": [("20:00 CST", "开发花絮帖 + 圈子话题", 8)],
    "小红书": [("20:00 CST", "3-6 张 3:4 图文", 8)],
    "微博": [("20:00 CST", "短帖 + AIGC 标识", 8)],
    "公众号": [("20:30 CST", "长文（故事版/战报版）", 8)],
}

BACKWARD_PLAN = [
    ("T-7", -7, "预热启动：waitlist 页/预告帖上线；素材三件套启动（launch-kit-generate-flow）",
     "素材方向拍板；waitlist 表单可提交（须含退订）"),
    ("T-3", -3, "素材定稿：PH 文案包 / FAQ 口径库（≥15 条）/ 多平台版本",
     "FAQ 逐条确认（不许批处理）；tagline 三选一"),
    ("T-1", -1, "全平台预检：十项检查清单逐项打勾", "每项打勾签字；红线未过 → 延后 24h"),
    ("T-0", 0, "分时区发布 + 评论值守（daily-comment-duty-flow 每 15 分钟）",
     "每次发布人工执行；PH 黄金窗口不排其他动作"),
    ("T+1", 1, "战报：battle-report-generate 五指标达标判定 + 归因", "目标值确认（发布前就该定）"),
    ("T+7", 7, "复盘：留存 + waitlist 转化 + 方向决策（乘胜/止损）", "决策人工做；T+1 建议逐条核对"),
]

CHECKLIST = [
    ("1", "所有链接可点（官网/下载/支付/隐私政策）"),
    ("2", "PH gallery 5 张 1270×760，第 1 张含 tagline"),
    ("3", "X 图 16:9（1600×900）"),
    ("4", "tagline ≤60 字符无句号"),
    ("5", "demo 视频 ≤60s 且 PH 服务器直传"),
    ("6", "价格三页一致（官网/PH/README）"),
    ("7", "账号状态（V2EX 等注册 >30 天）"),
    ("8", "FAQ 口径库 ≥15 条已定稿"),
    ("9", "PH 时区闹钟 ×3（T-30min / T-10min / T0）"),
    ("10", "UTM/统计埋点就位"),
]

REDLINE_ITEMS = {1, 6, 7}  # 红线项：未过 → 延后 24h


def to_local(slot_str, slot_tz_offset, local_offset, base_date):
    """把「HH:MM ±Z」换算为本地日期时间。返回 (日期str, 本地时间str, 跨日bool)。"""
    hm = slot_str.split(" ")[0]
    h, m = int(hm.split(":")[0]), int(hm.split(":")[1])
    utc_h = h - slot_tz_offset
    local_h = utc_h + local_offset
    day_shift = 0
    while local_h >= 24:
        local_h -= 24
        day_shift += 1
    while local_h < 0:
        local_h += 24
        day_shift -= 1
    d = base_date + dt.timedelta(days=day_shift)
    return d.isoformat(), f"{local_h:02d}:{m:02d}", day_shift != 0


def build(payload, outdir):
    try:
        base = dt.date.fromisoformat(str(payload.get("launch_date", "")))
    except ValueError:
        print("[失败处理] launch_date 缺失或非法（需 ISO 日期，如 2026-09-29），流程中止。", file=sys.stderr)
        sys.exit(2)
    local_offset = int(payload.get("local_utc_offset", 8))
    platforms = payload.get("platforms", list(PLATFORM_SLOTS))
    product = payload.get("product", "未命名产品")

    # --- 节点 1：倒排日历 ---
    cal_rows = []
    for label, delta, action, confirm in BACKWARD_PLAN:
        d = base + dt.timedelta(days=delta)
        cal_rows.append({"节点": label, "日期": d.isoformat(),
                         "星期": "周" + "一二三四五六日"[d.weekday()],
                         "动作": action, "人工确认点": confirm, "状态": "待执行"})

    # --- 节点 2：T-0 时点表（本地换算 + 冲突检查） ---
    slot_rows, timeline = [], []
    ph_window = None  # 本地黄金窗口 (开始, 结束)
    for p in platforms:
        slots = PLATFORM_SLOTS.get(p)
        if not slots:
            slot_rows.append({"平台": p, "本地日期": "—", "本地时间": "—",
                              "动作": "（时点未收录，需人工补充）", "备注": "平台不在支持列表",
                              "状态": "待人工补充"})
            continue
        for slot_str, action, tz in slots:
            d_str, t_str, cross = to_local(slot_str, tz, local_offset, base)
            note = ""
            if p == "ProductHunt":
                note = "闹钟 ×3（T-30/T-10/T0）"
                ph_window = (d_str, t_str)
            rows_note = "跨日" if cross else ""
            slot_rows.append({"平台": p, "本地日期": d_str, "本地时间": t_str,
                              "动作": action, "备注": (note + " " + rows_note).strip(),
                              "状态": "待人工执行"})
            timeline.append((f"{p} {t_str}", t_str))

    # 黄金窗口冲突检查：00:01-02:00 PT（本地 3 小时内）不排其他平台
    conflicts = []
    if ph_window:
        ph_d, ph_t = ph_window
        ph_h, ph_m = map(int, ph_t.split(":"))
        for r in slot_rows:
            if r["平台"] in ("ProductHunt",) or r["本地日期"] != ph_d:
                continue
            try:
                h, m = map(int, str(r["本地时间"]).split(":"))
            except ValueError:
                continue
            mins = (h * 60 + m) - (ph_h * 60 + ph_m)
            if 0 <= mins <= 120:
                conflicts.append(f"{r['平台']} {r['本地时间']} 落入 PH 黄金窗口（00:01-02:00 PT 本地段），建议移出")

    # Reddit 工作日规则：周六/周日 → 顺延周一
    wd = base.weekday()
    if wd >= 5:
        for r in slot_rows:
            if r["平台"] == "Reddit":
                monday = (base + dt.timedelta(days=(7 - wd))).isoformat()
                r["备注"] = f"发布日为周末，Reddit 顺延至 {monday}（工作日规则）"

    # --- 节点 3：T-1 检查清单 ---
    chk_rows = [{"#": n, "检查项": item, "红线": "是" if int(n) in REDLINE_ITEMS else "",
                 "结果": "待人工打勾", "备注": ""} for n, item in CHECKLIST]

    summary = {
        "产品": product,
        "发布日 T0": base.isoformat() + "（周" + "一二三四五六日"[wd] + "）",
        "本地时区": f"UTC{'+' if local_offset >= 0 else ''}{local_offset}",
        "平台数": len(platforms),
        "时点条目": len(slot_rows),
        "黄金窗口冲突": len(conflicts),
        "红线检查项": "、".join(f"第{n}项" for n in sorted(REDLINE_ITEMS)),
        "降级规则": "红线项未过 → 全线延后 24 小时；P0 bug → 中止先修后发",
        "说明": "日历/时点由脚本按 SOP 规则计算；发布动作全部人工执行",
    }

    at.ensure_outdir(outdir)
    files = []
    files.append(at.write_excel(
        os.path.join(outdir, "发布日历.xlsx"),
        {
            "倒排日历": cal_rows,
            "T0时点表": slot_rows,
            "T1检查清单": chk_rows,
            "黄金窗口冲突": [{"冲突": c} for c in conflicts] or [{"冲突": "（无）"}],
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"T0时点表": {"状态": "contains:待人工执行"},
                    "T1检查清单": {"红线": "contains:是"}},
        widths={"倒排日历": {"动作": 52, "人工确认点": 40},
                "T0时点表": {"动作": 46, "备注": 30},
                "T1检查清单": {"检查项": 46}},
    ))
    if timeline:
        labels = [t[0] for t in sorted(timeline, key=lambda x: x[1])]
        vals = [int(t[1].split(":")[0]) + int(t[1].split(":")[1]) / 60 for t in sorted(timeline, key=lambda x: x[1])]
        files.append(at.bar_chart(
            os.path.join(outdir, "发布日T0时间轴.png"),
            labels, vals, title=f"{product} T-0 各平台本地发布时点",
            xlabel="本地小时", horizontal=True,
        ))
    js = at.write_json({"summary": summary, "calendar": cal_rows, "slots": slot_rows,
                        "checklist": chk_rows, "conflicts": conflicts,
                        "generated_at": at.stamp(),
                        "note": "SOP 规则计算结果；发布动作全部人工执行"},
                       os.path.join(outdir, "publish_calendar.json"))
    files.append(js)
    return {"files": files, "summary": summary, "conflicts": conflicts}


DEMO = {
    "product": "ClipMate（剪贴板历史工具）",
    "launch_date": "2026-09-29",
    "local_utc_offset": 8,
    "platforms": ["ProductHunt", "X", "Reddit", "V2EX", "即刻"],
}


def main():
    ap = argparse.ArgumentParser(description="发布日历排期流程")
    ap.add_argument("--input", help="输入 JSON（launch_date/local_utc_offset/platforms）")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()

    payload = DEMO if a.demo else at.read_json(a.input) if a.input else None
    if payload is None:
        ap.error("需要 --input / --demo 之一")

    r = build(payload, a.outdir)
    s = r["summary"]
    print(f"{s['产品']} 发布日 {s['发布日 T0']}：{s['平台数']} 平台 {s['时点条目']} 条时点，"
          f"黄金窗口冲突 {s['黄金窗口冲突']} 个")
    for c in r["conflicts"]:
        print(" 冲突:", c)
    for f in r["files"]:
        print(" 产物:", f)
    at.emit(r)


if __name__ == "__main__":
    main()
