---
name: hero-image-sellingpoint
description: 独立开发者首图卖点提炼。把功能列表按「演示性 35% + 冲击力 25% + 受众宽度 25% + 差异化 15%」四维加权评分（0-100），选出 3-5 个上首图的卖点（≥60 分且可演示），并配 GIF 分镜骨架（总长 ≤5 秒）与 PH 首图方案（1270×760）。带 Python 脚本产出 Excel 评分清单 + 对比图。当用户需要发布首图规划、卖点提炼、GIF 脚本、PH gallery 排布时使用。
---

# 首图卖点提炼

首图停留时间不到 3 秒——从功能列表里挑出「值得上首图的 3-5 个」，配 GIF 分镜骨架。
不挑「自己最得意的」，挑「访客 3 秒看得懂的」。

不做的事：不做图、不录屏、不写 tagline 全套文案（走 producthunt-copy）。

## 元信息

| 字段 | 值 |
|------|-----|
| ID | `de_dev_02_sk02` |
| 类型 | **`atomic`（原子技能）** |
| 所属员工 | 发布指挥官 |
| 能力族 | 提炼判断型 · 卖点评分与视觉规划 |
| 复杂度 | `S` |
| 阶段 | `P0` |
| 复用度 | 中（T+7 复盘换图复用） |
| 资产形态 | 深度提示词 + Python 脚本（无模型调用、无 API Key） |

## 能力描述

1. **四维加权评分**：演示性 35% + 冲击力 25% + 受众宽度 25% + 差异化 15% → 0-100 分，
   4-5 分必须挂证据（用户原话/竞品对照/埋点数据）
2. **入选规则**：得分 ≥60 且可演示 → 取前 5；TOP1 = 首图主视觉；TOP2 分差 <5 分
   标「主卖点不突出，需补判」
3. **GIF 分镜骨架**：按类型给模板（speed / before_after / showcase / flow），
   总长 ≤5 秒、单分镜 ≤2 秒、最后帧定格拉 tagline
4. **硬约束检查**：入选 <3 个（素材不足）、>5 个（移详情页）、不可演示功能清单与
   改造建议（加 before/after / 计时器）
5. **PH gallery 排布**：第 1 张主视觉、第 2-3 张 TOP2/3 演示、第 4 张背书、第 5 张价格

## 输入规格

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `features` | array | ✅ | 功能列表 {name, description, demoable(0/1), wow(1-5), breadth(1-5), uniqueness(1-5)} |
| `audience` | string | ⬜ | 目标受众（影响受众宽度打分） |
| `product` | string | ⬜ | 产品名 |

## 输出规格

- `summary`：功能总数 / 入选数 / TOP1 / TOP2 分差
- `ranked`：评分排序 + GIF 类型 + 分镜骨架 + 入选标记
- `checks`：硬约束检查结果

**产物文件**：

| 文件 | 内容 |
|---|---|
| `out/卖点评分清单.xlsx` | 评分（入选行标绿）/ 入选清单 / 硬约束检查 / 汇总 |
| `out/卖点评分对比.png` | 卖点得分横向条形图 |
| `out/sellingpoint.json` | 机器可读结果，供 launch-kit-generate-flow 读取 |

## 使用步骤

### 方式一：纯提示词（含证据评估与文案）

1. 把 `prompt.txt` 全部内容粘贴为系统提示词
2. 提供功能列表与目标受众
3. 得到评分入选表 + 首图方案 + GIF 分镜脚本 + 落选说明

### 方式二：带脚本（加权计算 + 产出 Excel/PNG）

```bash
python3 <SKILL_DIR>/scripts/sellingpoint_score.py --input input.json --outdir out
python3 <SKILL_DIR>/scripts/sellingpoint_score.py --demo        # 无输入也能看效果
```

**分工**：脚本做加权计算、排序、入选判定、硬约束检查（数值以脚本为准，不要自己算）；
模型做维度证据评定、首图文案、GIF 字幕（脚本做不了的）。

## 边界（不做的事）

- ❌ 不做设计稿与录屏——输出的是「做什么」不是「做成什么」
- ❌ 不给每个功能都上首图的方案——首图只讲 3-5 个
- ❌ 无证据不打 4-5 分，「我觉得很惊艳」不是证据
- ❌ 不编造用户评价与数据背书；演示造数须在发布前替换为真实数据
- ❌ 不建议虚假按钮、假光标等诱导性视觉方案

## 调用示例

**输入**（`examples/input.json`，节选）：

```json
{
  "product": "ClipMate（剪贴板历史工具）",
  "features": [
    {"name": "全局历史搜索", "description": "Ctrl+Shift+V 秒搜三个月内所有剪贴记录", "demoable": 1, "wow": 5, "breadth": 5, "uniqueness": 3},
    {"name": "端到端加密同步", "description": "设备间同步剪贴板，密钥本地保存", "demoable": 0, "wow": 2, "breadth": 2, "uniqueness": 3}
  ]
}
```

**输出**（脚本实跑，退出码 0）：5 个功能入选 4 个，TOP1=全局历史搜索 90 分
（GIF 类型 speed）；端到端加密同步 20 分落选（不可演示，建议只做文字卖点）。
详见 examples/output.md。

## 所属工作流

- `launch-kit-generate-flow`（发布素材包生成，T-7 启动）

## 合规声明

- 输出标注「AI 生成内容」，首图最终稿人工确认后上传
- 截图含用户数据须脱敏或取得授权
- 卖点文案不含《广告法》极限词，用「实测/对照数据」说话

---

*本技能遵循 [bangwozuo 数字员工资产规范](https://github.com/bangwozuo/digital-employee-spec) v3.0*
