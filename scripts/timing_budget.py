#!/usr/bin/env python3
"""学术汇报时长预算与章节配比计算器。

根据总时长与场景，给出主线页数预算、各章节时间配比，以及方法/结果占比校验。
仅用 Python 标准库。

用法:
    python3 timing_budget.py --minutes 15 --scene defense
    python3 timing_budget.py --minutes 10 --scene conference --out budget.md
"""

import argparse
import sys

# 场景 -> 章节时间配比（占总讲解时间的比例，合计 1.0）
SCENES = {
    "defense": {
        "label": "学位 / 开题 / 毕业答辩",
        "sections": [
            ("背景与动机", 0.15),
            ("相关工作", 0.05),
            ("研究问题与贡献", 0.10),
            ("方法 / 框架", 0.35),
            ("实验与结果", 0.25),
            ("结论与展望", 0.10),
        ],
        "pages_per_minute": 1.0,
        "note": "开题可弱化已完成结果、强化研究计划；毕业答辩须以定量结果支撑工作量。",
    },
    "conference": {
        "label": "会议 / 期刊口头报告",
        "sections": [
            ("问题与动机", 0.12),
            ("研究问题", 0.08),
            ("方法", 0.35),
            ("实验结果", 0.35),
            ("结论", 0.10),
        ],
        "pages_per_minute": 0.9,
        "note": "严格卡时长；超时先砍相关工作与次要消融，保留主方法与主结果。",
    },
    "lab-meeting": {
        "label": "课题组会 / 周报汇报",
        "sections": [
            ("本周进展", 0.50),
            ("问题与卡点", 0.30),
            ("下周计划", 0.20),
        ],
        "pages_per_minute": 1.1,
        "note": "不追求完整叙事闭环；未完成实验如实标注进行中/待补。",
    },
    "poster": {
        "label": "学术海报转 PPT",
        "sections": [
            ("背景与动机", 0.15),
            ("研究问题", 0.10),
            ("方法", 0.30),
            ("结果", 0.30),
            ("结论", 0.15),
        ],
        "pages_per_minute": 1.0,
        "note": "海报并列模块按论证顺序分页；过密一页拆成 2–3 张。",
    },
}

METHOD_RESULT_KEYWORDS = ("方法", "实验", "结果")


def compute_budget(minutes: int, scene: str):
    cfg = SCENES[scene]
    # 页数预算：约一页一分钟，按场景系数四舍五入，标题/参考文献不计入
    content_pages = round(minutes * cfg["pages_per_minute"])
    rows = []
    method_result_share = 0.0
    for name, share in cfg["sections"]:
        sec_min = round(minutes * share, 1)
        rows.append((name, share, sec_min))
        if any(k in name for k in METHOD_RESULT_KEYWORDS):
            method_result_share += share
    return cfg, content_pages, rows, method_result_share


def render(minutes: int, scene: str) -> str:
    cfg, pages, rows, mr_share = compute_budget(minutes, scene)
    lines = []
    lines.append(f"# 时长预算 · {cfg['label']}")
    lines.append("")
    lines.append(f"- 总时长：{minutes} 分钟")
    lines.append(f"- 主线内容页数预算：约 {pages} 页（不含标题页与参考文献页）")
    lines.append(f"- 建议收尾：提前 1–2 分钟结束，预留提问与停顿缓冲")
    lines.append("")
    lines.append("| 章节 | 时间占比 | 讲解时长（分钟） |")
    lines.append("| --- | --- | --- |")
    for name, share, sec_min in rows:
        lines.append(f"| {name} | {share * 100:.0f}% | {sec_min} |")
    lines.append("")
    lines.append(f"- 方法 + 结果合计占比：{mr_share * 100:.0f}%（学术汇报应不低于 50%）")
    if mr_share < 0.50:
        lines.append("- ⚠️ 方法与结果占比不足一半，需压缩背景与相关工作。")
    lines.append(f"- 提示：{cfg['note']}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="学术汇报时长预算与章节配比")
    parser.add_argument("--minutes", type=int, required=True, help="总汇报时长（分钟）")
    parser.add_argument("--scene", required=True, choices=list(SCENES.keys()),
                        help="场景：" + ", ".join(SCENES.keys()))
    parser.add_argument("--out", help="可选：写入 Markdown 文件路径")
    args = parser.parse_args()

    if args.minutes <= 0:
        print("错误：时长必须为正整数分钟。", file=sys.stderr)
        sys.exit(1)

    report = render(args.minutes, args.scene)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"已写入 {args.out}")
    else:
        print(report)


if __name__ == "__main__":
    main()
