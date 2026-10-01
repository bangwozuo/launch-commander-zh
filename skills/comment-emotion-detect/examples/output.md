# 输出示例（脚本实跑）

> 由 `scripts/emotion_scan.py` 处理 `examples/input.json` 真实产出（退出码 0），非手写。

## 情绪总览

| 指标 | 值 | 基线 |
|---|---|---|
| 评论总数 | 7 | — |
| 正/负/中/疑/风险 | 1 / 0 / 2 / 1 / 3 | 正面占比 ≥60% 健康 |
| 正面占比 | 14% | 未达 60%（样例小样本，仅演示口径） |
| P0/P1 数量 | 3 | >8 条未回先清队列 |

## 优先级队列（脚本实跑排序）

| 队列位 | 平台 | 用户 | 摘录 | 情绪 | 风险子类 | 优先级 | SLA | 建议动作 |
|---|---|---|---|---|---|---|---|---|
| 1 | ProductHunt | angry_bob | Crashed twice within 10 minutes on Windo… | 🔴 风险 | 退款诉求 | P0 | 30 分钟 | 30 分钟内私信响应，公开回复处理进度 |
| 2 | ProductHunt | skeptic_pete | Another clipboard app? This is just a co… | 🔴 风险 | 抄袭/竞品指控 | P0 | 30 分钟 | 承认相似点+列差异表，不攻击竞品 |
| 3 | V2EX | 隐私控 | 剪贴板数据会上传服务器吗？涉及密码片段的话权限范围是什么？ | 🔴 风险 | 安全/隐私质疑 | P0 | 30 分钟 | 2 小时内回复数据流向说明，链接隐私政策 |
| 4 | ProductHunt | dev_sarah | Does it support Windows 11 dark mode? An… | 🔵 疑问 | — | P2 | 2 小时 | 对照 FAQ 库回答；FAQ 没有的补进 FAQ |
| 5 | ProductHunt | maker_fan99 | Congrats on the launch! Finally a clipbo… | 🟢 正面 | — | P3 | 24 小时 | 感谢+追问使用场景（截图须获用户同意） |
| 6 | V2EX | 老王聊软件 | 用了两天，搜索确实快，但希望加上 OCR 截图取词，要是能支持就好了 | ⚪ 中性 | — | P4 | 48 小时 | 观察即可（功能请求不算好评） |
| 7 | 即刻 | 潜水员 | mark 一下 | ⚪ 中性 | — | P4 | 48 小时 | 观察即可，不逐条回复 |

## 需模型复核项

| # | 评论 | 机器判定 | 疑点 | 建议改判 |
|---|---|---|---|---|
| — | — | — | 本样例无需改判；skeptic_pete 同时含刷榜暗示（upvotes came in the first hour），建议回复时一并说明推广方式 | — |

## 判定亮点（防误报验证）

- 「doesn't feel bloated」——否定翻转生效，未把 bloated 记为差评
- 「希望加上 OCR…要是能支持就好了」——功能请求未计为 🟢 正面
- 「Crashed…how do I get a refund」——refund 命中退款诉求，整条升 P0 而非普通疑问

## 产物

| 文件 | 大小 |
|---|---|
| out/评论分类清单.xlsx | 10.3 KB（优先级队列 / 分类明细 / 汇总三 sheet，风险行标红） |
| out/情绪分布.png | 26.4 KB |
| out/emotion_scan.json | 4.4 KB |

---

*本结果由 AI 生成，动作须人工确认后执行；负面评论处置原则「承认+给方案」不删帖。*
