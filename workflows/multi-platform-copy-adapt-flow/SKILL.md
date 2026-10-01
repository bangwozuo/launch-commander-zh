---
name: multi-platform-copy-adapt-flow
description: 独立开发者多平台文案适配工作流。platform-format-adapt 重写各平台原生版本（X/V2EX/即刻/小红书）+ bilingual-switch 双语各自成文，脚本做模型做不了的硬校验：X ≤280字符/tag≤2/首条无链接防降权、V2EX 标题≤40、小红书 20+1000、Reddit I made this 披露、双语数字口径比对（10万↔100k 折算对齐，漂移=红线）。当用户需要一稿多发、多平台改写校验、双语口径检查时使用。
---

# 多平台文案适配流程

主稿进，**五平台原生版本 + 校验全绿**出。重写由模型做，字数/链接/披露/数字口径
这些硬规则由脚本查——「发完才发现」的三类事故全部前移到发布前拦截。

## 元信息

| 字段 | 值 |
|------|-----|
| ID | `de_dev_02_wf02` |
| 类型 | **`composite`（复合技能/工作流）** |
| 所属员工 | 发布指挥官 |
| 阶段 | `P0` |
| 复杂度 | `S` |
| 触发方式 | 事件（主稿/卖点确认后，T-4 至 T-3） |
| ROI | 省 3h/次 ≈ ¥240/次；X 降权/Reddit 版封/口径漂移三类事故前移拦截 |
| 资产形态 | 可跑编排脚本 + 深度流程提示词（无模型调用依赖、无 API Key） |

## 编排的原子技能

| # | 原子技能 | 能力 |
|---|---------|------|
| 1 | [平台格式适配](../../skills/platform-format-adapt/) | 各平台原生重写 + 规格表（重写位） |
| 2 | [中英双语切换](../../skills/bilingual-switch/) | 双语各自成文 + 事实骨架（双语位） |

## 步骤链路（DAG）

```mermaid
flowchart LR
    IN["主稿<br/>PH版/产品说明"] --> S1["platform-format-adapt<br/>各平台原生重写"]
    S1 --> S2["bilingual-switch<br/>英中各自成文"]
    S2 --> S3["内置: 平台规格校验<br/>字数/tag/链接/披露"]
    S3 --> S4["内置: 双语数字口径比对<br/>10万↔100k 折算"]
    S4 --> O1["适配校验清单.xlsx"]
    O1 -->|❌| S1
    O1 -->|✅| H1["人工确认后发布<br/>版本交接 publish-calendar-flow"]
```

## 步骤明细

| # | 步骤 | 技能资产 | 输入 | 输出 | 失败处理 |
|---|------|---------|------|------|---------|
| 1 | 平台重写 | `platform-format-adapt` | 主稿 + 平台列表 | copies[]（title/body/tags/lang） | 语感模型判断，重要平台母语者终审 |
| 2 | 规格校验 | 本流程（内置） | copies[] | 逐项 ✅/❌/⚠️ | 超长给超出量；链接/披露缺失 ❌；未收录标人工核对 |
| 3 | 口径比对 | 本流程（内置） | en+zh 版本 | 数字集合差集 | 漂移=红线列差异；无双语对标「单语言」跳过 |

## 输入规格

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `copies` | array | ✅ | 各平台版本（platform/title/body/tags/lang） |

## 输出规格

| 字段 | 类型 | 说明 |
|------|------|------|
| `spec_checks` | array | 平台硬规格逐项结果 |
| `parity` | array | 双语数字口径比对（漂移=红线） |
| `deliverable` | file | `out/适配校验清单.xlsx`（❌ 标红） |

## 错误处理

| 情况 | 处理方式 |
|------|---------|
| 平台未收录 | ⚠️「需人工核对官方规格」，不编造限制 |
| 超长 | ❌ 并给出超出量（重写不是截断） |
| X 首条含链接 | ❌「链接放回复」 |
| Reddit 未披露 I made this | ❌（版封风险） |
| 数字口径漂移 | ❌ 红线，列两边差集 |
| 无双语对 | 标「单语言」跳过比对 |

## 使用步骤

### 方式一：跑脚本（校验已产出的版本）

```bash
python3 <FLOW_DIR>/scripts/run_flow.py --input input.json --outdir out
python3 <FLOW_DIR>/scripts/run_flow.py --demo
```

### 方式二：手动编排（任意 AI 平台）

1. platform-format-adapt 重写各平台版本；bilingual-switch 出英中两版
2. 对照 prompt 中规格表逐项核对（字数人工数，口径逐条比）
3. 未过项回重写位修正后复跑，不人工微调绕过

## 验收标准

- [x] DAG 节点为本仓真实技能 slug（platform-format-adapt / bilingual-switch）
- [x] 规格校验脚本可查（链接/披露/字数），超出量显式给出
- [x] 双语数字口径机器比对（万折算对齐），漂移=红线
- [x] 失败处理可演练（未收录平台/漂移/无披露/单语言）

## 边界（不做的事）

- ❌ 不代写重写文案（模型位负责），只做编排与硬校验
- ❌ 中文数字（三个月/两年）不计入口径比对——重写规范统一阿拉伯数字
- ❌ 不编造未收录平台的规格
- ❌ 不建议任何绕过平台规则的写法（谐音导流等）

## 调用示例

**输入**（`examples/input.json`，节选）：

```json
{
  "copies": [
    {"platform": "X", "body": "I lost my 7th API key... searchable for 3 months in 0.3s (tested on 100k entries)... https://clipmate.site", "lang": "en"},
    {"platform": "V2EX", "title": "剪贴板历史工具 ClipMate：本地存储，Ctrl+Shift+V 秒搜 3 个月记录", "body": "…0.3 秒命中（10 万条实测）…", "lang": "zh"}
  ]
}
```

**输出**（run_flow.py 实跑，退出码 0）：8 条检查未过 2（X 首条链接 ❌、V2EX 标题
44 字 ❌）；口径比对 ✅（10 万↔100k 折算对齐）。详见 examples/output.md。

## 所属工作流

本资产为复合技能（工作流）：产出版本交接 `publish-calendar-flow` 排期；
上游卖点来自 `launch-kit-generate-flow`。

## 合规声明

- 输出标注「AI 生成内容」；各平台版本人工确认后发布
- Reddit 披露利益相关为硬要求，流程代查但责任在发布者
- 平台 AIGC 标识按现行要求执行；规格以官方最新为准

---

*本技能遵循 [bangwozuo 数字员工资产规范](https://github.com/bangwozuo/digital-employee-spec) v3.0*
