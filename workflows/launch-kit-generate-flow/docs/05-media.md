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
| [`out/_demo_input.json`](out/_demo_input.json) | 结构化结果（实跑生成） · 2 KB |
| [`out/kit_result.json`](out/kit_result.json) | 结构化结果（实跑生成） · 2 KB |
| [`out/sellingpoint.json`](out/sellingpoint.json) | 结构化结果（实跑生成） · 3 KB |
| [`out/卖点评分对比.png`](out/卖点评分对比.png) | 图表产物（实跑生成） · 31 KB |
| [`out/卖点评分清单.xlsx`](out/卖点评分清单.xlsx) | Excel 工作簿（实跑生成） · 9 KB |
| [`out/素材包校验清单.xlsx`](out/素材包校验清单.xlsx) | Excel 工作簿（实跑生成） · 8 KB |


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

初始输入为占位提示，缺少产品信息，工作流无法继续执行。

> **AI 生成内容**

## 分步结果

1. 步骤 1：Product Hunt 文案 — 跳过，原因：无 brief/key_points 可输入。
2. 步骤 2：首图卖点提炼 — 跳过，原因：上一步无输出，且无 items 可提炼。
3. 步骤 3：FAQ 预生成 — 跳过，原因：上一步无输出，且无 subject 可预生成。

## 最终交付物

无。请提供包含产品 brief 与核心信息的初始输入后重新执行。


---

*运行效果由实跑验证生成*
