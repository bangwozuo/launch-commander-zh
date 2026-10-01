# 使用示例

以下示例均为按 prompt.txt 方法论产出的真实文案（无占位符），展示三种典型场景。

---

## 示例 1：工具类产品（完整文案包）

**输入**：见 `examples/input.json`（ClipMate，开发者受众，免费+Pro $8/月）。

**输出要点**（全文见 examples/output.md）：

| 件 | 产出 |
|---|---|
| tagline | Your clipboard, finally searchable（34 字符，痛点否定式，候选另含数字式 45 字符） |
| maker comment 开场 | 「Two years ago I lost the 7th API key I'd ever copied」——具体场景开场，不是「我们注意到需求」 |
| Ask | 问 Pro 定价是否合理 + 下一个平台选 macOS 还是 Linux（具体问题，不是 feedback welcome） |

---

## 示例 2：tagline 改写前后对照（模板句 → 结果句）

**输入**：

```json
{"brief": "PDF 工具站，合并/拆分/压缩，免费", "key_points": "无需上传服务器（浏览器本地处理）"}
```

**输出**（改写对照）：

| 版本 | 文案 | 判定 |
|---|---|---|
| ❌ 模板句 | An innovative AI-powered PDF toolkit | 「innovative/AI-powered」堆砌，0 信息量 |
| ❌ 说是什么 | A free online PDF tool | 「是什么」不「改变什么」，列表页无记忆点 |
| ✅ 结果句 | Merge PDFs without uploading them（33 字符） | 动词开头 + 差异化卖点（本地处理）入句 |

---

## 示例 3：无数据产品的证据纪律

**输入**：

```json
{"brief": "习惯打卡 App，刚做完还没公测", "key_points": "想写「帮助 10 万人养成习惯」"}
```

**输出**：**拒绝该断言**——无数据支撑。证据核对表标注：

| 断言 | 依据 | 处理 |
|---|---|---|
| 帮助 10 万人养成习惯 | 无（未公测） | ❌ 删除 |
| 「Track 5 habits in one glance」 | 功能事实 | ✅ 保留 |

改为场景描述：「Five habits, one glance, zero guilt-trips.」

---

## 示例 4：违规拦截（incentivized 话术）

**输入**：用户要求在 maker comment 里加「upvote our launch and get 3 months free Pro」。

**输出**：**拒绝并改写**——incentivized upvote 是 PH Guidelines 明令禁止的下架行为。
替代方案：「If you find this useful, a follow on GitHub helps more than an upvote」——
引导关注（合规）而非引导投票（违规）。

---

*本页示例由方法论产出；全部文案人工确认后上传，输出标注 AI 生成内容。*
