# 测试报告

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行 | ✅ PASS |
| prompt.txt 深度区块（四维权重 / 入选规则 / 首图四原则 / GIF 纪律 / 落选证据） | ✅ PASS |
| 无占位符残留 | ✅ PASS |
| 无 API Key / 无模型调用 | ✅ PASS |

## 二、脚本实跑

**命令**：

```bash
python scripts/sellingpoint_score.py --demo
python scripts/sellingpoint_score.py --input examples/input.json --outdir out
```

**运行环境**：Python 3.13（绝对路径解释器）/ openpyxl / matplotlib

| 项 | 结果 |
|---|---|
| 退出码 | 0（demo 与 input 双跑均 0） |
| 评分结果 | 5 功能 → 入选 4，TOP1=全局历史搜索 90.0 分，TOP2 分差 10.0 |
| 一票否决生效 | 端到端加密同步（demoable=0）得分 20.0 落选 |
| 产物 1 | `out/卖点评分清单.xlsx`（9.7 KB，4 sheet，入选行标绿） |
| 产物 2 | `out/卖点评分对比.png`（32.0 KB 横向条形图） |
| 产物 3 | `out/sellingpoint.json`（3.3 KB） |
| 耗时 | < 2 s |

### 评分核对（抽查 TOP1）

| 项 | 值 | 手工核对 |
|---|---|---|
| demoable=1 → 归一 | 1.0 × 0.35 | ✅ |
| wow=5 → 归一 | (5-1)/4 = 1.0 × 0.25 | ✅ |
| breadth=5 → 归一 | 1.0 × 0.25 | ✅ |
| uniqueness=3 → 归一 | (3-1)/4 = 0.5 × 0.15 = 0.075 | ✅ |
| 合计 | 0.35+0.25+0.25+0.075 = 0.925 → **90.0**（×100） | ✅ 一致 |

### 硬约束检查核对

| 检查项 | demo 样例触发 |
|---|---|
| 入选 <3 个 | 未触发（4 个入选）|
| 入选 >5 个 | 未触发 |
| TOP2 分差 <5 | 未触发（分差 10.0）|
| 不可演示功能 | **触发**（端到端加密同步，给出改造建议）|

## 三、边界与已知限制

| 限制 | 说明 |
|---|---|
| 维度分主观 | 脚本只管加权计算；wow/breadth/uniqueness 的打分须挂证据，由模型复核 |
| GIF 类型识别 | 基于名称/描述关键词推断（speed/before_after/flow/showcase），歧义时模型指定 |
| 不产出视觉稿 | 输出是分镜骨架与画面构成，实际做图/录屏由视觉工具完成 |
| 单一产品维度 | 不做多产品对比选型 |

## 四、结论

**通过。** 加权计算与手工核对一致，一票否决与硬约束检查全部生效，产物真实
（Excel/PNG/JSON）。demoable=0 的「自己最得意的功能」被正确挡在首图外。

---

*测试报告基于真实实跑输出生成 · 2026-09-30*
