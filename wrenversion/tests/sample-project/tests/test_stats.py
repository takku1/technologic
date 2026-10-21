import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from textstats import average_word_length, word_count


class StatsTest(unittest.TestCase):
    def test_word_count(self):
        self.assertEqual(word_count("a bb ccc"), 3)

    def test_average_word_length(self):
        self.assertEqual(average_word_length("a bb ccc"), 2.0)


if __name__ == "__main__":
    unittest.main()
