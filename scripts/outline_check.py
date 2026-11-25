#!/usr/bin/env python3
"""学术大纲规范自检脚本。

读取一份 Markdown 大纲，按 references/checklist.md 的规划与论证规则做确定性检查：
- 是否缺少研究问题页、结论页
- 标题是否疑似名词标签（而非结论式标题）
- 单页 bullet 是否超过 5 条
- 单页正文是否超长（中文 >120 字 / 英文 >40 词）
- 结果/方法页是否标注了证据或图表

仅用 Python 标准库。退出码：存在 ERROR 返回 1，否则 0（WARN 不影响退出码）。

用法:
    python3 outline_check.py outline.md
    python3 outline_check.py outline.md --json
"""

import argparse
import json
import re
import sys

LABEL_WORDS = {"方法", "结果", "数据", "相关工作", "实验", "讨论", "引言", "背景",
               "介绍", "概述", "目的", "材料", "结论", "References", "参考文献"}
ACTION_SIGNALS = re.compile(
    r"(\d|\d+%|提升|优于|降低|减少|解决|表明|发现|证明|揭示|实现|稳定|显著|"
    r"对比|下降|上升|超过|达到|缓解|消除|验证|支持|说明|改善|缩小|提高|"
    r"shows?|demonstrates?|improves?|reduces?|increases?|effect|does|can|outperform)")
QUESTION_RE = re.compile(r"研究问题|研究疑问|假设|待回答|RQ|research question|hypothesis", re.I)
CONCLUSION_RE = re.compile(r"结论|总结|conclusion|小结", re.I)
EVIDENCE_RE = re.compile(r"图|表|基线|指标|数据|实验|可视化|曲线|矩阵|消融|对比|样本|数据集")

MAX_BULLETS = 5
MAX_CJK_CHARS = 120
MAX_LATIN_WORDS = 40


def split_pages(text: str):
    """按二级标题切分页面，返回 [(heading, body_lines)]。"""
    pages = []
    current_heading = None
    current_body = []
    for line in text.splitlines():
        if line.strip().startswith("## "):
            if current_heading is not None:
                pages.append((current_heading, current_body))
            current_heading = line.strip()[3:].strip()
            current_body = []
        elif current_heading is not None:
            current_body.append(line)
    if current_heading is not None:
        pages.append((current_heading, current_body))
    return pages


def count_units(text: str):
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z0-9]+", text))
    return cjk, latin


def looks_like_label(title: str) -> bool:
    """启发式：标题是否更像名词标签而非结论句。"""
    cleaned = re.sub(r"[·:：\-_〔〕\[\]()（）]", " ", title).strip()
    if not cleaned:
        return True
    if ACTION_SIGNALS.search(title):
        return False
    # 标题主要由标签词构成，且很短（子串匹配）
    words = [w for w in re.split(r"\s+", cleaned) if w]
    if len(words) <= 2 and any(w in LABEL_WORDS or any(lw in w for lw in LABEL_WORDS) for w in words):
        return True
    return False


FIELD_PREFIXES = ("结论式标题", "证据", "讲稿", "页面要点")


def check_page(idx: int, heading: str, body: list):
    issues = []
    body_text = "\n".join(body)

    def is_field_line(line: str) -> bool:
        return any(line.strip().startswith(f"- {p}") or line.strip().startswith(f"-〔{p}")
                   for p in FIELD_PREFIXES)

    bullets = [l for l in body if re.match(r"^\s*[-*]\s+", l) and not is_field_line(l)]

    # 提取“结论式标题”字段的实际填写值（占位符跳过）
    title_value = ""
    for l in body:
        m = re.match(r"^\s*[-*]\s*结论式标题[:：]\s*(.+)$", l)
        if m:
            title_value = m.group(1).strip()
            break
    title_candidate = title_value or heading
    is_placeholder = "〔" in title_candidate or "[" in title_candidate

    # 标题疑似名词标签（占位骨架不判）
    if not is_placeholder and looks_like_label(title_candidate):
        issues.append(("WARN", "标题疑似名词标签，应写成一句陈述结论的话"))

    # bullet 数量
    if len(bullets) > MAX_BULLETS:
        issues.append(("WARN", f"bullet {len(bullets)} 条，超过 {MAX_BULLETS} 条上限"))

    # 正文长度（排除占位符行后统计）
    real_body = "\n".join(
        l for l in body if "〔" not in l and "[" not in l
    )
    cjk, latin = count_units(real_body)
    if cjk > MAX_CJK_CHARS or latin > MAX_LATIN_WORDS:
        issues.append(("WARN", f"正文偏长（中文 {cjk} 字 / 英文 {latin} 词），建议拆页或移入附录"))

    # 方法/结果页应有证据标注
    if re.search(r"方法|实验|结果|消融|对比", heading) and not EVIDENCE_RE.search(body_text):
        issues.append(("WARN", "方法/结果页未标注证据或图表"))

    return issues


def main():
    parser = argparse.ArgumentParser(description="学术大纲规范自检")
    parser.add_argument("file", help="大纲 Markdown 文件路径")
    parser.add_argument("--scene", default="defense",
                        choices=["defense", "conference", "lab-meeting", "poster"],
                        help="汇报场景；lab-meeting（组会周报）不强制研究问题页与结论页")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    args = parser.parse_args()

    try:
        text = open(args.file, encoding="utf-8").read()
    except OSError as e:
        print(f"无法读取文件：{e}", file=sys.stderr)
        sys.exit(2)

    pages = split_pages(text)
    report = {"pages": [], "errors": [], "warnings": []}

    if not pages:
        report["errors"].append("未识别到任何二级标题（## ）页面，请检查大纲格式")
    else:
        headings = " ".join(h for h, _ in pages)
        # 组会周报以进展/卡点/计划为主，不强制研究问题页与结论页
        if args.scene != "lab-meeting":
            if not QUESTION_RE.search(headings):
                report["errors"].append("缺少独立的研究问题/假设页")
            if not CONCLUSION_RE.search(headings):
                report["errors"].append("缺少结论页（结论页应在问答阶段留屏）")

        for i, (heading, body) in enumerate(pages, start=1):
            issues = check_page(i, heading, body)
            page_entry = {"page": i, "heading": heading, "issues": issues}
            report["pages"].append(page_entry)
            for level, msg in issues:
                report["errors" if level == "ERROR" else "warnings"].append(f"{heading}：{msg}")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"共解析 {len(pages)} 页")
        for entry in report["pages"]:
            if entry["issues"]:
                print(f"\n{entry['heading']}")
                for level, msg in entry["issues"]:
                    print(f"  [{level}] {msg}")
        print("\n=== 汇总 ===")
        for e in report["errors"]:
            print(f"  [ERROR] {e}")
        for w in report["warnings"]:
            print(f"  [WARN] {w}")
        if not report["errors"] and not report["warnings"]:
            print("  全部通过。")

    sys.exit(1 if report["errors"] else 0)


if __name__ == "__main__":
    main()
