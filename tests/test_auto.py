"""The `auto` adapter must read the same 12 questions out of many layouts.

  python3 -m unittest discover tests
"""
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                "skills", "reverse-engineer-tests", "scripts"))

from adapters import ADAPTERS  # noqa: E402
from ret_common import to_text  # noqa: E402

N = 12
STEMS = [f"Which statement about topic {i} is correct?" for i in range(1, N + 1)]
TEXTS = [[f"option {i} alpha", f"option {i} beta longer text", f"option {i} gamma",
          f"option {i} delta words here", f"option {i} epsilon"] for i in range(1, N + 1)]
ANS = [(i * 7) % 4 for i in range(N)]  # correct position per question


def paper(q=lambda n: f"{n}.", c=lambda l: f"{l}.", labels="ABCD", inline=False,
          answer_line=None, before_q=None, numbers=None):
    out = ["Sample Examination", "Directions: choose the best answer.", ""]
    for i in range(N):
        n = (numbers or list(range(1, N + 1)))[i]
        if before_q:
            out += before_q(i)
        out.append(f"{q(n)} {STEMS[i]}")
        ch = [f"{c(l)} {TEXTS[i][k]}" for k, l in enumerate(labels)]
        out += ["    ".join(ch)] if inline else ch
        if answer_line:
            out.append(answer_line(labels[ANS[i]]))
        out.append("")
    return "\n".join(out)


def key(fmt=lambda n, a: f"{n} {a}", labels="ABCD", numbers=None):
    nums = numbers or list(range(1, N + 1))
    return "\n".join(fmt(n, labels[ANS[i]]) for i, n in enumerate(nums)) + "\n"


class Auto(unittest.TestCase):
    def run_auto(self, paper_text, key_text=None, suffix=".txt"):
        d = tempfile.mkdtemp()
        paths = []
        for name, text in (("paper", paper_text), ("key", key_text)):
            if text is None:
                continue
            p = os.path.join(d, name + suffix)
            open(p, "w", encoding="utf-8").write(text)
            paths.append(p)
        opts = {"exam": "Demo"}
        return ADAPTERS["auto"].parse(paths, "F1", opts), opts["log"]

    def check(self, items, labels="ABCD", n=N):
        self.assertEqual(len(items), n)
        for i, it in enumerate(items[:N]):
            self.assertEqual(list(it["choices"]), list(labels), it["qid"])
            self.assertEqual(it["answer"], labels[ANS[i % N]], it["qid"])
            self.assertEqual(it["choices"][labels[1]], TEXTS[i % N][1], it["qid"])
            self.assertIn(f"topic {i % N + 1} ", it["stem"])

    def test_plain_numbered(self):
        self.check(self.run_auto(paper(), key())[0])

    def test_question_word_and_parenthesised_choices(self):
        items, _ = self.run_auto(paper(q=lambda n: f"Question {n}:", c=lambda l: f"({l})"),
                                 key(lambda n, a: f"{n}. {a}"))
        self.check(items)

    def test_choices_on_one_line_and_key_as_two_rows(self):
        rows = (" ".join(str(n) for n in range(1, N + 1)) + "\n"
                + " ".join("ABCD"[a] for a in ANS) + "\n")
        items, _ = self.run_auto(paper(q=lambda n: f"{n})", c=lambda l: f"{l})", inline=True), rows)
        self.check(items)

    def test_lowercase_choices_with_answer_lines_and_no_key_file(self):
        items, _ = self.run_auto(paper(q=lambda n: f"Q{n}.", c=lambda l: f"{l.lower()})",
                                       answer_line=lambda a: f"Answer: {a.lower()}\n"
                                       "Explanation: because the others are wrong."))
        self.check(items)

    def test_answer_key_section_inside_the_paper(self):
        items, _ = self.run_auto(paper() + "\nANSWER KEY\n" + key(lambda n, a: f"{n}-{a}"))
        self.check(items)

    def test_numbered_choices_with_a_numeric_key(self):
        items, _ = self.run_auto(paper(c=lambda l: f"({l})", labels="1234"), key(labels="1234"))
        self.check(items, labels="1234")

    def test_five_choices(self):
        items, _ = self.run_auto(paper(labels="ABCDE"), key(labels="ABCDE"))
        self.check(items, labels="ABCDE")

    def test_roman_statement_lists_are_not_choices(self):
        romans = lambda i: []
        text = paper().replace(
            STEMS[2], STEMS[2] + "\nI. first statement\nII. second statement\nIII. third one")
        items, _ = self.run_auto(text, key())
        self.check(items)
        self.assertIn("II. second statement", items[2]["stem"])
        del romans

    def test_two_sections_restart_numbering(self):
        text = paper() + "\nSECTION 2\n\n" + paper()
        items, _ = self.run_auto(text, key() + "\n" + key())
        self.assertEqual({i["section"] for i in items}, {"S1", "S2"})
        self.check(items, n=2 * N)

    def test_key_as_a_bare_run_of_letters(self):
        items, _ = self.run_auto(paper(), " ".join("ABCD"[a] for a in ANS))
        self.check(items)

    def test_passage_before_questions_is_kept_as_passage(self):
        text = paper(before_q=lambda i: ["The river rose quickly that spring.", ""] if i == 0 else [])
        items, _ = self.run_auto(text, key())
        self.check(items)
        self.assertIn("river rose", items[0]["passage"])

    def test_docx(self):
        d = tempfile.mkdtemp()
        body = "".join(f"<w:p><w:r><w:t>{line}</w:t></w:r></w:p>"
                       for line in paper().replace("&", "&amp;").split("\n"))
        p = os.path.join(d, "paper.docx")
        with zipfile.ZipFile(p, "w") as z:
            z.writestr("word/document.xml",
                       '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.'
                       f'org/wordprocessingml/2006/main"><w:body>{body}</w:body></w:document>')
        self.assertIn("1. Which statement about topic 1", to_text(p))
        k = os.path.join(d, "key.txt")
        open(k, "w").write(key())
        self.check(ADAPTERS["auto"].parse([p, k], "F1", {"exam": "Demo"}))

    def test_nothing_found_says_so(self):
        items, log = self.run_auto("This file has no questions in it at all.\n")
        self.assertEqual(items, [])
        self.assertIn("no questions found", log[0])


if __name__ == "__main__":
    unittest.main()
