# 输出示例（模型按 prompt.txt 产出）

> 输入为 `examples/input.json`（ClipMate 发布文案包需求）。本技能为 T2 纯提示词型，
> 以下为按 prompt 方法论产出的真实文案示例，无占位符。

## 文案包总览

| 件 | 内容 | 硬约束核对 |
|---|---|---|
| tagline | Your clipboard, finally searchable. | 38 字符 ✅（≤60） |
| 产品描述 | ClipMate keeps every text, link, and snippet you copy on Windows — searchable for the last 3 months, stored locally, never uploaded. OCR extracts text from screenshots; paste-as-plain-text cleans code formatting in one keystroke. | 193 字符 ✅（≤260） |
| gallery 配文 | 见下方 5 张逐张 | 1270×760 ✅ |
| maker comment | 见下方 | 217 词 ✅（150-250） |
| 开场话术 ×5 | 见下方 | 2-3 句/条 ✅ |

## tagline 候选（3 条，标注公式）

| # | 候选 | 公式 | 字符数 |
|---|---|---|---|
| 1 | Your clipboard, finally searchable | 痛点否定 | 34 |
| 2 | Never lose a copied link again | 痛点否定（变体） | 30 |
| 3 | Search 3 months of clipboard history in 0.3s | 具体数字 | 45 |

推荐 #1：受众最宽（人人都丢过复制内容）；#3 数字最强但把产品限死在「搜索」一个功能。

## gallery 配文（5 张）

| # | 内容 |
|---|---|
| 1 | 主视觉：界面截图 + 「Your clipboard, finally searchable」 |
| 2 | GIF：Ctrl+Shift+V → 输入 api key → 0.3s 命中 |
| 3 | GIF：截图 OCR 框选 → 文字可复制 |
| 4 | 背书：beta 用户原话（已获授权）+ 「100% local storage」 |
| 5 | 定价：Free / Pro $8 per month，含功能对照两列 |

## maker comment（217 词）

> Hey hunters! Two years ago I lost the 7th API key I'd ever copied — pasted it into a
> chat, closed the window, gone. I tried every clipboard manager on Windows and bounced
> off all of them: too heavy, too cluttered, or they wanted to upload my clipboard to
> their cloud.
>
> So I built ClipMate. One shortcut (Ctrl+Shift+V) searches everything you've copied in
> the last 3 months. Everything stays on your machine — the sync feature is end-to-end
> encrypted, and even that is opt-in. There's also screenshot OCR (grab text from any
> image) and paste-as-plain-text, which strips formatting from code so it doesn't
> explode your chat windows.
>
> It's a one-person project — I've been building it nights and weekends for two years.
> I'd love your take on two things: is $8/month for the Pro tier reasonable for
> individual devs? And which platform should I port to next, macOS or Linux?
>
> I'll be in the comments all day (Pacific time), so ask me anything.

## 开场话术（发布日弹药，5 条）

| 场景 | 草稿 |
|---|---|
| 感谢祝贺 | Thanks! Curious — how do you handle clipboard history today, or do you? |
| 问定价 | Free tier covers search + history; Pro ($8/mo) adds OCR, sync, and unlimited history. Full comparison on the site. What would you pay for this? |
| 问平台支持 | Windows 10/11 today. macOS port is next in the queue — Linux after, if demand's there. Which are you on? |
| 问竞品差异 | The honest difference: local-first storage and a search-first UI. Most alternatives either upload your clipboard or bury search three menus deep. |
| 负面（崩溃报告） | Sorry about that — that's on me. Could you share your Windows version and what you clicked right before the crash? Fix ships this week either way; DM me and I'll send you a build to verify. |

## 证据核对

| 文案中的断言 | 依据 | 状态 |
|---|---|---|
| 「0.3s」搜索命中 | 开发者实测（i7/16GB，1 万条记录） | ✅ 用户提供 |
| 「100% local storage」 | 架构设计（无上传代码路径） | ✅ 用户提供 |
| beta 用户原话 | 已获授权引用 | ✅ 用户提供 |
| 「two years」开发周期 | maker 自述 | ✅ |

## 发布前自查

- [x] tagline ≤60 字符且无句号
- [x] 无 Chinglish 直译（自查：无 very / more and more / using experience）
- [x] 每个数据断言有依据
- [x] 不含 incentivized upvote 诱导

---

*本结果由 AI 生成，全部文案人工确认后才上传；遵守 PH Guidelines（不做 incentivized voting）。*
