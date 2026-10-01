# -*- coding: utf-8 -*-
"""
多平台文案适配流程 —— 端到端编排脚本。

编排逻辑（与 SKILL.md 的 DAG 一致）：
  各平台文案版本（platform-format-adapt 产出）→ 内置规格校验：
    节点 1：平台硬规格校验（X ≤280 字符、V2EX 标题 ≤40 字、即刻 ≤500 字、
            小红书标题 ≤20 正文 ≤1000、tag ≤2 个、首条链接检查）
    节点 2：双语数字口径比对（bilingual-switch 事实骨架的机器可查部分：
            英文版与中文版出现的数字集合必须一致——0.3s/10万条/$8 漂移即拦截）
  → 产出：适配校验清单.xlsx + adapt_result.json

失败处理：
  - 平台未收录 → 标「需人工核对官方规格」，不编造限制
  - 超长 → ❌ 并给出超出量；链接在首条 → ❌（X 降权规则）
  - 数字口径不一致 → 列出两边数字集合差异（红线：事实漂移）
  - 单语言版本（无双语对）→ 跳过口径比对，标「单语言」

用法：
  python run_flow.py --input input.json --outdir out
  python run_flow.py --demo
"""
from __future__ import annotations

import argparse
import json
import os
import re
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

# 平台硬规格（与 platform-format-adapt 规格表一致，T-3 检查基线）
SPECS = {
    "X": {"body_max": 280, "media": "16:9（1600×900）", "first_link_allowed": False, "tag_max": 2},
    "Reddit": {"body_max": None, "media": "按版规", "must_disclose": "I made this"},
    "V2EX": {"title_max": 40, "body_max": None, "media": "正文不放图"},
    "即刻": {"body_max": 500, "media": "1-3 张 3:4"},
    "小红书": {"title_max": 20, "body_max": 1000, "media": "3-6 张 3:4"},
    "ProductHunt": {"tagline_max": 60},
    "微博": {"body_max": 2000},
}

NUM_PAT = re.compile(r"\d+(?:\.\d+)?")


def extract_numbers(text):
    """抽取文案中的数字集合（用于双语口径比对）。中文「N万」折算为 N*10（万→十位）
    并从原文移除，避免同一短语双重计数。"""
    nums = set()
    def _wan(m):
        nums.add(str(int(float(m.group(1)) * 10)))  # 10万 → 100（对齐 100k）
        return " "
    text = re.sub(r"(\d+(?:\.\d+)?)\s*万", _wan, text)
    for m in NUM_PAT.findall(text):
        nums.add(m)
    return nums


def check_platform(name, copy):
    rows = []
    spec = SPECS.get(name)
    body = str(copy.get("body", ""))
    title = str(copy.get("title", "") or "")

    if spec is None:
        rows.append({"平台": name, "检查项": "规格收录", "结果": "⚠️", "说明": "平台未收录——需人工核对官方规格，不编造限制"})
        return rows

    if spec.get("title_max"):
        lim = spec["title_max"]
        ok = len(title) <= lim and bool(title)
        rows.append({"平台": name, "检查项": f"标题 ≤{lim} 字", "结果": "✅" if ok else "❌",
                     "说明": f"{len(title)} 字" if title else "标题缺失"})
    if spec.get("body_max"):
        lim = spec["body_max"]
        n = len(body)
        rows.append({"平台": name, "检查项": f"正文 ≤{lim} 字", "结果": "✅" if n <= lim else "❌",
                     "说明": f"{n} 字" + (f"，超出 {n - lim}" if n > lim else "")})
    if spec.get("tag_max") is not None:
        tags = copy.get("tags", []) or []
        n = len(tags)
        rows.append({"平台": name, "检查项": f"tag ≤{spec['tag_max']} 个", "结果": "✅" if n <= spec["tag_max"] else "❌",
                     "说明": f"{n} 个"})
    if spec.get("first_link_allowed") is False:
        has_link = bool(re.search(r"https?://|t\.co/", body))
        rows.append({"平台": name, "检查项": "首条不带链接（防降权）", "结果": "❌ 链接放回复" if has_link else "✅",
                     "说明": "首条含链接" if has_link else "正文无链接"})
    if spec.get("must_disclose"):
        ok = spec["must_disclose"].lower() in body.lower()
        rows.append({"平台": name, "检查项": f"利益相关披露（{spec['must_disclose']}）", "结果": "✅" if ok else "❌",
                     "说明": "已披露" if ok else "未披露——Reddit 不披露被识破=版封"})
    return rows


