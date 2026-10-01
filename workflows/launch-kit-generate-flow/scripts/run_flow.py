# -*- coding: utf-8 -*-
"""
发布素材包生成流程 —— 端到端编排脚本。

编排逻辑（与 SKILL.md 的 DAG 一致）：
  产品信息（功能列表 + PH 文案要点 + FAQ 素材）
    → 节点 1：[hero-image-sellingpoint] 四维评分选卖点（scripts/sellingpoint_score.py）
    → 节点 2：内置 PH 文案包硬约束校验
      （tagline ≤60 字符无句号 / gallery 5 张 1270×760 / demo 视频 ≤60s /
        价格三处一致 / FAQ 条数 ≥15）
    → 节点 3：内置 FAQ 覆盖度校验（六类质疑每类 ≥2）
    → 产出：素材包校验清单.xlsx + kit_result.json
      （PH 文案与 FAQ 文本由模型按 producthunt-copy / faq-pregenerate 生成，本脚本只做硬约束校验）

失败处理：
  - 上游 sellingpoint_score 退出码 != 0 或产物缺失 → 中止并打印错误
  - tagline 缺失 → 校验项标「缺失」而非失败（文案可能未写，列待办）
  - FAQ 六类覆盖不足 → 列缺口清单，不阻断（T-3 前补齐即可）
  - 价格不一致 → 红线项，判定「不可进入 T-1」
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

SP_SCRIPT = os.path.join(REPO, "skills", "hero-image-sellingpoint", "scripts", "sellingpoint_score.py")

FAQ_CATEGORIES = ["价值质疑", "价格质疑", "隐私/安全", "可持续性", "平台/兼容", "边界/限制"]


def check_tagline(tagline):
    t = str(tagline or "").strip()
    if not t:
        return "缺失", "未提供 tagline——producthunt-copy 三候选待产出"
    n = len(t)
    if n > 60:
        return "❌", f"{n} 字符 > 60 上限，重写（不截断）"
    if t.endswith("。") or t.endswith("."):
        return "❌", "以句号结尾——列表页拖沓，去掉"
    return "✅", f"{n} 字符（≤60）"


def main():
    ap = argparse.ArgumentParser(description="发布素材包生成流程")
    ap.add_argument("--input", help="流程输入 JSON（product/features/ph_copy/faq_stats）")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()

    at.ensure_outdir(a.outdir)
    if a.demo:
        payload_path = os.path.join(a.outdir, "_demo_input.json")
        payload = {
            "product": "ClipMate（剪贴板历史工具）",
            "tagline": "Your clipboard, finally searchable",
            "gallery_count": 5,
            "gallery_size": "1270x760",
            "demo_video_seconds": 45,
            "price_pages": {"官网": "Free + Pro $8/mo", "ProductHunt": "Free + Pro $8/mo", "README": "Free + Pro $8/mo"},
            "faq_total": 8,
            "faq_categories": {"价值质疑": 2, "价格质疑": 2, "隐私/安全": 1, "可持续性": 1, "平台/兼容": 1, "边界/限制": 1},
            "features": [
                {"name": "全局历史搜索", "description": "Ctrl+Shift+V 秒搜三个月内所有剪贴记录", "demoable": 1, "wow": 5, "breadth": 5, "uniqueness": 3},
                {"name": "代码片段纯粘贴", "description": "粘贴代码自动去格式，不再手动清理缩进", "demoable": 1, "wow": 3, "breadth": 3, "uniqueness": 4},
                {"name": "截图 OCR 取字", "description": "截图里的文字一键变成可复制文本", "demoable": 1, "wow": 4, "breadth": 4, "uniqueness": 4},
                {"name": "端到端加密同步", "description": "设备间同步剪贴板，密钥本地保存", "demoable": 0, "wow": 2, "breadth": 2, "uniqueness": 3},
                {"name": "低内存占用", "description": "常驻内存 <50MB，比同类省一半", "demoable": 1, "wow": 2, "breadth": 4, "uniqueness": 2},
            ],
        }
        at.write_json(payload, payload_path)
    elif a.input:
        payload_path = a.input
        payload = at.read_json(a.input)
    else:
        ap.error("需要 --input / --demo 之一")

    # --- 节点 1：上游卖点评分 ---
    r = subprocess.run(
        [sys.executable, SP_SCRIPT, "--input", payload_path, "--outdir", a.outdir],
        cwd=FLOW_DIR, capture_output=True, text=True, timeout=180,
    )
    if r.returncode != 0:
        print(f"[失败处理] 上游技能 hero-image-sellingpoint 退出码 {r.returncode}，流程中止。", file=sys.stderr)
        print(r.stderr[-800:], file=sys.stderr)
        sys.exit(1)
    sp_js = os.path.join(a.outdir, "sellingpoint.json")
    if not os.path.exists(sp_js):
        print(f"[失败处理] 上游产物 {sp_js} 缺失，流程中止。", file=sys.stderr)
        sys.exit(1)
    sp = at.read_json(sp_js)

    # --- 节点 2：PH 文案包硬约束校验 ---
    checks = []
    verdict_tag, note_tag = check_tagline(payload.get("tagline"))
    checks.append({"件": "tagline", "标准": "≤60 字符、无句号", "结果": verdict_tag, "说明": note_tag,
                   "红线": ""})

    gc = payload.get("gallery_count")
    gs = str(payload.get("gallery_size", ""))
    if gc == 5 and gs == "1270x760":
        checks.append({"件": "gallery", "标准": "5 张 1270×760（第 1 张含 tagline）", "结果": "✅", "说明": f"{gc} 张 / {gs}", "红线": ""})
    else:
        checks.append({"件": "gallery", "标准": "5 张 1270×760", "结果": "❌", "说明": f"当前 {gc} 张 / {gs or '未提供'}", "红线": ""})

    vid = payload.get("demo_video_seconds")
    if vid is None:
        checks.append({"件": "demo 视频", "标准": "≤60s 且 PH 服务器直传", "结果": "缺失", "说明": "时长未提供", "红线": ""})
    elif vid <= 60:
        checks.append({"件": "demo 视频", "标准": "≤60s 且 PH 服务器直传", "结果": "✅", "说明": f"{vid}s", "红线": ""})
    else:
        checks.append({"件": "demo 视频", "标准": "≤60s 且 PH 服务器直传", "结果": "❌", "说明": f"{vid}s 超长，剪辑到 60s 内", "红线": ""})

    prices = payload.get("price_pages", {})
    uniq = {str(v).strip() for v in prices.values()}
    if not prices:
        checks.append({"件": "价格一致性", "标准": "官网/PH/README 逐字一致", "结果": "缺失", "说明": "未提供各页价格", "红线": "是"})
    elif len(uniq) == 1:
        checks.append({"件": "价格一致性", "标准": "官网/PH/README 逐字一致", "结果": "✅", "说明": " / ".join(f"{k}:{v}" for k, v in prices.items()), "红线": ""})
    else:
        checks.append({"件": "价格一致性", "标准": "官网/PH/README 逐字一致", "结果": "❌",
                       "说明": "价格打架：" + " / ".join(f"{k}:{v}" for k, v in prices.items()), "红线": "是"})

    # --- 节点 3：FAQ 覆盖度校验 ---
    faq_total = payload.get("faq_total", 0)
    faq_cats = payload.get("faq_categories", {})
    total_ok = faq_total >= 15
    checks.append({"件": "FAQ 总量", "标准": "≥15 条", "结果": "✅" if total_ok else "⚠️ 未达标",
                   "说明": f"当前 {faq_total} 条" + ("" if total_ok else "，T-3 前补齐"), "红线": ""})
    gaps = [c for c in FAQ_CATEGORIES if faq_cats.get(c, 0) < 2]
    checks.append({"件": "FAQ 六类覆盖", "标准": "每类 ≥2 条", "结果": "✅" if not gaps else "⚠️ 有缺口",
                   "说明": "缺口：" + "、".join(gaps) if gaps else "六类全部达标", "红线": ""})

    redline_fail = any(c["红线"] == "是" and c["结果"] == "❌" for c in checks)
    overall = "❌ 不可进入 T-1（红线未过）" if redline_fail else ("✅ 可进入 T-1" if all(c["结果"] in ("✅",) for c in checks) else "⚠️ 补齐非红线项后进入 T-1")

    summary = {
        "产品": payload.get("product", "未提供"),
        "TOP1 卖点": (sp.get("summary", {}) or {}).get("TOP1", "—"),
        "入选卖点数": (sp.get("summary", {}) or {}).get("入选卖点数", "—"),
        "硬约束检查": len(checks),
        "通过项": sum(1 for c in checks if c["结果"] == "✅"),
        "红线未过": sum(1 for c in checks if c["红线"] == "是" and c["结果"] == "❌"),
        "FAQ 缺口类": "、".join(gaps) or "无",
        "整体判定": overall,
        "说明": "卖点评分为脚本计算；PH 文案与 FAQ 文本由 producthunt-copy / faq-pregenerate 生成；本脚本只做硬约束校验",
    }

    xlsx = at.write_excel(
        os.path.join(a.outdir, "素材包校验清单.xlsx"),
        {
            "硬约束校验": checks,
            "入选卖点": sp.get("ranked", [])[:5] or [{"功能": "（无）"}],
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"硬约束校验": {"结果": "contains:❌", "红线": "contains:是"}},
        widths={"硬约束校验": {"标准": 34, "说明": 48}},
    )

    result = {
        "flow": "launch-kit-generate-flow",
        "steps": [
            {"step": 1, "skill": "hero-image-sellingpoint", "status": "ok", "output": sp_js},
            {"step": 2, "skill": "（内置）PH 文案包硬约束校验", "status": "ok"},
            {"step": 3, "skill": "（内置）FAQ 覆盖度校验", "status": "ok", "output": xlsx},
        ],
        "summary": summary,
        "checks": checks,
        "files": [xlsx, sp_js],
        "generated_at": at.stamp(),
    }
    at.write_json(result, os.path.join(a.outdir, "kit_result.json"))
    print(f"素材包校验：通过 {summary['通过项']}/{len(checks)}，红线未过 {summary['红线未过']} —— {overall}")
    for f in result["files"] + [os.path.join(a.outdir, 'kit_result.json')]:
        print(" 产物:", f)
    at.emit(result)


if __name__ == "__main__":
    main()
