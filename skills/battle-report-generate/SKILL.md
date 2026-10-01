---
name: battle-report-generate
description: 独立开发者发布日战报（T+1）。汇总 Product Hunt/V2EX/X/即刻等平台的 PV、注册、GitHub 星标、waitlist 转化、媒体提及五指标，对照目标判定达标/部分达标/未达标（100%/70% 分档），按流量层→转化层→留存层→传播层四层漏斗归因，产出 Excel 战报 + PNG 数据图。当用户需要发布战报、发布复盘、发布数据汇总、T+1 复盘时使用。
---

# 战报生成

T+1 早上把各平台数据收拢成**达标对照表 + 归因分析 + ≤3 条行动建议**。
产出决定下一周是乘胜追击还是止损换方向——不写流水账。

不做的事：不抓取平台数据（由用户提供截图/后台导出）、不写对外 PR 稿。

## 元信息

| 字段 | 值 |
|------|-----|
| ID | `de_dev_02_sk09` |
| 类型 | **`atomic`（原子技能）** |
| 所属员工 | 发布指挥官 |
| 能力族 | 报告生成型 · 数据汇总与达标判定 |
| 复杂度 | `S` |
| 阶段 | `P1` |
| 复用度 | 中（#1 周报、T+7 复盘复用） |
| 资产形态 | 深度提示词 + Python 脚本（无模型调用、无 API Key） |

## 能力描述

1. **五指标汇总**：PV / 注册数 / GitHub 星标 / waitlist 转化 / 媒体与社区提及，
   全部带参考基准（PV→注册 5%-12%、waitlist/PV 3%-8%、PH 首日 100 星属头部）
2. **达标三档判定**：≥100% 达标 / 70%-100% 部分达标 / <70% 未达标，整体判定三档
3. **平台结构分析**：各平台 PV 占比、转化率对比；单平台占比 >70% 标「鸡蛋一个篮子」
4. **规则式归因提示**：转化率 <3% → 落地页问题；waitlist <3% → 钩子/表单问题；
   注册未达标但转化正常 → 流量缺口
5. **逐小时曲线**：对照各平台发布时点识别自来水峰（非发布时点的异常峰 = 被转发）

## 输入规格

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `platforms` | array | ✅ | 各平台 {name, pv, signups, github_stars, waitlist, mentions, note} |
| `targets` | object | ⬜ | 五指标目标值；未设的不参与达标判定 |
| `hourly_pv` | array | ⬜ | 发布日逐小时 PV（≥2 条时出曲线图） |
| `product` / `launch_date` | string | ⬜ | 产品名 / 发布日 |

## 输出规格

- `summary`：总 PV / 注册 / 转化率 / 星标 / 达标 n/m / 整体判定
- `metrics`：五指标达标表（实际/目标/达标率/判定/参考基准）
- `attribution_hints`：规则式归因提示（漏斗定位），深度归因由模型撰写

**产物文件**：

| 文件 | 内容 |
|---|---|
| `out/发布战报.xlsx` | 关键指标（未达标行标红）/ 平台明细 / 归因提示 / 汇总 |
| `out/平台流量对比.png` | 各平台 PV 柱状图 |
| `out/当日流量曲线.png` | 逐小时 PV 曲线（有 hourly 数据时） |
| `out/battle_report.json` | 机器可读结果，供 launch-battle-review-flow 读取 |

## 使用步骤

### 方式一：纯提示词（含深度归因）

1. 把 `prompt.txt` 全部内容粘贴为系统提示词
2. 提供各平台数据（后台截图转述或导出）与目标值
3. 得到核心结论 + 达标表 + 归因分析 + ≤3 条行动建议

### 方式二：带脚本（确定性计算 + 产出 Excel/PNG）

```bash
python3 <SKILL_DIR>/scripts/battle_report.py --input input.json --outdir out
python3 <SKILL_DIR>/scripts/battle_report.py --demo        # 无输入也能看效果
```

**分工**：脚本算达标率/转化率/占比/排名（数值以脚本为准，不要自己算）；
模型做四层漏斗归因、高光提炼、行动建议（脚本做不了的）。两者结果交叉核对。

## 边界（不做的事）

- ❌ 不自动抓取平台数据（PH/Google Analytics/GitHub API 均由用户提供）
- ❌ 数据缺失标「缺失」让用户补，**不估算不填均值**
- ❌ 不用单日数据下长期结论（发布日有脉冲效应，留存看 T+7）
- ❌ 行动建议 ≤3 条——独立开发者只够做 1-2 件事，列 10 条等于没列
- ❌ 对外版本须去除转化率等商业敏感项（由人工把关）

## 调用示例

**输入**（`examples/input.json`，节选）：

```json
{
  "product": "ClipMate（剪贴板历史工具）",
  "targets": {"pv": 5000, "signups": 300, "github_stars": 100, "waitlist": 200, "mentions": 3},
  "platforms": [
    {"name": "ProductHunt", "pv": 3200, "signups": 190, "github_stars": 76, "mentions": 2, "note": "当日榜第 9"},
    {"name": "V2EX", "pv": 980, "signups": 45, "github_stars": 12, "waitlist": 8, "note": "上午 10 点发"}
  ]
}
```

**输出**（脚本实跑，退出码 0）：PV 4910（98% 🟡）、注册 272（91% 🟡）、星 97（97% 🟡）、
waitlist 11（6% 🔴）、提及 4（133% ✅）——达标 1/5，归因提示 3 条（waitlist 转化 0.2%
低于 3% 基准 → 钩子/表单问题）。详见 examples/output.md。

## 所属工作流

- `launch-battle-review-flow`（发布战报复盘，T+1 事件触发）

## 合规声明

- 输出标注「AI 生成内容」，对外分享前须人工确认（用户量数据属敏感信息）
- 不引用无授权的第三方/竞品数据
- 内部战报含转化率等商业数据，外发版本须人工脱敏

---

*本技能遵循 [bangwozuo 数字员工资产规范](https://github.com/bangwozuo/digital-employee-spec) v3.0*