def main():
    ap = argparse.ArgumentParser(description="多平台文案适配流程")
    ap.add_argument("--input", help="流程输入 JSON（copies[]）")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()

    at.ensure_outdir(a.outdir)
    if a.demo:
        payload_path = os.path.join(a.outdir, "_demo_input.json")
        payload = {
            "copies": [
                {"platform": "X", "body": "I lost my 7th API key last year. So I spent two years building ClipMate: every snippet you copy on Windows, searchable for 3 months in 0.3s (tested on 100k entries). Local storage only, never uploaded. Free + Pro $8/mo. Details: https://clipmate.site", "tags": ["buildinpublic", "indiedev"], "lang": "en"},
                {"platform": "V2EX", "title": "剪贴板历史工具 ClipMate：本地存储，Ctrl+Shift+V 秒搜 3 个月记录", "body": "做这个东西的原因：去年第 7 次弄丢 API key。所有记录只存本机 SQLite，搜索 0.3 秒命中（10 万条实测）。免费 + Pro $8/月。", "lang": "zh"},
                {"platform": "即刻", "body": "做了两年，我的剪贴板工具终于要发了。Ctrl+Shift+V 秒搜 3 个月记录，0.3 秒命中（10 万条实测），只存本机不上传。免费 + Pro $8/月。", "lang": "zh"},
                {"platform": "小红书", "title": "这个剪贴板工具也太能打了吧", "body": "丢 API key 丢到破防之后自己做了一个：Ctrl+Shift+V 秒搜 3 个月记录（0.3 秒，10 万条实测），截图 OCR 取字，粘贴去格式，只存本机。免费 + Pro 每月 8 美元。", "tags": ["效率工具", "独立开发"], "lang": "zh"},
                {"platform": "知乎", "body": "（知乎专栏稿）", "lang": "zh"},
            ]
        }
        at.write_json(payload, payload_path)
    elif a.input:
        payload_path = a.input
        payload = at.read_json(a.input)
    else:
        ap.error("需要 --input / --demo 之一")

    copies = payload.get("copies", [])

    # --- 节点 1：平台硬规格校验 ---
    spec_rows = []
    for c in copies:
        spec_rows.extend(check_platform(c.get("platform", "?"), c))

    # --- 节点 2：双语数字口径比对（en↔zh 配对按 lang 字段） ---
    parity_rows = []
    en = [c for c in copies if c.get("lang") == "en"]
    zh = [c for c in copies if c.get("lang") == "zh"]
    if en and zh:
        en_nums, zh_nums = set(), set()
        for c in en:
            en_nums |= extract_numbers(str(c.get("body", "")) + str(c.get("title", "") or ""))
        for c in zh:
            zh_nums |= extract_numbers(str(c.get("body", "")) + str(c.get("title", "") or ""))
        only_en = sorted(en_nums - zh_nums)
        only_zh = sorted(zh_nums - en_nums)
        parity_rows.append({
            "比对": "英文版 vs 中文版 数字口径",
            "结果": "✅" if not (only_en or only_zh) else "❌ 红线：事实漂移",
            "仅英文版出现": "、".join(only_en) or "—",
            "仅中文版出现": "、".join(only_zh) or "—",
            "处置": "口径一致" if not (only_en or only_zh) else "数字是两版共同的信任资产——一边删/改 = 口径漂移，恢复一致",
        })
    else:
        parity_rows.append({"比对": "双语数字口径", "结果": "— 单语言版本",
                            "仅英文版出现": "—", "仅中文版出现": "—",
                            "处置": "无双语对，跳过比对（bilingual-switch 产出双语后复跑）"})

    n_fail = sum(1 for r in spec_rows if str(r["结果"]).startswith("❌")) + \
             sum(1 for r in parity_rows if str(r["结果"]).startswith("❌"))
    overall = "✅ 全部通过" if n_fail == 0 else f"❌ {n_fail} 项未过，修正后复跑"

    summary = {
        "平台数": len(copies),
        "规格检查条目": len(spec_rows),
        "规格未过": sum(1 for r in spec_rows if str(r["结果"]).startswith("❌")),
        "口径比对": parity_rows[0]["结果"] if parity_rows else "—",
        "整体判定": overall,
        "说明": "规格与数字口径为脚本校验；语感重写质量由 platform-format-adapt / bilingual-switch 的模型层负责",
    }

    xlsx = at.write_excel(
        os.path.join(a.outdir, "适配校验清单.xlsx"),
        {
            "平台规格校验": spec_rows or [{"平台": "（无）"}],
            "双语口径比对": parity_rows,
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"平台规格校验": {"结果": "contains:❌"}, "双语口径比对": {"结果": "contains:❌"}},
        widths={"平台规格校验": {"说明": 44}, "双语口径比对": {"处置": 52}},
    )
    js = at.write_json({"summary": summary, "spec_checks": spec_rows, "parity": parity_rows,
                        "generated_at": at.stamp(),
                        "note": "规格与口径机器校验；语感重写由模型层负责"},
                       os.path.join(a.outdir, "adapt_result.json"))
    print(f"适配校验：{summary['规格检查条目']} 条规格检查，未过 {summary['规格未过']}；口径比对 {summary['口径比对']}")
    for f in [xlsx, js]:
        print(" 产物:", f)
    at.emit({"summary": summary, "files": [xlsx, js]})


if __name__ == "__main__":
    main()
