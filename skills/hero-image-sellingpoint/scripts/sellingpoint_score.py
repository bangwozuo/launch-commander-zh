# -*- coding: utf-8 -*-
"""
首图卖点提炼 —— 卖点四维评分与排序器。

职责边界：本脚本只做**确定性打分**（演示性/冲击力/受众宽度/差异化加权评分）、
排序、入选判定与产物生成。卖点文案、首图构图、GIF 分镜创意由模型按 prompt.txt 完成。

用法：
  python sellingpoint_score.py --input input.json --outdir out
  python sellingpoint_score.py --demo

产物：
  out/卖点评分清单.xlsx   卖点评分 / 入选清单 / 汇总
  out/卖点评分对比.png    卖点得分条形图
  out/sellingpoint.json   机器可读结果（供智能体/工作流读取）
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

# 四维权重：演示性 35% / 冲击力 25% / 受众宽度 25% / 差异化 15%
# 演示性权重最高——首图和 GIF 的唯一 job 是「让人 3 秒看懂」，讲不出来的卖点不上首图
WEIGHTS = [("demoable", 0.35), ("wow", 0.25), ("breadth", 0.25), ("uniqueness", 0.15)]
DIM_NAMES = {"demoable": "演示性(0/1)", "wow": "冲击力(1-5)", "breadth": "受众宽度(1-5)", "uniqueness": "差异化(1-5)"}

# GIF 分镜模板（按演示性类型给骨架；具体画面由模型填）
GIF_TEMPLATES = {
    "before_after": "分镜 1（0-1.5s）旧方式痛点画面 → 分镜 2（1.5-3s）用产品后同一任务完成 → 分镜 3（3-4s）结果对比定格 + 一句话字幕",
    "speed": "分镜 1（0-1s）按下快捷键/点击 → 分镜 2（1-2.5s）瞬时出结果（不加减速假） → 分镜 3（2.5-3.5s）计时器定格",
    "showcase": "分镜 1（0-2s）主界面全景慢移 → 分镜 2（2-3.5s）招牌功能特写 → 分镜 3（3.5-5s）logo + tagline 定格",
    "flow": "分镜 1（0-1.5s）起点状态 → 分镜 2（1.5-3s）关键操作 2-3 步连招 → 分镜 3（3-4.5s）终点状态 + 结果亮点",
}


def score_feature(f):
    """四维加权 → 0-100 分。demoable 为 0/1，其余 1-5。"""
    parts, weights = {}, {}
    for key, w in WEIGHTS:
        v = f.get(key, 0)
        if key == "demoable":
            norm = 1.0 if v else 0.0
        else:
            v = max(1, min(5, int(v or 1)))
            norm = (v - 1) / 4  # 归一到 0-1
        parts[key] = norm
        weights[key] = w
    total, _detail = at.weighted_score(parts, weights)
    return total * 100


def demo_type(f):
    if not f.get("demoable"):
        return "—（不可演示：建议只做文字卖点，不上 GIF）"
    if any(k in str(f.get("name", "")) + str(f.get("description", "")) for k in ("秒", "快", "speed", "instant")):
        return "speed"
    if any(k in str(f.get("description", "")) for k in ("之前", "以前", "手动", "before")):
        return "before_after"
    if any(k in str(f.get("description", "")) for k in ("流程", "一步", "自动", "workflow")):
        return "flow"
    return "showcase"


def build(payload, outdir):
    product = payload.get("product", "未命名产品")
    features = payload.get("features", [])

    scored = []
    for f in features:
        s = score_feature(f)
        dt = demo_type(f)
        scored.append({
            "功能": f.get("name", "?"),
            "一句话描述": f.get("description", ""),
            "演示性": "可" if f.get("demoable") else "否",
            "冲击力": f.get("wow", "-"),
            "受众宽度": f.get("breadth", "-"),
            "差异化": f.get("uniqueness", "-"),
            "综合得分": round(s, 1),
            "GIF 类型": dt,
            "GIF 分镜骨架": GIF_TEMPLATES.get(dt, "—"),
        })
    scored.sort(key=lambda r: -r["综合得分"])
    for i, r in enumerate(scored, 1):
        r["排名"] = i

    # 入选规则：得分 ≥60 且可演示 → 首图/GIF 候选；取前 5
    selected = [r for r in scored if r["综合得分"] >= 60 and r["演示性"] == "可"][:5]
    sel_names = {r["功能"] for r in selected}
    for r in scored:
        r["入选首图/GIF"] = "✅ 入选" if r["功能"] in sel_names else ""

    # 机器可判的硬约束检查
    checks = []
    n_sel = len(selected)
    if n_sel < 3:
        checks.append(f"入选卖点仅 {n_sel} 个（<3 个）——可演示卖点不足：检查是否把强功能标了 demoable=0，或功能本身需要补录屏")
    if n_sel > 5:
        checks.append("入选超过 5 个——首图只讲 3-5 个卖点，超出部分移到详情页")
    if scored and scored[0]["综合得分"] - (scored[1]["综合得分"] if len(scored) > 1 else 0) < 5:
        checks.append("TOP2 得分差 <5 分——主卖点不突出，首图主视觉会犹豫；用用户访谈或竞品对比补判")
    undemo = [r["功能"] for r in scored if r["演示性"] == "否"]
    if undemo:
        checks.append(f"不可演示功能 {len(undemo)} 个（{'、'.join(undemo)}）——这些不做 GIF，考虑改造成可演示形态（如加 before/after）")
    if not checks:
        checks.append("数量与梯度检查通过（3-5 个可演示卖点 + TOP2 有分差）")

    summary = {
        "产品": product,
        "功能总数": len(features),
        "入选卖点数": n_sel,
        "TOP1": scored[0]["功能"] if scored else "—",
        "TOP1 得分": scored[0]["综合得分"] if scored else "—",
        "TOP2 分差": (round(scored[0]["综合得分"] - scored[1]["综合得分"], 1) if len(scored) > 1 else "—"),
        "入选规则": "得分 ≥60 且可演示，取前 5；首图主视觉 = TOP1",
        "说明": "评分为脚本加权计算；维度打分（wow/breadth/uniqueness）须由模型按 prompt.txt 结合用户证据评定",
    }

    at.ensure_outdir(outdir)
    files = []
    files.append(at.write_excel(
        os.path.join(outdir, "卖点评分清单.xlsx"),
        {
            "卖点评分": scored or [{"功能": "（无功能数据）"}],
            "入选清单": selected or [{"功能": "（无可演示卖点）", "GIF 分镜骨架": "检查 demoable 标注"}],
            "硬约束检查": [{"#": i + 1, "检查": c} for i, c in enumerate(checks)],
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"卖点评分": {"入选首图/GIF": "contains:入选"}},
        widths={"卖点评分": {"一句话描述": 34, "GIF 分镜骨架": 56}, "硬约束检查": {"检查": 64}},
    ))
    if scored:
        files.append(at.bar_chart(
            os.path.join(outdir, "卖点评分对比.png"),
            [r["功能"] for r in scored],
            [r["综合得分"] for r in scored],
            title=f"{product} 卖点四维加权得分",
            ylabel="得分（0-100）", horizontal=True,
        ))
    js = at.write_json({"summary": summary, "ranked": scored, "checks": checks,
                        "generated_at": at.stamp(),
                        "note": "加权评分结果；维度证据与首图文案由模型按 prompt.txt 完成"},
                       os.path.join(outdir, "sellingpoint.json"))
    files.append(js)
    return {"files": files, "summary": summary, "selected": selected, "checks": checks}


DEMO = {
    "product": "ClipMate（剪贴板历史工具）",
    "audience": "Windows 重度文字工作者",
    "features": [
        {"name": "全局历史搜索", "description": "Ctrl+Shift+V 秒搜三个月内所有剪贴记录", "demoable": 1, "wow": 5, "breadth": 5, "uniqueness": 3},
        {"name": "代码片段纯粘贴", "description": "粘贴代码自动去格式，不再手动清理缩进", "demoable": 1, "wow": 3, "breadth": 3, "uniqueness": 4},
        {"name": "截图 OCR 取字", "description": "截图里的文字一键变成可复制文本", "demoable": 1, "wow": 4, "breadth": 4, "uniqueness": 4},
        {"name": "端到端加密同步", "description": "设备间同步剪贴板，密钥本地保存", "demoable": 0, "wow": 2, "breadth": 2, "uniqueness": 3},
        {"name": "低内存占用", "description": "常驻内存 <50MB，比同类省一半", "demoable": 1, "wow": 2, "breadth": 4, "uniqueness": 2},
    ],
}


def main():
    ap = argparse.ArgumentParser(description="首图卖点提炼 —— 四维加权评分")
    ap.add_argument("--input", help="输入 JSON（product/features[]）")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--demo", action="store_true", help="用内置样例跑一遍")
    a = ap.parse_args()

    payload = DEMO if a.demo else at.read_json(a.input) if a.input else None
    if payload is None:
        ap.error("需要 --input / --demo 之一")

    r = build(payload, a.outdir)
    s = r["summary"]
    print(f"{s['产品']}：功能 {s['功能总数']} 个，入选 {s['入选卖点数']} 个，TOP1={s['TOP1']}（{s['TOP1 得分']} 分）")
    for c in r["checks"]:
        print(" 检查:", c)
    for f in r["files"]:
        print(" 产物:", f)
    at.emit(r)


if __name__ == "__main__":
    main()
