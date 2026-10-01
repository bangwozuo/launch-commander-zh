# 测试报告

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行 | ✅ PASS |
| prompt.txt 深度区块（PH 机制表 / tagline 公式 / 首评三段式 / 证据纪律 / 违规拦截） | ✅ PASS |
| 无占位符残留 | ✅ PASS |
| 无 API Key / 无模型调用 | ✅ PASS |

## 二、内容深度自检（T2 无脚本，按五维度核）

| 维度 | 证据 |
|---|---|
| D1 领域术语 | tagline / maker comment / gallery / incentivized upvote / 00:01 PT / 马太效应 |
| D2 量化约束 | tagline ≤60 字符、描述 ≤260 字符、首评 150-250 词、首评 30 分钟内、评论响应 30 分钟 |
| D3 方法 | tagline 四公式 + 三候选 A/B 法、首评三段式、Chinglish 自查清单、证据核对流程 |
| D4 领域边界 | incentivized upvote 下架风险、模板句开头无记忆点、假数据被 PH 受众识破 |
| D5 输出可交付 | 文案包总览表 / tagline 候选表 / gallery 逐张配文 / 发布前自查清单 |

## 三、示例实核（无脚本，按方法论走查）

| 走查项 | 结果 |
|---|---|
| ClipMate 文案包（examples/output.md） | tagline 38 字符 ✅；首评 217 词（150-250 内）✅；5 件套齐全 ✅ |
| 证据核对表 | 「0.3s」「100% local」「two years」4 项断言全部挂依据 ✅ |
| 违规拦截走查 | 「upvote 换会员」话术被拒并给合规替代 ✅ |
| 无数据走查 | 「帮助 10 万人」无依据断言被拒，改场景描述 ✅ |
| Chinglish 自查 | 无 very / more and more / using experience 类直译 ✅ |

## 四、边界与已知限制

| 限制 | 说明 |
|---|---|
| 纯提示词 | 无脚本；字符数/词数由模型自数并在输出表标注，发布前人工复核 |
| 平台规则时效 | PH 字符限制与榜单机制以官方为准，需定期核对（tracking_log） |
| 语感判断 | 母语者语感为模型判断，重要发布建议母语者终审 |
| 不做图 | gallery 只给配文与排布，视觉产出走 hero-image-sellingpoint + 视觉工具 |

## 五、结论

**通过。** 结构合规 + 深度五维全中；三处典型错误（模板句、无数据断言、incentivized
话术）均有拦截示例与替代写法。

---

*测试报告基于方法论走查与示例实核 · 2026-09-30*
