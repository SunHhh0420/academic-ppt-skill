#!/usr/bin/env python3
"""学术大纲规范自检脚本。

读取一份 Markdown 大纲，按 references/checklist.md 的规划与论证规则做确定性检查：
- 结构性（ERROR）：是否缺少研究问题页、结论页（组会周报豁免）
- 规范性（WARN）：
  - 标题是否疑似名词标签（而非结论式标题）
  - 单页 bullet 是否超过 5 条
  - 单页正文是否超长（中文 >120 字 / 英文 >40 词）
  - 方法/结果页是否标注证据或图表
  - 方法/结果页是否含定量数字
  - 内容页是否填写讲稿备注
  - 是否缺少 References 页
  - 是否以“谢谢聆听”等空页收尾、结论页是否位于主线末尾
  - 方法/结果类页面占比是否低于一半

仅用 Python 标准库。退出码：存在 ERROR 返回 1，否则 0（WARN 不影响退出码）。

用法:
    python3 outline_check.py outline.md
    python3 outline_check.py outline.md --scene conference --json
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
REFERENCE_RE = re.compile(r"参考文献|references?|引用列表", re.I)
THANKS_RE = re.compile(r"谢谢|感谢聆听|感谢各位|thanks?|thank you|q\s*&?\s*a|问答环节", re.I)
EVIDENCE_RE = re.compile(r"图|表|基线|指标|数据|实验|可视化|曲线|矩阵|消融|对比|样本|数据集")
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?%?")
METHOD_RESULT_RE = re.compile(r"方法|实验|结果|消融|对比")
# 不做填充质量检查的页面角色（封面/目录/附录/参考文献）
SHELL_PAGE_RE = re.compile(r"封面|标题页|目录|附录|参考文献|references?|谢谢|感谢|问答", re.I)

MAX_BULLETS = 5
MAX_CJK_CHARS = 120
MAX_LATIN_WORDS = 40
MIN_METHOD_RESULT_SHARE = 0.50

FIELD_PREFIXES = ("结论式标题", "证据", "讲稿", "页面要点")
NOTE_FIELD_RE = re.compile(r"讲稿")


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
    latin = len(re.findall(r"[A-Za-z][A-Za-z0-9]*", text))
    return cjk, latin


def looks_like_label(title: str) -> bool:
    """启发式：标题是否更像名词标签而非结论句。"""
    cleaned = re.sub(r"[·:：\-_〔〕\[\]()（）]", " ", title).strip()
    if not cleaned:
        return True
    if ACTION_SIGNALS.search(title):
        return False
    words = [w for w in re.split(r"\s+", cleaned) if w]
    if len(words) <= 2 and any(w in LABEL_WORDS or any(lw in w for lw in LABEL_WORDS) for w in words):
        return True
    return False


def _is_field_line(line: str) -> bool:
    return any(line.strip().startswith(f"- {p}") or line.strip().startswith(f"-〔{p}")
               for p in FIELD_PREFIXES)


def _is_placeholder(body: list) -> bool:
    """整页仍是骨架占位（含〔〕占位符）时，跳过填充质量类检查。"""
    return any("〔" in l for l in body)


def check_page(heading: str, body: list) -> list:
    """返回本页 issues，每项为 (level, message)。"""
    issues = []
    body_text = "\n".join(body)
    placeholder = _is_placeholder(body)
    shell = bool(SHELL_PAGE_RE.search(heading))

    bullets = [l for l in body if re.match(r"^\s*[-*]\s+", l) and not _is_field_line(l)]

    # 提取“结论式标题”字段的实际填写值（占位符跳过）
    title_value = ""
    for l in body:
        m = re.match(r"^\s*[-*]\s*结论式标题[:：]\s*(.+)$", l)
        if m:
            title_value = m.group(1).strip()
            break
    title_candidate = title_value or heading
    title_is_placeholder = "〔" in title_candidate or "[" in title_candidate

    # 标题疑似名词标签（占位骨架不判）
    if not title_is_placeholder and looks_like_label(title_candidate):
        issues.append(("WARN", "标题疑似名词标签，应写成一句陈述结论的话"))

    # bullet 数量
    if len(bullets) > MAX_BULLETS:
        issues.append(("WARN", f"bullet {len(bullets)} 条，超过 {MAX_BULLETS} 条上限"))

    # 正文长度（排除占位符行后统计）
    real_body = "\n".join(l for l in body if "〔" not in l and "[" not in l)
    cjk, latin = count_units(real_body)
    if cjk > MAX_CJK_CHARS or latin > MAX_LATIN_WORDS:
        issues.append(("WARN", f"正文偏长（中文 {cjk} 字 / 英文 {latin} 词），建议拆页或移入附录"))

    # 方法/结果类页面的证据与定量检查（壳页与占位页跳过）
    if METHOD_RESULT_RE.search(heading) and not shell and not placeholder:
        if not EVIDENCE_RE.search(body_text):
            issues.append(("WARN", "方法/结果页未标注证据或图表"))
        if not NUMBER_RE.search(body_text):
            issues.append(("WARN", "方法/结果页未见定量数字（指标/数值/百分比），关键结论需有数据支撑"))

    # 内容页讲稿备注（壳页与占位页跳过）
    if not shell and not placeholder and not NOTE_FIELD_RE.search(body_text):
        issues.append(("WARN", "未填写讲稿备注（3–5 句可直接照读的口播）"))

    return issues


def evaluate(text: str, scene: str = "defense") -> dict:
    """对整份大纲做校验，返回结构化报告。"""
    pages = split_pages(text)
    report = {"scene": scene, "pages": [], "errors": [], "warnings": []}

    if not pages:
        report["errors"].append("未识别到任何二级标题（## ）页面，请检查大纲格式")
        return report

    headings = " ".join(h for h, _ in pages)
    main_pages = [(h, b) for h, b in pages if not SHELL_PAGE_RE.search(h)]

    # 结构性必备页（组会周报豁免研究问题页与结论页）
    if scene != "lab-meeting":
        if not QUESTION_RE.search(headings):
            report["errors"].append("缺少独立的研究问题/假设页")
        if not CONCLUSION_RE.search(headings):
            report["errors"].append("缺少结论页（结论页应在问答阶段留屏）")
        if not REFERENCE_RE.search(headings):
            report["warnings"].append("缺少 References / 参考文献页；借用的图、数据、主张需标注来源")

    # 逐页检查
    for i, (heading, body) in enumerate(pages, start=1):
        issues = check_page(heading, body)
        report["pages"].append({"page": i, "heading": heading, "issues": issues})
        for level, msg in issues:
            report["errors" if level == "ERROR" else "warnings"].append(f"{heading}：{msg}")

    # 收尾页：不应以感谢/问答空页作为整份大纲的最后一页
    last_heading = pages[-1][0]
    if THANKS_RE.search(last_heading) and not CONCLUSION_RE.search(last_heading):
        report["warnings"].append("主线最后一页是感谢/问答页，结论页应作为主线收尾并留屏给问答")

    if main_pages:
        # 结论页位置：结论之后不应再出现非附录主线页
        conclusion_idx = next((idx for idx, (h, _) in enumerate(main_pages)
                               if CONCLUSION_RE.search(h)), None)
        if conclusion_idx is not None and conclusion_idx != len(main_pages) - 1:
            report["warnings"].append("结论页之后仍有主线页面；结论应位于主线末尾，其余内容移入附录")

        # 方法/结果页面占比（组会周报不强调完整方法-结果闭环，豁免）
        if scene != "lab-meeting":
            mr_pages = [h for h, _ in main_pages if METHOD_RESULT_RE.search(h)]
            if main_pages:
                share = len(mr_pages) / len(main_pages)
                if share < MIN_METHOD_RESULT_SHARE:
                    report["warnings"].append(
                        f"方法/结果类页面占比 {share * 100:.0f}%，低于 {MIN_METHOD_RESULT_SHARE * 100:.0f}%；"
                        "应压缩背景与相关工作，扩充方法与结果")

    return report


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

    report = evaluate(text, scene=args.scene)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"共解析 {len(report['pages'])} 页")
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
