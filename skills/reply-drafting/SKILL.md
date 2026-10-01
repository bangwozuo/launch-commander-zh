---
name: reply-drafting
description: 独立开发者发布日回复草拟。按 comment-emotion-detect 值守队列逐条产出可直接粘贴的回复草稿：负面用「承认+给方案+留渠道」三段骨架，疑问「直接回答+支撑+钩子」对照 FAQ 库，风险按六类标准处置（刷榜公开说明推广方式、退款给政策+渠道），按平台语感定制（PH/Reddit/V2EX/X），超授权事项标「需开发者定夺」。当用户需要回复评论草稿、负面评论应对、发布日评论区话术时使用。
---

# 回复草拟

为值守队列（P0-P4）逐条产出**可直接粘贴**的回复草稿——按情绪、问题类型、平台
语感定制，标明升级项。你不发布、不承诺超出授权范围的事。

不做的事：不发布、不删帖、不替开发者定金额/日期/法律口径。

## 元信息

| 字段 | 值 |
|------|-----|
| ID | `de_dev_02_sk08` |
| 类型 | **`atomic`（原子技能）** |
| 所属员工 | 发布指挥官 |
| 能力族 | 文案生成型 · 评论回复草拟 |
| 复杂度 | `S` |
| 阶段 | `P1` |
| 复用度 | 高（发布后日常客服复用） |
| 资产形态 | 纯提示词（无运行时依赖） |

## 能力描述

1. **四种基本盘骨架**：负面=承认+给方案+留渠道（三段缺一不可）；疑问=直接回答+
   支撑+钩子；风险=六类标准处置；正面=感谢+追问使用场景
2. **平台语感**：PH 2-4 句友好、Reddit 平实技术向、V2EX 直接对口、X ≤280 字符、
   即刻轻松不油
3. **授权边界**：对照 authorized/not_authorized 清单——日期承诺、金额特批、降价
   一律标「需开发者定夺」，草稿写占位句
4. **升级判断**：退款/法律/媒体/同一用户第二回合 → 转私信或升级，公开区只留进度
5. **FAQ 缺口回填**：没答上的问题列清单，回填 faq-pregenerate 口径库

## 输入规格

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `queue` | array | ✅ | 值守队列（含 text 全文 / platform / sentiment / priority） |
| `faq_highlights` | object | ⬜ | 相关口径（价格/功能事实/政策），不得超出现编 |
| `authorized` / `not_authorized` | array | ⬜ | 授权边界清单 |
| `launch_day` | boolean | ⬜ | 发布日（P0/P1 SLA 30 分钟） |

## 输出规格

| 件 | 说明 |
|---|---|
| `drafts` | 逐条草稿（直接粘贴级，30 分钟 SLA 项不得写「待确认」） |
| `escalation_list` | 需开发者定夺清单（事项/卡点/建议） |
| `faq_gaps` | FAQ 缺口（回填口径库） |

## 使用步骤

### 方式一：纯提示词

1. 把 `prompt.txt` 全部内容粘贴为系统提示词
2. 提供值守队列 + FAQ 口径 + 授权边界
3. 得到逐条草稿 + 升级清单 + FAQ 缺口；人工确认后发布

### 在流程中的位置

- 上游：`comment-emotion-detect` 排队（P0-P4 + SLA）→ 本技能草拟
- 口径来源：`faq-pregenerate` 口径库
- 编排：`daily-comment-duty-flow`（每 15 分钟一轮）

## 边界（不做的事）

- ❌ 不写「感谢反馈，我们会持续优化」敷衍负面——每条负面必须有具体方案
- ❌ 不辩解开头；评论区拉锯超两个回合必须转私信
- ❌ 不现编口径——FAQ 没有的价格/日期/功能宁可标「需定夺」
- ❌ 不删帖不 suggestions 删帖；不用小号回帖（astroturfing）
- ❌ 不在公开回复透露内部数据（收入、用户数、未公开路线图）

## 调用示例

**输入**（`examples/input.json`，节选）：

```json
{
  "queue": [
    {"user": "angry_bob", "platform": "ProductHunt", "sentiment": "🔴 风险/退款诉求", "priority": "P0",
     "text": "Crashed twice within 10 minutes. How do I get a refund?"}
  ],
  "faq_highlights": {"refund_policy": "14 天无理由退款，走网站 /refund"},
  "not_authorized": ["退款金额特批"]
}
```

**输出**（见 examples/output.md）：P0 退款回复——承认（that's on me）→ 要崩溃信息 →
「fix in the works」不承诺具体日期 → 退款给 14 天政策 + 私信渠道（标准政策内无需
特批）。另含疑问/功能请求/刷榜指控三条草稿与 2 条 FAQ 缺口。

## 所属工作流

- `daily-comment-duty-flow`（当日评论值守，每 15 分钟）
- `launch-battle-review-flow`（T+1 复盘引用回复记录）

## 合规声明

- 输出标注「AI 生成内容」；草稿全部「待人工确认」后才可发布
- 升级类（退款金额/法律/媒体）人工处理，AI 只备料
- 引用用户内容须获授权；不承诺未授权事项；不做小号运营

---

*本技能遵循 [bangwozuo 数字员工资产规范](https://github.com/bangwozuo/digital-employee-spec) v3.0*
