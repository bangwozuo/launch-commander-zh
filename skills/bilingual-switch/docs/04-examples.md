# 使用示例

以下示例均为按 prompt.txt 方法论产出的真实双语稿（无占位符），展示四种典型场景。

---

## 示例 1：完整双语重写（V2EX → PH/Reddit）

**输入**：见 `examples/input.json`（ClipMate 中文主稿 + 术语表）。

**输出**（全文见 examples/output.md）：英文版用「the 7th one broke me」重写「破防」，
「破防」不硬搬；事实骨架 7 项（开发周期/起因/架构/性能/环境/功能/定价）全部一致；
「10 万条 → 100k entries」「$8/月 → $8/mo」按英文社区习惯换算。

---

## 示例 2：Chinglish 拦截（直译稿 → 重写稿）

**输入**：用户自译稿：

> ClipMate has a very good using experience. It can improve your efficiency greatly.
> Welcome to use!

**输出**（重写稿）：

> ClipMate feels instant. Search everything you've copied in 0.3s.

**拦截点**：`using experience`（中式搭配）、`very good`（very 滥用）、
`improve your efficiency greatly`（中式直译）、`Welcome to use`（经典 Chinglish）——
四项全部触发自查清单，整段重写。

---

## 示例 3：tagline 处理（两案并列，不擅自决定）

**输入**：英文 tagline `Your clipboard, finally searchable`，用户问中文版怎么翻。

**输出**（两案并列）：

| 方案 | 中文版 | 适用 |
|---|---|---|
| A：保留英文 | Your clipboard, finally searchable | 产品定位偏国际化，tagline 本身是品牌资产 |
| B：重写 | 你的剪贴板，终于能搜了 | 中文社区独立投放，需要原生记忆点 |

**要点**：不直译（「你的剪贴板，最终可被搜索」是机翻腔），也不替用户拍板。

---

## 示例 4：事实口径漂移拦截

**输入**：英文版把「0.3s（10 万条实测）」改写成「instant」（觉得数字啰嗦）。

**输出**：**拦截**——事实骨架第 4 项对不齐：

| # | 事实 | 中文版 | 英文版 | 一致 |
|---|---|---|---|---|
| 4 | 搜索性能 | 0.3 秒命中（10 万条实测） | instant | ❌ |

处理：英文版恢复 `hits in 0.3s, tested on 100k entries`。数字证据是两版共同的
信任资产，一边删 = 口径漂移；嫌啰嗦可以改句式，不能改事实。

---

*本页示例由方法论产出；两版均人工确认后发布，输出标注 AI 生成内容。*
