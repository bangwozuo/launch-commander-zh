---
name: producthunt-copy
description: 独立开发者 Product Hunt 发布文案包。产出 tagline（≤60 字符，3 条候选标注公式）、产品描述（≤260 字符）、5 张 gallery 配文（1270×760 排布）、maker comment 首评三段式（Why/What/Ask，150-250 词）、发布日开场话术×5，附证据核对表与 Chinglish 自查。当用户需要 PH 文案、PH 发布准备、tagline、首评、maker comment 时使用。
---

# Product Hunt 文案

产出一整套 PH 发布文案包：tagline / 产品描述 / gallery 配文 / maker comment /
开场话术。PH 受众给每个产品 5 秒——文案唯一任务是 5 秒内让人点「访网站」。

不做的事：不做图、不发布、不代替用户回复评论（回复草拟走 reply-drafting）。

## 元信息

| 字段 | 值 |
|------|-----|
| ID | `de_dev_02_sk01` |
| 类型 | **`atomic`（原子技能）** |
| 所属员工 | 发布指挥官 |
| 能力族 | 文案生成型 · PH 发布文案包 |
| 复杂度 | `S` |
| 阶段 | `P0` |
| 复用度 | 中（更新发布 / 新平台启动复用） |
| 资产形态 | 纯提示词（无运行时依赖） |

## 能力描述

1. **tagline 三候选**：按「动词+结果 / 痛点否定 / 具体数字」三个公式各写一条，
   标注字符数；禁用 `A / AI-powered / an innovative` 开头与形容词堆砌
2. **maker comment 三段式**：Why（具体到场景的痛）→ What（一个核心功能+一个差异点）
   → Ask（问具体问题）；150-250 词，母语者语感自查（无 very / 中式直译）
3. **gallery 排布**：5 张 1270×760 逐张配文——主视觉、演示×2、背书、定价
4. **开场话术 ×5**：祝贺 / 定价 / 平台 / 竞品 / 负面；负面用「承认+给方案+留渠道」
5. **证据核对表**：文案中每个数据断言挂依据；无依据的必须删除或改为场景描述

## 输入规格

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `brief` | string | ✅ | 产品说明：是什么、给谁用、核心功能、差异化 |
| `key_points` | string | ⬜ | 必写要点（数据须真实可溯源） |
| `tone` | string | ⬜ | 语气要求，默认「直接、开发者对开发者」 |
| `constraints` | object | ⬜ | 覆盖默认硬约束（tagline 长度等） |

## 输出规格

| 件 | 约束 |
|---|---|
| `tagline` | ≤60 字符无句号，3 条候选标注公式与字符数 |
| `description` | ≤260 字符 |
| `gallery_notes` | 5 张逐张配文（1270×760） |
| `maker_comment` | 150-250 词三段式 |
| `openers` | 5 条开场话术（含负面模板） |
| `evidence_check` | 断言依据核对表 |

## 使用步骤

### 方式一：纯提示词

1. 把 `prompt.txt` 全部内容粘贴为系统提示词
2. 提供 brief + key_points（真实数据）+ tone
3. 得到文案包总览 + tagline 候选 + 证据核对 + 发布前自查清单

### 与其他技能配合

- 卖点不够清晰 → 先跑 `hero-image-sellingpoint` 拿 TOP 卖点再写文案
- 需要中文社区版本 → 产出后走 `bilingual-switch`（不是翻译，是重写）
- 发布日评论 → `reply-drafting` 按情绪与问题类型草拟

## 边界（不做的事）

- ❌ 不编造用户数、评分、评价；无数据的卖点改用场景描述
- ❌ 不写 incentivized 投票话术（投票换福利/解锁）——PH 明令禁止，被抓下架
- ❌ 不攻击竞品；差异用「我们怎么做」表述，不用「比 X 好」
- ❌ 不替用户决定 tagline——给 3 条候选 + 推荐理由，最终人工选
- ❌ 不承诺路线图外功能

## 调用示例

**输入**（`examples/input.json`）：

```json
{
  "brief": "为 ClipMate（Windows 剪贴板历史工具）撰写 PH 发布文案包，目标受众是开发者和重度文字工作者",
  "key_points": "全局历史搜索（Ctrl+Shift+V 秒搜三个月记录）、截图 OCR 取字、粘贴代码自动去格式；本地存储不上传；发布日 2026-09-29 00:01 PT；定价免费+Pro $8/月"
}
```

**输出**（见 examples/output.md）：tagline「Your clipboard, finally searchable.」
（38 字符，痛点否定式）；maker comment 217 词三段式（以「丢了第 7 个 API key」开场）；
5 条开场话术含崩溃报告的「承认+给方案」模板；证据核对 4 项全部挂依据。

## 所属工作流

- `launch-kit-generate-flow`（发布素材包生成，T-7 启动）

## 合规声明

- 输出标注「AI 生成内容」，全部文案人工确认后才上传
- 遵守 PH Guidelines：不做 incentivized voting、不假冒用户评论
- 文案与实际功能一致；性能数字标注测试环境

---

*本技能遵循 [bangwozuo 数字员工资产规范](https://github.com/bangwozuo/digital-employee-spec) v3.0*
