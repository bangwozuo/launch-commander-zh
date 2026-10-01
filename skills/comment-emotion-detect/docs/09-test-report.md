# 测试报告

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行 | ✅ PASS |
| prompt.txt 深度区块（五类标签 / 六类风险 / 规则树 / SLA 表 / 健康线 / 禁止事项 / 合规） | ✅ PASS |
| 无占位符残留 | ✅ PASS |
| 无 API Key / 无模型调用 | ✅ PASS |

## 二、脚本实跑

**命令**：

```bash
python scripts/emotion_scan.py --demo
python scripts/emotion_scan.py --input examples/input.json --outdir out
```

**运行环境**：Python 3.13（`C:\Users\nsxzy\.workbuddy\binaries\python\envs\default\Scripts\python.exe`）/ openpyxl / matplotlib

| 项 | 结果 |
|---|---|
| 退出码 | 0（demo 与 input 双跑均 0） |
| 分类结果 | 7 条：正 1 / 负 0 / 中 2 / 疑 1 / 风险 3 |
| P0+P1 | 3 条（退款诉求 / 抄袭指控 / 隐私质疑） |
| 产物 1 | `out/评论分类清单.xlsx`（10.3 KB，三 sheet，风险行标红） |
| 产物 2 | `out/情绪分布.png`（26.4 KB 饼图） |
| 产物 3 | `out/emotion_scan.json`（4.4 KB，机器可读） |
| 耗时 | < 1 s |

### 分类明细核对（真实输出）

```
P0  angry_bob      🔴 退款诉求       （refund 命中）
P0  skeptic_pete   🔴 抄袭/竞品指控   （copy of 命中）
P0  隐私控          🔴 安全/隐私质疑  （上传服务器 命中）
P2  dev_sarah      🔵 疑问          （Does it support 命中）
P3  maker_fan99    🟢 正面          （love+finally；bloated 否定翻转）
P4  老王聊软件      ⚪ 中性+功能请求   （愿望句式不计好评）
P4  潜水员          ⚪ 中性
```

### 防误报核对

| 检查 | 结果 |
|---|---|
| 「doesn't feel bloated」误判差评 | 0（否定窗口 12 字符生效） |
| 「希望加上 OCR…就好了」误判好评 | 0（功能请求单独标记） |
| 「refund」漏检 | 0（风险规则大小写不敏感） |
| 中英混排（V2EX 中文 + PH 英文） | 正常 |

## 三、边界与已知限制

| 限制 | 说明 |
|---|---|
| 词表非穷尽 | 反讽、隐喻、图片评论须模型按 prompt.txt 复核 |
| 刷量号识别 | 脚本不做账号行为分析；同 ID 短时雷同好评由模型复核 |
| 截断文本 | 摘录仅前 40 字供人看，打分用全文；输入须传全文 |
| 平台语言 | 词表覆盖中英双语；小语种评论（日/韩）暂不支持 |

## 四、结论

**通过。** 结构与实跑双向验证达标；三类 P0 风险全部命中，否定翻转与功能请求修正生效，
脚本产出真实文件（Excel/PNG/JSON）。

---

*测试报告基于真实实跑输出生成 · 2026-09-30*
