# 输出示例（脚本实跑）

> 由 `scripts/run_flow.py` 处理 `examples/input.json` 真实产出（退出码 0），非手写。
> 场景：发布日一轮（6 条新评论，PH/V2EX/即刻 三平台）。

## 值守看板（脚本实跑）

| 项 | 内容 |
|---|---|
| 产品 | ClipMate（剪贴板历史工具） |
| 轮次类型 | 发布日值守（每 15 分钟一轮） |
| 本轮新评论 | 6（正/负/中/疑/风险 = 1/0/2/1/2） |
| 待回任务（P0-P2） | 3（30 分钟 SLA 风险 2 条） |
| 健康判定 | 正面占比 ≥60% 且风险=0 为健康（本样例风险 2 条，未达健康线） |
| 升级提示 | P0 全部升级开发者本人；同一用户负面第二回合转私信；媒体/大V询问升级人工 |
| 异常标注 | 正常 |

## 回复任务卡（脚本实跑排序）

| 队列位 | 优先级 | 平台 | 用户 | 摘录 | SLA | 回复骨架 | FAQ 命中 | FAQ 口径 |
|---|---|---|---|---|---|---|---|---|
| 1 | P0 | ProductHunt | angry_bob | Crashed twice within 10 minutes… | 30 分钟 | 风险处置：退款=政策+私信渠道 | refund\|退款 | 14 天无理由退款，走网站 /refund |
| 2 | P0 | ProductHunt | skeptic_pete | This is just a copy of Paste… | 30 分钟 | 风险处置：抄袭=承认相似+差异表；刷榜=公开说明推广方式 | （无命中） | 回复前须人工确认事实，缺口回填 faq-pregenerate |
| 3 | P2 | ProductHunt | dev_sarah | Does it support Windows 11 dark mode?… | 2 小时 | 疑问直答：第一句就是答案 | dark mode\|深色 | 支持 Win11 深色模式，自动跟随系统 |

## 观察名单

| 队列位 | 平台 | 用户 | 摘录 | 处置 |
|---|---|---|---|---|
| 4 | ProductHunt | maker_fan99 | Congrats! Finally a clipboard manager… | 感谢+追问场景（引用须授权） |
| 5 | V2EX | 老王聊软件 | 用了两天搜索确实快，希望加上 OCR… | 观察不逐条回（功能请求，OCR 已上线——回复时直接给口径） |
| 6 | 即刻 | 潜水员 | mark 一下，看着不错 | 观察不逐条回 |

## 衔接说明（流程终点）

- 任务卡 1/2/3 → `reply-drafting` 按骨架撰写可粘贴草稿 → 人工确认 → 人工发布
- skeptic_pete 无 FAQ 命中 → 说明推广方式的口径（waitlist 邮件）需开发者现场确认，
  确认后补进口径库（faq-pregenerate）
- 老王聊软件的功能请求 → OCR 已上线（2.1），回复时直接给更新路径

## 产物

| 文件 | 大小 |
|---|---|
| out/值守清单.xlsx | 8.6 KB（回复任务卡/观察名单/值守看板，P0 行标红） |
| out/emotion_scan.json | 上游产物（步骤 1 输出） |
| out/duty_flow_result.json | 3.5 KB（机器可读，供下轮对比积压） |

---

*本结果由 AI 生成；所有回复人工确认后在平台原生界面发出；输出标注 AI 生成内容。*
