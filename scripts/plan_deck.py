#!/usr/bin/env python3
"""按场景生成学术汇报大纲骨架（Markdown）。

骨架只给出页面角色与占位字段，内容由使用者填充；规范见 references/argument.md、
references/scenarios.md。仅用 Python 标准库。

用法:
    python3 plan_deck.py --scene defense --minutes 18 --title "课题题目"
    python3 plan_deck.py --scene conference --minutes 12 --out outline.md
"""

import argparse
import sys

# 场景 -> 页面角色序列（角色名同时用于占位提示）
SCENES = {
    "defense": [
        ("封面", "题目、姓名、导师、专业、日期"),
        ("背景与动机", "领域现状 → 现存问题 → 本课题要解决什么"),
        ("相关工作", "与本方法直接对比的方向及切入点"),
        ("研究问题与贡献", "研究问题独立成页；一句话总贡献 + 2–3 条可核验贡献"),
        ("方法 / 框架（总览）", "总体框架图：输入、核心模型/算法、输出"),
        ("方法 · 模块拆解", "逐模块说明输入、作用、输出与创新点"),
        ("实验 · 数据集与指标", "数据集划分、评价指标、对比基线"),
        ("实验 · 主结果", "主对比表/图，关键发现标注在图上"),
        ("实验 · 定性可视化", "预测 vs 真值、失败案例分组排列"),
        ("实验 · 消融", "每次只变动一个组件，列出各项增益"),
        ("讨论与局限", "回扣研究问题；正面列出主要局限"),
        ("结论与展望", "2–4 条核心结论；后续方向；联系方式"),
    ],
    "conference": [
        ("标题页", "论文标题、作者、单位、会议名称"),
        ("问题与动机", "用具体场景或失败案例切入待解问题"),
        ("研究问题", "明确写出要回答的疑问，不并入动机页"),
        ("方法 · 总览", "一张总览图讲清思路"),
        ("方法 · 创新点", "核心创新逐条展开，配关键模块示意"),
        ("实验 · 主结果", "主表/主图放最显眼位置"),
        ("实验 · 对比与可视化", "1–2 个最有说服力的对比与定性结果"),
        ("结论", "一句话总结 + 局限；此页留屏给问答"),
    ],
    "lab-meeting": [
        ("本周进展", "做了什么、初步结果，配最小必要图表"),
        ("问题与卡点", "现象、已尝试方案、未解决原因、需要协助的点"),
        ("下周计划", "可执行任务清单、预期产出与时间节点"),
        ("相关阅读（可选）", "本周论文要点与对课题的启发"),
    ],
    "poster": [
        ("背景与动机", "从海报摘要/动机模块抽取"),
        ("研究问题", "海报要回答的核心疑问"),
        ("方法", "海报框架图对应方法主图"),
        ("结果 · 定量", "保留定量表格与关键曲线"),
        ("结果 · 定性", "保留关键定性对比"),
        ("结论", "核心结论与边界"),
    ],
}

SCENE_LABELS = {
    "defense": "学位 / 开题 / 毕业答辩",
    "conference": "会议 / 期刊口头报告",
    "lab-meeting": "课题组会 / 周报汇报",
    "poster": "学术海报转 PPT",
}

PLACEHOLDER_TITLE = "〔结论式标题：一句陈述本页 so-what，而非名词标签〕"
PLACEHOLDER_EVIDENCE = "〔证据 / 图表：一页一证据，标注关键发现与来源〕"
PLACEHOLDER_NOTE = "〔讲稿备注：3–5 句可直接照读的话，不照念 bullet〕"


def build_outline(scene: str, title: str, minutes: int) -> str:
    pages = SCENES[scene]
    lines = []
    lines.append(f"# 汇报大纲 · {SCENE_LABELS[scene]}")
    lines.append("")
    lines.append(f"- 题目：{title or '〔待填写〕'}")
    lines.append(f"- 总时长：{minutes} 分钟")
    lines.append(f"- 场景：{scene}")
    lines.append("")
    lines.append("> 填写要求：标题写成结论句；每页一个论证角色；证据直接支撑标题。")
    lines.append("")
    for i, (role, hint) in enumerate(pages, start=1):
        lines.append(f"## P{i:02d} · {role}")
        lines.append(f"- 结论式标题：{PLACEHOLDER_TITLE}")
        lines.append(f"- 页面要点：{hint}")
        lines.append(f"- {PLACEHOLDER_EVIDENCE}")
        lines.append(f"- {PLACEHOLDER_NOTE}")
        lines.append("")
    if scene != "lab-meeting":
        lines.append("## 参考文献 / References")
        lines.append("- 按统一格式列出借用的图、数据、主张对应文献；页内标注图号与出处。")
        lines.append("")
    lines.append("## 附录（按需）")
    lines.append("- 预置问答页、补充消融、额外数据集、详细推导；单独标注编号。")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="生成学术汇报大纲骨架")
    parser.add_argument("--scene", required=True, choices=list(SCENES.keys()),
                        help="场景：" + ", ".join(SCENES.keys()))
    parser.add_argument("--minutes", type=int, default=15, help="总时长（分钟）")
    parser.add_argument("--title", default="", help="汇报题目")
    parser.add_argument("--out", help="可选：写入 Markdown 文件路径")
    args = parser.parse_args()

    outline = build_outline(args.scene, args.title, args.minutes)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(outline)
        print(f"已写入 {args.out}（{len(SCENES[args.scene])} 个主线页面骨架）")
    else:
        print(outline)


if __name__ == "__main__":
    main()
