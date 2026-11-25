"""outline_check.py 单测。"""

import json
import unittest

from _loader import load

check = load("outline_check")


def outline(*pages):
    """pages: [(heading, [body lines]), ...] 拼成大纲 Markdown。"""
    lines = ["# 大纲", ""]
    for heading, body in pages:
        lines.append(f"## {heading}")
        lines.extend(body)
        lines.append("")
    return "\n".join(lines)


def messages(report, level):
    return " | ".join(report[level])


# 一份字段填全、仅缺 References 的完整大纲（避免其他 WARN 干扰定位）
FULL_NO_REF = [
    ("背景与动机", [
        "- 结论式标题：聚焦稀疏标注下的小样本识别难题",
        "- 要点：现有方法在标注受限时性能明显下滑",
        "- 讲稿备注：先交代背景与动机，引出待解问题。",
    ]),
    ("研究问题", [
        "- 结论式标题：本研究回答跨域迁移能否降低标注成本",
        "- 要点：明确要验证的核心假设",
        "- 讲稿备注：用一句话说明研究问题与贡献边界。",
    ]),
    ("方法 · 框架", [
        "- 结论式标题：模块化框架逐层完成特征对齐与融合",
        "- 要点：输入、核心模块、输出三段式总览",
        "- 证据 / 图表：框架总图（图 1）",
        "- 讲稿备注：按模块顺序讲解设计动机与创新点。",
    ]),
    ("实验 · 主结果", [
        "- 结论式标题：在 3 个数据集上平均准确率提升 8.2%",
        "- 要点：主对比表突出最优值与基线",
        "- 证据 / 图表：主结果对比表（表 1）",
        "- 讲稿备注：先报主结论，再解释关键数字。",
    ]),
    ("结论与展望", [
        "- 结论式标题：方法在低标注场景下稳定优于基线",
        "- 要点：2–3 条核心结论与后续方向",
        "- 讲稿备注：回扣研究问题，说明局限与下一步。",
    ]),
]


class TestSplitPages(unittest.TestCase):
    def test_split_count(self):
        text = outline(("P1", ["- a"]), ("P2", ["- b"]), ("P3", ["- c"]))
        pages = check.split_pages(text)
        self.assertEqual(len(pages), 3)
        self.assertEqual(pages[0][0], "P1")


class TestCleanSkeleton(unittest.TestCase):
    def test_plan_deck_skeleton_passes(self):
        deck = load("plan_deck")
        for scene in ("defense", "conference", "lab-meeting", "poster"):
            text = deck.build_outline(scene, "题目", 12)
            report = check.evaluate(text, scene=scene)
            self.assertEqual(report["errors"], [], scene)


class TestStructuralRules(unittest.TestCase):
    def test_missing_question_and_conclusion_are_errors(self):
        text = outline(("背景", ["- 要点：背景描述", "- 讲稿备注：备注"]),
                       ("方法", ["- 要点：方法描述", "- 证据：图 1", "- 讲稿备注：备注"]))
        report = check.evaluate(text, scene="defense")
        self.assertTrue(any("研究问题" in e for e in report["errors"]))
        self.assertTrue(any("结论页" in e for e in report["errors"]))

    def test_lab_meeting_exempt_from_question_conclusion(self):
        text = outline(("本周进展", ["- 要点：初步结果", "- 讲稿备注：备注"]),
                       ("问题与卡点", ["- 要点：待解问题", "- 讲稿备注：备注"]),
                       ("下周计划", ["- 要点：任务清单", "- 讲稿备注：备注"]))
        report = check.evaluate(text, scene="lab-meeting")
        self.assertEqual(report["errors"], [])

    def test_missing_references_warns(self):
        report = check.evaluate(outline(*FULL_NO_REF), scene="defense")
        self.assertEqual(report["errors"], [])
        self.assertTrue(any("References" in w or "参考文献" in w for w in report["warnings"]))

    def test_empty_outline_error(self):
        report = check.evaluate("# 无页面", scene="defense")
        self.assertTrue(report["errors"])


