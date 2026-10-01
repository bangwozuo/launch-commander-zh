# 输出示例（模型按 prompt.txt 产出）

> 输入为 `examples/input.json`（ClipMate 中文版主稿 → 英文版重写）。
> 重写而非互译：事实骨架一字不差，表达各自原生。

## 事实骨架（两版必须对应）

| # | 事实 | 中文版表述 | 英文版表述 | 一致 |
|---|---|---|---|---|
| 1 | 开发周期/形态 | 一个人做了两年 | two years, one person | ✅ |
| 2 | 起因故事 | 第 7 次弄丢 API key | my 7th lost API key | ✅ |
| 3 | 存储架构 | 只存本机 SQLite | local SQLite only, never uploaded | ✅ |
| 4 | 搜索性能 | 0.3 秒命中（10 万条实测） | 0.3s hits (tested on 100k entries) | ✅ |
| 5 | 测试环境 | i7/16GB | i7/16GB | ✅ |
| 6 | 附加功能 | 截图 OCR 取字、粘贴去格式 | screenshot OCR, paste-as-plain-text | ✅ |
| 7 | 定价 | 免费 + Pro $8/月 | Free + Pro $8/mo | ✅ |

## 英文版（社区：PH/Reddit，重写稿）

> I've lost count of how many API keys I've lost to the void — the 7th one broke me.
> So I spent two years building the fix for myself:
>
> ClipMate. One shortcut (Ctrl+Shift+V) searches everything you've copied on Windows
> for the last 3 months. Everything lives in a local SQLite file — there's no upload
> code path at all. It also does OCR on screenshots and paste-as-plain-text, so code
> stops exploding chat windows.
>
> Search hits in 0.3s, tested against 100k entries on an i7/16GB box. Free to use;
> Pro is $8/mo if you want OCR, unlimited history, and sync.
>
> Launching on Product Hunt today — happy to answer anything in the comments.

## 中文版（社区：V2EX，原稿，供对照）

> 做了两年，我的剪贴板工具终于要发了。起因是丢了太多次复制过的 API key（丢到第 7 次
> 的时候破防了）。ClipMate 的方案：所有记录只存本机 SQLite，Ctrl+Shift+V 呼出搜索，
> 三个月内内容 0.3 秒命中（i7/16GB、10 万条实测）。顺手做了截图 OCR 取字和粘贴去格式。
> 免费 + Pro $8/月。

## 术语表执行

| 原词 | 英文处理 | 中文处理 | 依据 |
|---|---|---|---|
| ClipMate | 不翻译 | 不翻译 | 产品名永不翻译 |
| tagline | 另案重写：Your clipboard, finally searchable | 你的剪贴板，终于能搜了 | 重写非直译（两案已并列供用户选择） |
| 10 万条 | 100k entries | 10 万条 | 英文社区计数习惯 |
| $8/月 | $8/mo | $8/月 | 通行写法 |
| 破防 | broke me | 破防了 | 文化梗各自原生，不硬搬 |

## 自查清单

### 英文 Chinglish 扫描
- [x] 无 very 滥用
- [x] 无中式搭配直译（improve efficiency greatly 等未出现）
- [x] 无 welcome to use / using experience / good compatibility
- [x] 主语一致（无电报体）
- [x] 冠词与单复数过检
- [x] GitHub / macOS / Windows 大小写正确
- [x] 无硬翻成语（「破防」译为 broke me，语义等价且地道）

### 中文翻译腔扫描
- [x] 无「进行……操作」公文腔
- [x] 无「您」
- [x] 无被动态滥用
- [x] 数字单位为中文习惯（10 万 / $8/月）
- [x] 无英文语序残留

### 事实口径一致性：✅（7/7 骨架项一致）

---

*本结果由 AI 生成，两版均人工确认后发布；输出标注 AI 生成内容。*
