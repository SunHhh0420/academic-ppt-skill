---
name: academic-ppt
description: "学术汇报演示文稿的论证规划与内容规范指南，覆盖学位/开题/毕业答辩、会议与期刊口头报告、课题组会周报、学术海报转 PPT 四类场景。专注学术论证质量：核心主张提炼、叙事脊柱、结论式标题（action title）、主张—证据映射、证据纪律、定量结果与引用规范、页面架构、时间预算、讲稿与答辩问答，并提供交付前学术 QA 清单。当用户需要制作、重构、精简或评审学术 PPT、答辩幻灯片、会议报告 slides、组会进展汇报，或从论文/学术海报提炼演示文稿时使用。本 Skill 只沉淀论证、结构与规范，不绑定具体渲染工具；实际幻灯片文件生成交由环境中现有 PPT 工具执行。"
---

# Academic PPT

## Overview

把论文、课题进展或学术海报转化为论证清晰、证据扎实、符合顶会/答辩标准的演示文稿。本 Skill 是**规划与规范层**，聚焦学术论证质量——主张是否锐利、证据链是否严谨、叙事是否成立；不直接渲染幻灯片，落地为 `.pptx`/在线 Slides 时调用环境中已有的 PPT 制作能力。

与通用 PPT Skill 的分工：通用工具负责怎么把页面写出来（版式实现、图表库、导出）；本 Skill 负责这页该不该存在、主张是什么、证据是否撑得住、讲稿与问答怎么准备。

## Workflow

按 **Plan → Do → Check** 推进，每阶段结束先过对应自检。

### Plan（规划，动手排版前）

1. **判定场景与模式**：确认汇报类型、总时长、页数上限、听众；区分结构化论证（学术默认）与视觉叙事模式。见 [references/scenarios.md](references/scenarios.md)。
2. **提炼主张与证据**：写出一句话研究问题/核心主张，列出 2–3 条关键证据；选定一条叙事脊柱（SCR / 漏斗 / 结论先行）。见 [references/argument.md](references/argument.md)。
3. **搭逐页大纲**：一页一个论证角色，标题写结论句；标注每页主张与所需证据；做主张—证据映射。
4. **结构测试**：通过幽灵稿测试（标题连读成完整论证）与衔接测试（每页是上一页的自然推论）；规划研究问题页、结论页与附录。见 [references/argument.md](references/argument.md) 与 [references/deck-architecture.md](references/deck-architecture.md)。
5. **确认架构与预算**：核对完整页面架构、引用安排、页数预算与可砍页标记。见 [references/deck-architecture.md](references/deck-architecture.md)。

### Do（逐页制作）

6. **套用版式与视觉规范**：按 [references/design.md](references/design.md) 确定层级、配色、字体、对齐与留白；方法页为视觉中心，背景介绍压缩；遵守文本纪律与学术禁止项。
7. **组织证据与图表**：按 [references/figures-tables.md](references/figures-tables.md) 一页一证据、图上标注关键发现、保证基线/指标/口径齐全；定量结果优先于定性描述。
8. **配套讲稿与问答**：按 [references/speaker-notes.md](references/speaker-notes.md) 写逐页口播备注，预判 5–10 个问答并预置附录页。

### Check（交付前复核）

9. **学术 QA**：按 [references/checklist.md](references/checklist.md) 分组过规划、论证、证据、引用、文本视觉与时间讲稿清单；不达标先修复再交付。
10. **落地生成**：把确认后的大纲、规范与素材交给现有 PPT 工具生成文件；成稿后再次过 QA 清单复核。

## Core Principles

- **主张先行，一次一论点**：先讲研究问题与结论，再倒推支撑；限时内能有力证明的那个论点才是主线，其余进附录。
- **结论式标题**：每页标题是一句完整陈述结论的话，不是名词标签；连读标题应讲得出完整故事。
- **方法为视觉中心**：方法/框架/流程图占最大版面；结果页紧随其后用定量证据支撑；背景压缩为少量铺垫。
- **证据纪律**：一页一证据；证据必须撑得住标题；关键发现直接标在图上；页面脱离讲稿也能读懂。
- **定量优先，主张匹配证据等级**：关键主张有数字、指标或对照实验支撑；有对照才说"优于"，只有趋势就说"提示/初步"。
- **引用与诚信**：借用的图、数据、主张页内标注来源，末尾设 References 页；不编造数据与引用。
- **讲稿承载论证，页面承载证据**：幻灯片给锚点与证据，讲者口头展开推理；正文精简，不照念 bullet。
- **克制去 AI 感**：一套字体、一个主色加中性色；无卡片、色条、装饰图标与渐变阴影；留白即清晰。

## Reference Map

| 需求 | 读取文件 |
| --- | --- |
| 主张提炼、叙事脊柱、结论式标题、幽灵稿/衔接测试 | [references/argument.md](references/argument.md) |
| 四场景结构配比、模式选择、领域子类型侧重 | [references/scenarios.md](references/scenarios.md) |
| 完整页面架构、附录、引用规范、时间预算与砍页预案 | [references/deck-architecture.md](references/deck-architecture.md) |
| 版式层级、配色字体、文本纪律、学术禁止项、无障碍 | [references/design.md](references/design.md) |
| 证据纪律、图表选型、定量对比表、消融与可视化规范 | [references/figures-tables.md](references/figures-tables.md) |
| 逐页讲稿、时间分配、问答预判与应答、附录映射 | [references/speaker-notes.md](references/speaker-notes.md) |
| 交付前分组学术 QA 清单 | [references/checklist.md](references/checklist.md) |

## Execution Notes

- 本 Skill 不绑定特定渲染工具；生成 `.pptx` 或在线 Slides 时遵循环境中现有 PPT Skill 的流程与模板，仅把本指南的论证结构、证据规范与 QA 清单作为约束传入。
- 若用户提供论文、海报或笔记作为素材，先通读并抽取要点（图、表、公式中的信息不可遗漏），再进入 Plan 阶段；不要在素材未读完时直接套模板。
- 多轮迭代时，优先调整主张锐利度、证据链与讲稿，而非增删无关装饰元素。
