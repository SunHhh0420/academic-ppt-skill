"""plan_deck.py 单测。"""

import unittest

from _loader import load

deck = load("plan_deck")


def page_headings(text: str):
    return [line[3:].strip() for line in text.splitlines() if line.strip().startswith("## ")]


class TestBuildOutline(unittest.TestCase):
    def test_all_scenes_nonempty(self):
        for scene in deck.SCENES:
            text = deck.build_outline(scene, "课题题目", 12)
            self.assertIn("课题题目", text)
            self.assertTrue(page_headings(text))

    def test_main_page_count_matches_scene(self):
        for scene, roles in deck.SCENES.items():
            text = deck.build_outline(scene, "", 12)
            headings = page_headings(text)
            # 主线角色页 + 附录页；非组会再加 References 页
            extra = 2 if scene != "lab-meeting" else 1
            self.assertEqual(len(headings), len(roles) + extra, scene)

    def test_each_main_page_has_placeholders(self):
        text = deck.build_outline("defense", "题目", 12)
        blocks = text.split("## ")[1:]
        for block in blocks:
            if "附录" in block or "References" in block or "参考文献" in block:
                continue
            self.assertIn("结论式标题", block)
            self.assertIn("证据", block)
            self.assertIn("讲稿备注", block)

    def test_references_page_present_except_lab_meeting(self):
        for scene in ("defense", "conference", "poster"):
            text = deck.build_outline(scene, "", 12)
            self.assertTrue("参考文献" in text or "References" in text, scene)
        lab_text = deck.build_outline("lab-meeting", "", 12)
        self.assertNotIn("参考文献", lab_text)

    def test_appendix_page_present(self):
        for scene in deck.SCENES:
            text = deck.build_outline(scene, "", 12)
            self.assertTrue(any("附录" in h for h in page_headings(text)), scene)

    def test_empty_title_placeholder(self):
        text = deck.build_outline("conference", "", 10)
        self.assertIn("待填写", text)


if __name__ == "__main__":
    unittest.main()
