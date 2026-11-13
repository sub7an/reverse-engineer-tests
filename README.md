# reverse-engineer-tests

**Do test-taking tricks actually work? This skill counts.**

An agent skill that reverse engineers any exam from its real past papers:
what each question type tests, which traps repeat, where the hard questions
are, and whether "pick the longest answer" or "avoid *always* and *never*"
earns a single mark. Every claim comes with counts, question ids, and a
check on papers it was not learned from.

Works with Claude Code and any agent that reads `SKILL.md` skills.

```
> Crack these six past papers. Does "the longest answer is usually right" hold?

US History: longest choice is right — 440 of 1,353 (33%; chance 25%), strong
  held-out: +7.3 pts blind, +6.0 pts two-left (±1.8) | established
Global History: longest choice is right — 26%, no signal
  held-out: under +1 pt | not established
```

## What it found so far

Run on 145 official exams and one official question bank, about 10,000
questions in total.

| Claim | SAT | ACT | NY Regents English | NY Regents History & Science |
|---|---|---|---|---|
| "Avoid *always*, *never*, *only*" | Myth | Myth | Myth | **True**: right 8% of the time (chance 25%) |
| "Pick the hedged answer (*may*, *some*)" | Myth | Myth | Myth | **True**: right 49–64% |
| "The longest answer is right" | Only on notes-synthesis questions (37%) | No | No | US History 33%, Living Environment 28% |
| "In grammar, shortest is best" | **True**: shortest right 48%, longest 7% | **True**: 44% and 7% | not tested | not tested |
| "When in doubt, pick C" | Myth | Myth (one quirk: J is right 40% on even-numbered Math) | Myth | Myth |
| "The odd one out is wrong" (the answer looks like the other choices) | **True** on reading: most-similar choice right 34–43%, odd one out 11–18% | **True** on Reading (37%) | Weak (30%) | Weak (28–29%) |
| "The key is balanced, so count your letters" | **False**: counting loses marks | Fewer repeats than chance; balance tentative | **True** | **True**: US History uses every position almost equally |

**And what it is worth:** answer-choice tricks earn 0.4 to 1 extra question
per paper, on every test analyzed. They are tie-breakers for a guess, not a
way to score. One exception so far: on Regents US History the answer key is
so evenly balanced that counting your confident answers and filling the
under-used position is worth about 1.4 questions per exam. The larger gains
are in the other output: which skills are rated hard, what each question
type really asks, and what makes hard questions hard.

Full write-ups, including three published corrections of the project's own
earlier claims, are in [`docs/findings/`](docs/findings/).

## Why this is different

- **It counts.** No frequency is estimated. Scripts tally every pattern and
  cite the questions behind it.
- **It prices every signal.** Rules are learned on some papers and scored on
  papers they never saw. A pattern with a good p-value and no held-out gain
  is reported as "not established".
- **It reports myths as loudly as hits.** Most folklore fails. Knowing that
  saves students from habits that cost marks.
- **It checks its own parsing.** A validator catches the PDF-extraction
  damage (scrambled columns, text glued onto choices, misread keys) that
  quietly fakes results.

## Install

**Claude Code plugin:**

```
/plugin marketplace add sub7an/reverse-engineer-tests
/plugin install reverse-engineer-tests@reverse-engineer-tests
```

**Or copy the skill folder:**

```bash
git clone https://github.com/sub7an/reverse-engineer-tests
cp -r reverse-engineer-tests/skills/reverse-engineer-tests ~/.claude/skills/
```

Needs `python3` (standard library only) and `pdftotext` for PDFs
(`brew install poppler` or `apt install poppler-utils`).

## Use

Give your agent past papers and ask:

- "Crack these past papers. Where are the marks and what are the traps?"
- "Is it true the longest answer is usually right on this exam?"
- "Which skills are hardest in this question bank, and why?"
- "Make me 10 practice questions like the hard ones here."
- "Give me a one-page cheatsheet for this exam."

## Try it in 30 seconds, no exam needed

The demo builds a synthetic exam (invented words, four forms) with one flaw
planted on purpose, then finds it and prices it.

```bash
python3 examples/make_demo.py examples/demo
S=skills/reverse-engineer-tests/scripts
for i in 1 2 3 4; do
  python3 $S/ret.py ingest generic examples/demo/form$i.txt examples/demo/key$i.txt --form D$i -o /tmp/d$i.json
done
python3 $S/ret.py run /tmp/d1.json /tmp/d2.json /tmp/d3.json /tmp/d4.json --out /tmp/demo-out
cat /tmp/demo-out/report.md
```

```
| Trick               | Right            | Chance | Verdict                  |
| The longest choice  | 114 of 160 (71%) | 25%    | **Above chance** (strong) |
| The shortest choice | 15 of 160 (9%)   | 25%    | **Below chance** (strong) |

| Question type | Rule applies | Blind guess | Two choices left | Established |
| All questions | 100%         | +46.2 ±7.0  | +30.9 ±5.1       | yes         |

- **Favour** the longest choice: it was right 114 of 160 times (71%).
- **Cross out** the shortest choice: it was right 15 of 160 times (9%).
```

A real, professionally built exam gives a much smaller number. That is the
point of measuring.

## How it works

| Phase | What happens | Script |
|---|---|---|
| 1. Ingest | Paper + key become one item schema; parsing damage is flagged | `ret.py ingest`, `validate` |
| 2. Records | One record per question: skill, trap, fastest method | — |
| 3. Patterns | Counted skill, archetype and trap frequencies, with question ids | `tally.py` |
| 4. Answer DNA | Tests length, word-copying, extreme and hedge words, convergence, letter balance | `answer_dna.py` |
| 4b. Key structure | Tests whether the answer key is balanced or avoids repeats, and prices counting strategies | `key_structure.py` |
| 5. Worth | Held-out gain per signal, in guess accuracy and questions per exam | `simulate_score.py` |
| Report | One readable Markdown report: verdicts, worth, rulebook, coverage | `report.py` |
| 6. Difficulty | Where officially-hard questions are, and what makes them hard | `difficulty_drivers.py` |
| 7–8. Output | Practice questions built on the real traps; a one-page cheatsheet | — |

**Adapters included:** `sat-digital`, `act-enhanced`, `cb-qbank` (College
Board Question Bank), `regents-ela`, `regents-mc`, and `generic` for any
plainly formatted paper. A new exam costs one adapter; see
[CONTRIBUTING.md](CONTRIBUTING.md).

## Limits

- Signals apply only to questions a student would otherwise guess. They do
  not replace knowing the material.
- Results are per exam family. A verdict on the SAT says nothing about a
  state history exam, and the table above shows why.
- Held-out checks need several forms. With 4 ACT forms, no ACT signal could
  be confirmed out of sample.
- Scanned or figure-heavy papers need OCR and lose some questions; the
  coverage footer on every report says how many.

## Integrity and legal

This skill studies **past, released and practice papers**. It refuses to
help with a live or embargoed exam.

The repository contains no exam content: no papers, no question text.
Bring your own legally obtained papers. Published findings are aggregate
statistics.

SAT® is a trademark of College Board. ACT® is a trademark of ACT, Inc.
Regents Examinations are published by the New York State Education
Department. This project is not affiliated with, endorsed by, or sponsored
by any of them.

## License

MIT. See [LICENSE](LICENSE).
