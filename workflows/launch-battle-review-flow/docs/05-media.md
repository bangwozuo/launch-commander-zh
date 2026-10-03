# 截图与录屏

> 以下素材均来自**真实执行**：`--run` 实拍终端 / 实跑产物文件，无摆拍。

## 演示视频

![演示视频](assets/demo.mp4)

*Hyperframes 动态渲染 15s：命令逐字敲入（光标闪烁）→ 21 行真实输出逐行流式 → 实跑产物 Ken Burns 缓推*

## 执行截图

![真实执行](assets/run-terminal.png)

## 实跑产物

| 文件 | 说明 |
|---|---|
| [`out/_battle_input.json`](out/_battle_input.json) | 结构化结果（实跑生成） · 2 KB |
| [`out/_demo_input.json`](out/_demo_input.json) | 结构化结果（实跑生成） · 4 KB |
| [`out/_emotion_input.json`](out/_emotion_input.json) | 结构化结果（实跑生成） · 1 KB |
| [`out/battle_report.json`](out/battle_report.json) | 结构化结果（实跑生成） · 3 KB |
| [`out/emotion_scan.json`](out/emotion_scan.json) | 结构化结果（实跑生成） · 4 KB |
| [`out/review_result.json`](out/review_result.json) | 结构化结果（实跑生成） · 2 KB |
| [`out/发布战报.xlsx`](out/发布战报.xlsx) | Excel 工作簿（实跑生成） · 9 KB |
| [`out/复盘报告.xlsx`](out/复盘报告.xlsx) | Excel 工作簿（实跑生成） · 7 KB |
| [`out/平台流量对比.png`](out/平台流量对比.png) | 图表产物（实跑生成） · 27 KB |
| [`out/当日流量曲线.png`](out/当日流量曲线.png) | 图表产物（实跑生成） · 57 KB |
| [`out/情绪分布.png`](out/情绪分布.png) | 图表产物（实跑生成） · 26 KB |
| [`out/评论分类清单.xlsx`](out/评论分类清单.xlsx) | Excel 工作簿（实跑生成） · 10 KB |


---

## 附录：实跑输出明细

> 本资产为纯提示词客户端资产，无界面可截图。以下为**实跑运行效果**。

## 运行效果

### 输入

```json
{
  "input": "请提供工作流的初始输入数据"
}

```

### 输出

## 执行摘要

初始输入为占位提示，缺少各平台发布数据，工作流无法继续执行。

> **AI 生成内容**

## 分步结果

1. 步骤 1：评论情绪识别 — 跳过，原因：无数据输入。
2. 步骤 2：战报生成 — 跳过，原因：上一步无输出，且缺少 metrics/period 等核心字段。

## 最终交付物

无。请提供包含各平台数据的初始输入后重新执行。


---

*运行效果由实跑验证生成*
