---
name: comment-emotion-detect
description: 独立开发者发布日评论情绪识别。五类标签（正/负/中/疑/风险）+ 六类风险子类（刷榜指控、隐私质疑、退款诉求、抄袭指控、存续质疑、水军指控），按 P0-P4 优先级排队并给响应 SLA（PH 首日评论 30 分钟内响应）。带 Python 脚本产出 Excel 分类清单 + 情绪分布 PNG。当用户需要发布日评论值守、评论分类、负面评论预警、评论区排优先级时使用。
---

# 评论情绪识别

把发布日评论流切成「该立刻回 / 该认真回 / 该记录 / 不用回」四档，P0 风险 30 分钟内
升级给开发者本人。PH 首日评论响应速度直接影响排名，识别慢 = 排名亏。

不做的事：不写回复内容（走 reply-drafting）、不执行自动回复、不删任何评论。

## 元信息

| 字段 | 值 |
|------|-----|
| ID | `de_dev_02_sk07` |
| 类型 | **`atomic`（原子技能）** |
| 所属员工 | 发布指挥官 |
| 能力族 | 检测判断型 · 情绪分类与风险预警 |
| 复杂度 | `M` |
| 阶段 | `P1` |
| 复用度 | 中（T+1 战报复用评论数据） |
| 资产形态 | 深度提示词 + Python 脚本（无模型调用、无 API Key） |

## 能力描述

1. **五类情绪标签**：🟢 正面 / ⚠️ 负面 / ⚪ 中性 / 🔵 疑问 / 🔴 风险，带否定翻转与
   「功能请求≠好评」修正
2. **六类风险子类**：刷榜指控、安全/隐私质疑、退款诉求、抄袭/竞品指控、存续质疑、
   水军指控——每类有标准处置动作与 SLA
3. **优先级队列**：P0 风险（30 分钟）→ P1 负面（PH 首日 30 分钟）→ P2 疑问（2 小时）
   → P3 正面（24 小时）→ P4 中性（48 小时）
4. **健康度基线**：正面占比 ≥60% 且风险=0 为健康；负面 >20% 触发置顶澄清集中响应；
   疑问 >30% 说明素材有盲区

## 输入规格

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `comments` | array | ✅ | 评论流，每条含 `text`（原文尽量全文）+ `user` + `platform` |
| `platform` | string | ⬜ | 主平台：ProductHunt / Reddit / V2EX / X / 即刻 / 微博 / 公众号 / 通用 |
| `product` | string | ⬜ | 产品名，用于语境判断 |

## 输出规格

- `summary`：五类计数、正面占比、P0/P1 数量、健康线判定
- `queue`：优先级队列（P0→P4），每条带风险子类 / SLA / 建议动作 / 待人工确认状态

**产物文件**：

| 文件 | 内容 |
|---|---|
| `out/评论分类清单.xlsx` | 优先级队列（风险行标红）/ 分类明细 / 汇总 |
| `out/情绪分布.png` | 五类情绪占比饼图 |
| `out/emotion_scan.json` | 机器可读结果，供工作流（daily-comment-duty-flow）读取 |

## 使用步骤

### 方式一：纯提示词（最快，含语境判断）

1. 把 `prompt.txt` 全部内容粘贴为系统提示词
2. 提供评论流（全文，标注平台）
3. 得到情绪总览 + 优先级队列 + 需模型复核项（反讽/刷量号）

### 方式二：带脚本（词表精确打分 + 产出 Excel/PNG）

```bash
python3 <SKILL_DIR>/scripts/emotion_scan.py --input input.json --outdir out
python3 <SKILL_DIR>/scripts/emotion_scan.py --demo        # 无输入也能看效果
```

**分工**：脚本做词表打分、否定翻转、风险规则扫描、P0-P4 排队（不漏、不猜）；
模型做反讽识别、刷量号复核、老用户差评归因（脚本做不了的）。两者结果交叉核对。

## 边界（不做的事）

- ❌ 不删评论、不建议删帖——「承认+给方案」是负面评论唯一正确姿势
- ❌ 不写回复内容（reply-drafting 的事），只给处置方向
- ❌ 不把功能请求计为好评（会高估情绪、误判 PMF）
- ❌ 不做语境判断的自动化——反讽与刷量号必须由模型复核
- ❌ 评论流为空时输出「发布日 0 评论」并提示检查发布链接，不编造数据

## 调用示例

**输入**（`examples/input.json`，节选）：

```json
{
  "product": "ClipMate（剪贴板历史工具）",
  "comments": [
    {"user": "maker_fan99", "platform": "ProductHunt", "text": "Congrats! Finally a clipboard manager that doesn't feel bloated. Love the search speed."},
    {"user": "angry_bob", "platform": "ProductHunt", "text": "Crashed twice within 10 minutes. How do I get a refund?"},
    {"user": "隐私控", "platform": "V2EX", "text": "剪贴板数据会上传服务器吗？"}
  ]
}
```

**输出**（脚本实跑，退出码 0）：正 1 / 负 0 / 中 2 / 疑 1 / 风险 3，P0+P1 共 3 条——
angry_bob「refund」命中退款诉求 P0；「doesn't feel bloated」被否定翻转正确判为好评。
详见 examples/output.md。

## 所属工作流

- `daily-comment-duty-flow`（当日评论值守，每 15 分钟）
- `launch-battle-review-flow`（发布战报复盘，T+1）

## 合规声明

- 输出标注「AI 生成内容」，所有动作「待人工确认」后才执行
- 评论内容属用户数据：清单仅限发布值守使用，不外发、不公开截图（好评引用须获授权）
- 不执行自动回复；回复草稿一律走 reply-drafting 并经人工确认

---

*本技能遵循 [bangwozuo 数字员工资产规范](https://github.com/bangwozuo/digital-employee-spec) v3.0*
