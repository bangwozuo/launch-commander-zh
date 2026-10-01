# 测试报告

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行 | ✅ PASS |
| prompt.txt 深度区块（三步骤含失败处理 / 量化规则 / 编排层失败模式 / 编排规则） | ✅ PASS |
| 无占位符残留 | ✅ PASS |
| 无 API Key / 无模型调用 | ✅ PASS |

## 二、脚本实跑（含上游技能串联）

**命令**：

```bash
python scripts/run_flow.py --demo
python scripts/run_flow.py --input examples/input.json --outdir out
```

**运行环境**：Python 3.13（绝对路径解释器）/ openpyxl

| 项 | 结果 |
|---|---|
| 退出码 | 0（demo 与 input 双跑均 0） |
| 上游串联 | hero-image-sellingpoint 子进程调用成功，sellingpoint.json 衔接 ✅ |
| 校验结果 | 通过 4/6：tagline 34 字符 ✅ / gallery ✅ / 视频 45s ✅ / 价格三处一致 ✅ / FAQ 8 条 ⚠️ / 六类覆盖 ⚠️ |
| 整体判定 | ⚠️ 补齐非红线项后进入 T-1（红线未过 0） |
| 产物 1 | `out/素材包校验清单.xlsx`（8.6 KB，❌ 与红线标红） |
| 产物 2 | `out/sellingpoint.json`（上游产物） |
| 产物 3 | `out/kit_result.json`（2.6 KB，对接 T-1 清单） |
| 耗时 | < 3 s（含上游子进程） |

### 红线与边界演练

| 场景 | 结果 |
|---|---|
| 价格打架（$6/mo vs $8/mo） | 红线 ❌ → 「不可进入 T-1」 ✅ |
| tagline 74 字符 | ❌ 「重写（不截断）」 ✅ |
| tagline 缺失 | 标「缺失」待办，不阻断 ✅ |
| FAQ 补齐 + 价格统一 | 6/6 全绿 → ✅ 可进入 T-1 ✅ |

## 三、边界与已知限制

| 限制 | 说明 |
|---|---|
| 不代写素材 | 文案/FAQ 由 producthunt-copy / faq-pregenerate 生成后回填字段 |
| 数量型 FAQ 校验 | 攻击性占比 ≥1/3 由 faq-pregenerate 保证，本流程查数量与覆盖 |
| 视觉规格 | 校验的是声明值（张数/尺寸/时长），实际文件人工核对后上传 |
| 价格口径 | 逐字比对含符号写法（$8/mo ≠ $8/月），对外口径须统一 |

## 四、结论

**通过。** 上游技能真实串联、六项硬约束可查、红线拦截有效（价格打架被正确阻止
进入 T-1）、四类失败处理可演练，产出真实（Excel/JSON）并可交接发布日历流程。

---

*测试报告基于真实实跑输出生成 · 2026-09-30*
