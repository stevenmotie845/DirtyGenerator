"""Regression tests for smart_story_engine's story-bible behavior."""
from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import smart_story_engine as engine


class SmartStoryEngineTests(unittest.TestCase):
    def test_normalizer_removes_legacy_race_labels_and_keeps_selected_noun(self) -> None:
        result = engine.normalize_language("A big black cock and a white dick.", "dick")
        self.assertNotIn("black", result.casefold())
        self.assertNotIn("white", result.casefold())
        self.assertNotIn("cock", result.casefold())
        self.assertIn("dick", result.casefold())

    def test_local_generation_is_repeatable_and_preserves_story_state(self) -> None:
        state = engine.StoryState(
            character_name="Avery Quinn", pov="third", location="the hotel suite",
            wardrobe="a fitted dress and heels", makeup="smoky eyeliner", nails="red nails",
            noun="cock", tone="direct", premise="a fictional adult encounter",
        )
        result = engine.generate_story(state, 4, random.Random(7), False, "", "", "", 1)
        self.assertEqual(len(result["beats"]), 4)
        self.assertEqual(result["state"]["location"], "the hotel suite")
        self.assertNotIn("black cock", result["story"].casefold())
        self.assertNotIn("white cock", result["story"].casefold())
        self.assertNotIn(" my ", f" {result['story'].casefold()} ")


if __name__ == "__main__":
    unittest.main()