class TestPageRules(unittest.TestCase):
    def test_label_title_warns(self):
        text = outline(("研究问题", ["- 结论式标题：研究问题", "- 讲稿备注：备注"]),
                       ("方法", ["- 结论式标题：方法介绍", "- 证据：图 1", "- 讲稿备注：备注"]),
                       ("结论", ["- 结论式标题：方法在 3 项指标上提升 5%", "- 讲稿备注：备注"]))
        report = check.evaluate(text, scene="defense")
        self.assertTrue(any("名词标签" in w for w in report["warnings"]))

    def test_too_many_bullets_warns(self):
        bullets = [f"- 要点 {i}" for i in range(7)]
        text = outline(("研究问题", ["- 结论式标题：本研究回答一个明确疑问", "- 讲稿备注：备注"]),
                       ("方法", bullets + ["- 证据：图 1", "- 讲稿备注：备注"]),
                       ("结论", ["- 结论式标题：方法验证了假设", "- 讲稿备注：备注"]))
        report = check.evaluate(text, scene="defense")
        self.assertTrue(any("bullet 7 条" in w for w in report["warnings"]))

    def test_overlong_body_warns(self):
        long_text = "描述" * 80
        text = outline(("研究问题", ["- 结论式标题：本研究回答明确疑问", "- 讲稿备注：备注"]),
                       ("方法", [f"- 要点：{long_text}", "- 证据：图 1", "- 讲稿备注：备注"]),
                       ("结论", ["- 结论式标题：方法验证假设", "- 讲稿备注：备注"]))
        report = check.evaluate(text, scene="defense")
        self.assertTrue(any("正文偏长" in w for w in report["warnings"]))

    def test_result_page_without_number_warns(self):
        text = outline(("研究问题", ["- 结论式标题：本研究回答明确疑问", "- 讲稿备注：备注"]),
                       ("实验结果", ["- 结论式标题：本方法表现出更好趋势", "- 证据：对比图", "- 讲稿备注：备注"]),
                       ("结论", ["- 结论式标题：方法验证假设", "- 讲稿备注：备注"]))
        report = check.evaluate(text, scene="defense")
        self.assertTrue(any("定量数字" in w for w in report["warnings"]))

    def test_missing_notes_warns(self):
        text = outline(("研究问题", ["- 结论式标题：本研究回答明确疑问"]),
                       ("方法", ["- 结论式标题：框架逐层对齐特征", "- 证据：图 1"]),
                       ("结论", ["- 结论式标题：方法验证假设"]))
        report = check.evaluate(text, scene="defense")
        self.assertEqual(sum("讲稿备注" in w for w in report["warnings"]), 3)


class TestStructureFlowRules(unittest.TestCase):
    def test_thanks_closing_warns(self):
        pages = FULL_NO_REF[:-1] + [("谢谢聆听", ["- 要点：欢迎提问"])]
        report = check.evaluate(outline(*pages), scene="defense")
        self.assertTrue(any("感谢/问答页" in w for w in report["warnings"]))

    def test_conclusion_not_last_warns(self):
        pages = FULL_NO_REF + [("相关阅读", ["- 要点：补充文献", "- 讲稿备注：备注"])]
        report = check.evaluate(outline(*pages), scene="defense")
        self.assertTrue(any("结论页之后仍有主线页面" in w for w in report["warnings"]))

    def test_low_method_result_share_warns(self):
        pages = [
            ("背景", ["- 结论式标题：领域现状尚存未决问题", "- 讲稿备注：备注"]),
            ("相关工作", ["- 结论式标题：现有方法切入点有限", "- 讲稿备注：备注"]),
            ("动机", ["- 结论式标题：标注成本约束落地场景", "- 讲稿备注：备注"]),
            ("研究问题", ["- 结论式标题：本研究回答降本可行性", "- 讲稿备注：备注"]),
            ("方法", ["- 结论式标题：提出单一对齐模块", "- 证据：图 1", "- 讲稿备注：备注"]),
            ("结论", ["- 结论式标题：初步验证了设计思路", "- 讲稿备注：备注"]),
        ]
        report = check.evaluate(outline(*pages), scene="defense")
        self.assertTrue(any("占比" in w for w in report["warnings"]))

    def test_lab_meeting_share_not_flagged(self):
        pages = [
            ("本周进展", ["- 结论式标题：已完成数据收集", "- 讲稿备注：备注"]),
            ("问题与卡点", ["- 结论式标题：训练收敛偏慢", "- 讲稿备注：备注"]),
            ("下周计划", ["- 结论式标题：计划调整学习率", "- 讲稿备注：备注"]),
        ]
        report = check.evaluate(outline(*pages), scene="lab-meeting")
        self.assertFalse(any("占比" in w for w in report["warnings"]))


class TestHelpers(unittest.TestCase):
    def test_looks_like_label(self):
        self.assertTrue(check.looks_like_label("方法"))
        self.assertTrue(check.looks_like_label("实验结果"))
        self.assertFalse(check.looks_like_label("在 3 个数据集上准确率提升 8.2%"))
        self.assertFalse(check.looks_like_label("模块化框架逐层完成特征对齐"))

    def test_count_units(self):
        cjk, latin = check.count_units("提升 8.2%，outperform baseline")
        self.assertGreaterEqual(cjk, 2)
        self.assertEqual(latin, 2)

    def test_report_is_json_serializable(self):
        report = check.evaluate(outline(*FULL_NO_REF), scene="defense")
        text = json.dumps(report, ensure_ascii=False)
        self.assertIn("warnings", text)


if __name__ == "__main__":
    unittest.main()
