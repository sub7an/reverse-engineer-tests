#!/usr/bin/env python3
"""Generate a synthetic exam for the demo: 4 forms x 40 questions, with keys.

Every word is invented, so the demo ships no real test content. One flaw is
planted on purpose: the correct answer is the longest choice about 55% of the
time (chance is 25%). The pipeline should find it and price it on held-out
forms.

  python3 examples/make_demo.py examples/demo
"""
import os
import random
import sys

WORDS = ("tavin morl quenta bispar dolven ushra kelmit prova zanth ireld "
         "fosk merrin tulba vexor cando plith arvem sorda nibel grathe").split()
TOPICS = ("the tavin cycle", "a morl reaction", "the quenta treaty",
          "bispar growth", "the dolven index", "an ushra cell")


def phrase(rng, n):
    return " ".join(rng.choice(WORDS) for _ in range(n))


def question(rng):
    lengths = rng.sample(range(2, 9), 4)
    choices = [phrase(rng, n) for n in lengths]
    longest = max(range(4), key=lambda i: len(choices[i]))
    answer = longest if rng.random() < 0.55 else rng.randrange(4)
    return f"Which statement about {rng.choice(TOPICS)} is correct?", choices, answer


def main(out):
    os.makedirs(out, exist_ok=True)
    rng = random.Random(7)
    for form in range(1, 5):
        paper, key = [], []
        for q in range(1, 41):
            stem, choices, answer = question(rng)
            paper.append(f"{q}. {stem}")
            paper += [f"{'ABCD'[i]}. {c}" for i, c in enumerate(choices)]
            paper.append("")
            key.append(f"{q} {'ABCD'[answer]}")
        open(os.path.join(out, f"form{form}.txt"), "w").write("\n".join(paper))
        open(os.path.join(out, f"key{form}.txt"), "w").write("\n".join(key) + "\n")
    print(f"wrote 4 forms and 4 keys to {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "examples/demo")
