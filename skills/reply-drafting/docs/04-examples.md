# 使用示例

以下示例均为按 prompt.txt 方法论产出的真实草稿（无占位符），展示四种典型场景。

---

## 示例 1：P0 退款诉求（三段骨架完整走查）

**输入**：见 `examples/input.json`（angry_bob 崩溃+退款，PH 首日）。

**输出**（全文见 examples/output.md）：

> Sorry about that — that's on me. … Could you share your Windows 10 build…?
> Fix ships this week either way; DM me and I'll send you a build to verify.

| 骨架段 | 落点 |
|---|---|
| 承认 | 「that's on me」，无辩解开头 |
| 给方案 | 要崩溃信息定位 + fix in the works（不承诺具体日期——授权边界） |
| 留渠道 | DM + 退款政策链接（14 天无理由在授权内，未特批金额） |

---

## 示例 2：疑问直答（不绕弯）

**输入**：「Does it support Windows 11 dark mode?」

**反例（拒绝的写法）**：

> Great question! Dark mode is something we've been thinking about a lot…

（寒暄+绕弯，30 分钟 SLA 下是浪费时间，PH 排名等不起）

**正例（产出）**：

> Dark mode: yes, Win11 dark mode is supported and follows your system setting.

第一句就是答案；结尾钩子（哪台设备先同步？）把对话续上。

---

## 示例 3：授权边界拦截（日期承诺）

**输入**：用户问「German translation this month?」，not_authorized 含「具体修复/交付日期」。

**输出**：草稿不给日期承诺，写授权内占位句：

> i18n is on the roadmap and German is the most-requested — I can't promise a date
> yet, but I'll post here the moment it ships.

**拦截逻辑**：承诺「this month」= 给挖坑；「can't promise a date yet + 会第一时间
告知」既诚实又留住期待。

---

## 示例 4：拉锯升级（两回合规则）

**输入**：同一用户对定价的第二轮负面（「$8 就是抢钱」已回复过一次）。

**输出**：

> 公开区：I've DM'd you — happy to keep the conversation there.
> 私信草稿：（了解预算约束 + 给免费版用法建议 + 需要时开发者定夺学生折扣）

**规则**：公开区拉锯超两回合必转私信；公开区只留「已私信，会在这里更新结果」，
不让评论区变成辩论场。

---

*本页示例由方法论产出；草稿全部待人工确认后才可发布，输出标注 AI 生成内容。*
