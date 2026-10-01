# 测试报告

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行 | ✅ PASS |
| prompt.txt 深度区块（三步骤含失败处理 / 量化规则 / 编排层失败模式 / 编排规则） | ✅ PASS |
| 无占位符残留 | ✅ PASS |
| 无 API Key / 无模型调用 / 无自动回复 | ✅ PASS |

## 二、脚本实跑（含上游技能串联）

**命令**：

```bash
python scripts/run_flow.py --demo
python scripts/run_flow.py --input examples/input.json --outdir out
```

**运行环境**：Python 3.13（绝对路径解释器）/ openpyxl

| 项 | 结果 |
|---|---|
| 退出码 | 0（demo 与 input 双跑均 0） |
| 上游串联 | comment-emotion-detect 子进程调用成功，emotion_scan.json 衔接 ✅ |
| 分流结果 | 6 条评论 → 待回 3（P0×2+P2×1）/ 观察 3；30 分钟 SLA 风险 2 条 |
| FAQ 匹配 | 按原文全文匹配：refund ✅ / dark mode ✅ / 无命中标「须人工确认事实」 ✅ |
| 产物 1 | `out/值守清单.xlsx`（8.6 KB，任务卡/观察名单/看板，P0 行标红） |
| 产物 2 | `out/emotion_scan.json`（上游产物） |
| 产物 3 | `out/duty_flow_result.json`（3.5 KB） |
| 耗时 | < 3 s（含上游子进程） |

### 分流核对（真实输出）

```
P0  angry_bob      任务卡（refund 命中 → 14 天无理由口径）
P0  skeptic_pete   任务卡（无命中 → 须人工确认事实）
P2  dev_sarah      任务卡（dark mode 命中 → Win11 深色模式口径）
P3  maker_fan99    观察名单（感谢+追问场景）
P4  老王聊软件      观察名单（功能请求，OCR 已上线）
P4  潜水员          观察名单（观察不逐条回）
```

### 失败处理演练

| 场景 | 结果 |
|---|---|
| 评论流为空 | 正常退出 + 「发布日 0 评论，检查发布链接」 ✅ |
| 全部中性 | 标红「疑似抓取不全」 ✅ |
| FAQ 库缺失 | 任务卡照常生成 + 备注「须人工确认事实」 ✅ |
| 上游退出码 ≠0 | 中止打印 stderr（逻辑在位） ✅ |

## 三、边界与已知限制

| 限制 | 说明 |
|---|---|
| 评论获取 | 评论流由用户提供/粘贴；不代抓平台数据 |
| FAQ 匹配 | 关键词正则匹配，同义未收录的口径不命中（标人工确认） |
| 反讽复核 | 上游「需模型复核」位须人工过一遍后再草拟 |
| 积压统计 | 跨轮积压由 duty_flow_result.json 人工累计，脚本不做跨轮状态持久化 |

## 四、结论

**通过。** 上游技能真实串联、分流与 SLA 正确、FAQ 全文匹配生效（修复了摘录截断
导致 refund 漏命中的缺陷）、四类失败处理可演练，回复零自动化。

---

*测试报告基于真实实跑输出生成 · 2026-09-30*
