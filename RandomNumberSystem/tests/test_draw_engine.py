from __future__ import annotations

import random
import unittest

from draw_engine import DrawConfig, DrawEngine, DrawError, MAX_DRAW_COUNT


class DrawConfigTests(unittest.TestCase):
    def test_pool_size_and_mode_name(self) -> None:
        config = DrawConfig(minimum=1, maximum=49, count=6, unique=True)
        self.assertEqual(config.pool_size, 49)
        self.assertEqual(config.mode_name, "不重复")

        repeat = DrawConfig(minimum=-5, maximum=5, count=3, unique=False)
        self.assertEqual(repeat.pool_size, 11)
        self.assertEqual(repeat.mode_name, "可重复")

    def test_rejects_reversed_range(self) -> None:
        with self.assertRaisesRegex(DrawError, "最小值"):
            DrawConfig(minimum=10, maximum=1, count=1).validate()

    def test_rejects_non_positive_count(self) -> None:
        with self.assertRaisesRegex(DrawError, "至少"):
            DrawConfig(minimum=1, maximum=10, count=0).validate()

    def test_rejects_too_many_numbers_without_duplicates(self) -> None:
        with self.assertRaisesRegex(DrawError, "最多只能抽取 10"):
            DrawConfig(minimum=1, maximum=10, count=11, unique=True).validate()

    def test_rejects_excessive_count(self) -> None:
        with self.assertRaisesRegex(DrawError, str(MAX_DRAW_COUNT)):
            DrawConfig(
                minimum=1,
                maximum=MAX_DRAW_COUNT + 10,
                count=MAX_DRAW_COUNT + 1,
                unique=True,
            ).validate()

    def test_allows_single_number_pool(self) -> None:
        config = DrawConfig(minimum=7, maximum=7, count=1, unique=True)
        config.validate()
        result = DrawEngine(random.Random(1)).draw(config)
        self.assertEqual(result.numbers, (7,))


class DrawEngineTests(unittest.TestCase):
    def test_unique_draw_has_no_duplicates_and_stays_in_range(self) -> None:
        config = DrawConfig(minimum=1, maximum=20, count=10, unique=True)
        result = DrawEngine(random.Random(2026)).draw(config)
        self.assertEqual(len(result.numbers), 10)
        self.assertEqual(len(set(result.numbers)), 10)
        self.assertTrue(all(1 <= number <= 20 for number in result.numbers))

    def test_repeat_draw_can_produce_duplicates(self) -> None:
        config = DrawConfig(minimum=5, maximum=5, count=4, unique=False)
        result = DrawEngine(random.Random(1)).draw(config)
        self.assertEqual(result.numbers, (5, 5, 5, 5))

    def test_seed_makes_draw_reproducible(self) -> None:
        config = DrawConfig(minimum=1, maximum=100, count=6, unique=True)
        first = DrawEngine(random.Random(42)).draw(config)
        second = DrawEngine(random.Random(42)).draw(config)
        self.assertEqual(first.numbers, second.numbers)

    def test_preview_does_not_change_history_semantics(self) -> None:
        config = DrawConfig(minimum=1, maximum=10, count=3, unique=True)
        engine = DrawEngine(random.Random(9))
        preview = engine.preview(config)
        self.assertEqual(len(preview), 3)
        self.assertEqual(len(set(preview)), 3)
        result = engine.draw(config)
        self.assertEqual(len(result.numbers), 3)

    def test_number_text(self) -> None:
        config = DrawConfig(minimum=1, maximum=10, count=3, unique=True)
        result = DrawEngine(random.Random(7)).draw(config)
        self.assertEqual(
            result.number_text,
            "  ".join(str(number) for number in result.numbers),
        )
        self.assertEqual(
            result.comma_text,
            ", ".join(str(number) for number in result.numbers),
        )


if __name__ == "__main__":
    unittest.main()
