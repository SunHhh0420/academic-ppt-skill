"""timing_budget.py 单测。"""

import unittest

from _loader import load

budget = load("timing_budget")


class TestComputeBudget(unittest.TestCase):
    def test_all_scenes_compute(self):
        for scene in budget.SCENES:
            cfg, pages, rows, mr_share = budget.compute_budget(15, scene)
            self.assertEqual(cfg, budget.SCENES[scene])
            self.assertGreaterEqual(pages, 1)
            self.assertTrue(rows)
            self.assertIsInstance(mr_share, float)

    def test_page_count_follows_coefficient(self):
        minutes = 10
        for scene, cfg in budget.SCENES.items():
            _, pages, _, _ = budget.compute_budget(minutes, scene)
            expected = round(minutes * cfg["pages_per_minute"])
            self.assertEqual(pages, expected)

    def test_section_share_sums_to_one(self):
        for scene in budget.SCENES:
            _, _, rows, _ = budget.compute_budget(15, scene)
            total = sum(share for _, share, _ in rows)
            self.assertAlmostEqual(total, 1.0, places=6)

    def test_method_result_share_above_half_for_talks(self):
        # 答辩/会议/海报以方法结果为主；组会周报不强调该闭环
        for scene in ("defense", "conference", "poster"):
            _, _, _, mr_share = budget.compute_budget(15, scene)
            self.assertGreaterEqual(mr_share, 0.50, scene)

    def test_render_contains_key_fields(self):
        text = budget.render(15, "defense")
        self.assertIn("15 分钟", text)
        self.assertIn("方法 + 结果合计占比", text)
        self.assertIn(budget.SCENES["defense"]["label"], text)

    def test_small_minutes_does_not_crash(self):
        _, pages, _, _ = budget.compute_budget(1, "conference")
        self.assertGreaterEqual(pages, 1)


if __name__ == "__main__":
    unittest.main()
