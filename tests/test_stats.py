"""Unit tests for the statistics. Each guards a bug that has happened or a
claim the README makes.

  python3 -m unittest discover tests
"""
import os
import random
import sys
import unittest
from math import comb

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                "skills", "reverse-engineer-tests", "scripts"))

from answer_dna import binom_tail, choice_length, feature_scores, rank_counts  # noqa: E402
from report import build  # noqa: E402
from ret_common import make_item  # noqa: E402
from simulate_score import ci, simulate  # noqa: E402
from validate_items import validate  # noqa: E402


def item(n, choices, answer, form="F1", **kw):
    return make_item(qid=f"{form}-Q{n}", exam="T", form=form, section="S", q=n,
                     block="all", stem="Which is correct?", choices=choices,
                     answer=answer, **kw)


def exam(p_longest, forms=4, per_form=40, seed=1):
    """Synthetic forms where the longest choice is right with probability
    p_longest, otherwise the answer is random."""
    rng, out = random.Random(seed), []
    for f in range(forms):
        for q in range(1, per_form + 1):
            lens = rng.sample(range(3, 30), 4)
            ch = {l: "x" * n for l, n in zip("ABCD", lens)}
            longest = max(ch, key=lambda k: len(ch[k]))
            ans = longest if rng.random() < p_longest else rng.choice("ABCD")
            out.append(item(q, ch, ans, form=f"F{f}"))
    return out


class BinomTail(unittest.TestCase):
    def test_matches_exact_sum(self):
        n, p = 20, 0.25
        exact = lambda ks: sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in ks)
        self.assertAlmostEqual(binom_tail(3, n, p), exact(range(3, n + 1)), places=10)
        self.assertAlmostEqual(binom_tail(3, n, p, upper=False), exact(range(0, 4)), places=10)

    def test_large_n_does_not_overflow(self):
        p = binom_tail(1300, 5000, 0.25)
        self.assertTrue(0 <= p <= 1)


class Ties(unittest.TestCase):
    """Tied questions are left out, not counted as misses. Counting them made
    every 'the X choice is rarely right' figure look stronger than it was."""

    def test_tied_extreme_is_not_eligible(self):
        its = [item(q, {"A": "aaaa", "B": "bbbb", "C": "c", "D": "dd"}, "A")
               for q in range(10)]
        counts = rank_counts(its, choice_length)
        self.assertEqual(counts[True][:2], (0, 0))    # A and B tie for longest
        self.assertEqual(counts[False][:2], (0, 10))  # C is uniquely shortest, never right

    def test_unique_extreme_is_counted(self):
        its = [item(q, {"A": "aaaaa", "B": "bbb", "C": "c", "D": "dd"}, "A")
               for q in range(10)]
        self.assertEqual(rank_counts(its, choice_length)[True][:2], (10, 10))


class Placeholders(unittest.TestCase):
    def test_no_change_has_no_length(self):
        it = item(1, {"A": "NO CHANGE", "B": "walks", "C": "walk quickly", "D": "walking"}, "B")
        scores = feature_scores(it, choice_length)
        self.assertNotIn("A", scores)
        self.assertEqual(set(scores), {"B", "C", "D"})


class Simulation(unittest.TestCase):
    def test_planted_flaw_is_found_and_priced(self):
        _, _, _, res = simulate(exam(0.55))
        rs = [r for v in res.values() for r in v]
        mean, half = ci([r[1] for r in rs])
        self.assertGreater(mean - half, 0.2)

    def test_fair_exam_yields_no_rule(self):
        _, _, _, res = simulate(exam(0.0, seed=3))
        self.assertFalse(any(r[0] for v in res.values() for r in v))


class Validation(unittest.TestCase):
    def test_glued_text_is_flagged_swallowed(self):
        its = [item(q, {"A": "one", "B": "two", "C": "three", "D": "four"}, "A")
               for q in range(1, 6)]
        its.append(item(6, {"A": "one", "B": "two", "C": "three",
                            "D": "four " + "passage text glued on " * 10}, "A"))
        _, flags = validate(its)
        self.assertEqual(flags["swallowed"], ["F1-Q6"])


class Report(unittest.TestCase):
    def test_planted_flaw_reported_as_rule(self):
        text = build(exam(0.55))
        self.assertIn("**Above chance** (strong)", text)
        self.assertIn("**Favour** the longest choice", text)
        self.assertIn("Coverage: 160 analyzed / 0 skipped", text)

    def test_fair_exam_reported_as_nothing(self):
        text = build(exam(0.0, seed=3))
        self.assertIn("Gain: 0", text)
        self.assertIn("No rule to use.", text)


if __name__ == "__main__":
    unittest.main()
