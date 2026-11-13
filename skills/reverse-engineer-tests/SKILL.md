---
name: reverse-engineer-tests
description: Reverse engineer any test or exam from its real past papers into evidence-backed patterns — SAT, ACT, AP, GRE, GMAT, LSAT, state exams, school finals, mock papers, certification and licensing exams, any multiple-choice or short-answer set. Use whenever the user wants to crack a test, decode question patterns, find recurring traps or answer-choice tells, check whether a test-taking trick really works ("is the longest answer usually right?"), learn where the marks and the hard questions are, analyze an official question bank, build practice questions like the real ones, or make a strategy cheatsheet — even if they never say "reverse engineer". Input is PDFs (scanned ones too, via OCR) or pasted text. Every claim comes with counts, cited question ids and a held-out check of what it is worth in marks. This is document and pattern analysis; it is NOT for reverse engineering software, binaries, apps or APKs.
metadata:
  version: "8"
compatibility: Needs python3 (standard library only) and pdftotext (poppler) for PDFs. Uses the `pdf` skill for OCR of scanned pages when available.
---

# Reverse Engineer Any Test (RET)

A test paper leaks its own construction. Every question is built to a
template: one tested skill, a planted trap, and wrong choices picked to catch
predictable mistakes. Recover the templates from real past papers, count
them, and check each claim against papers it was not learned from.

The skill's value is honesty. Most test-prep "tricks" fail when counted, and
a student is better served by "this trick is a myth, here are the numbers"
than by a confident rule that costs marks. Report busted myths as
prominently as real signals.

## Two rules that hold everywhere

1. **Evidence, not vibes.** A pattern is real only when seen in 2+ questions
   with cited question ids (qids). One occurrence is an anecdote. Never
   estimate a frequency; the scripts count. Keep coverage separate from
   completeness: a pattern absent from the papers analyzed is not proven
   absent from the test. `references/evidence-model.md` defines the record
   format, unknowns and the mandatory footer; read it before Phase 2.
2. **No signal without its held-out value.** A p-value says a pattern
   exists; it does not say it earns marks. Phase 5 prices every
   answer-choice signal on papers it never saw. If that gain's interval
   includes 0, say "not established".

## Pick the lane first

Run only the phases the request needs.

| The user wants | Run |
|---|---|
| "Crack this test" with whole papers | Phases 1–5, then 7–8 if asked |
| "Which topics / patterns matter" | Phases 1–3 |
| "Does trick X work" / "what makes the right answer right" | Phases 1, 4, 5 |
| "What makes questions hard" (official bank exists) | Phases 1, 6 |
| "Practice questions like these" | Phases 1–2, then 7 |
| "A cheatsheet / strategy" | Phases 1–3, then 8 |
| A few pasted questions | Phase 2 only (too few to count) |

Label question types with `references/pattern-library.md` and name traps and
fast methods with `references/analysis-method.md`.

## Phase 1 — Ingest

**Fast path: whole papers with an answer key.** One command per paper, then
one run:

```bash
python3 scripts/ret.py adapters        # sat-digital, act-enhanced, cb-qbank, regents-ela, regents-mc, generic
python3 scripts/ret.py ingest <adapter> <paper> <key> --form F1 -o f1.json
python3 scripts/ret.py validate f1.json f2.json      # fix the parse until clean
python3 scripts/ret.py run f1.json f2.json --out out/
```

`run` writes `validation.txt`, `answer_dna.txt` and `simulation.txt`. Give
each paper its own `--form`; held-out scoring needs 2+ forms, and more forms
give tighter intervals. For a test with no adapter, start with `generic`. If
`validate` shows gaps, copy `scripts/adapters/generic.py` into a
test-specific adapter and fix the parsing there. Every adapter emits one
schema (`scripts/ret_common.py`), so everything after ingest is shared.

**By hand, when no adapter fits:**

1. PDFs: extract text; OCR scanned pages; read page images for questions
   that depend on a figure. Pasted text: use as-is.
2. Separate questions, choices and the answer key. With no key, solve the
   questions yourself and mark those answers `derived`.
3. If a page stays unreadable after OCR and a direct look at the image, log
   an unknown and move on. Never invent a question you could not read.

**Checks that apply either way.** Each of these has silently corrupted a
real analysis, so do not skip them:

- **Verify the key.** Key tables often sit beside score-conversion tables,
  and a careless parser reads conversion numbers as answers. If the key
  prints totals per category, your counts must match. If choice letters
  alternate by question (ACT: A–D odd, F–J even), every key letter must
  exist among that question's choices.
- **Never trust extraction order.** Two-column pages scramble questions.
  Pair items with a key or explanations using `scripts/match_items.py` and
  hand-check every qid it reports as unconfirmed.
- **Validate before any statistics.** Clear or explain every
  `answer-missing`, `choices`, `letter-set` and `swallowed` flag.
  "Swallowed" means page text was glued onto a choice; it once made 41 ACT
  choices look longest and distorted every length result.
- **Spot-check alignment.** Pick questions answerable from the stem alone
  (vocabulary, simple arithmetic) and confirm the keyed answer is right. A
  misaligned key produces a convincing "no pattern" result.
- Use the maker's own categories as skill labels when the key prints them.
  Keep unscored field-test questions; they still show how the test is built.

Report: number of questions, sections, and anything unreadable.

## Phase 2 — One record per question

For each question write one record (schema in
`references/evidence-model.md`): `qid, section, skill, difficulty,
archetype, trap, answer, answer_source, fast_method, notes`. Solve the long
way to be sure, then record the fastest reliable route. Save all records to
one JSON file.

## Phase 3 — Pattern report

Count with the script, never by hand:

```bash
python3 scripts/tally.py records.json --md
```

It gives the skill distribution, archetype frequency, trap catalog, and
difficulty and section splits, each with the qids behind the count, and
flags single occurrences. Then interpret: where the marks are, which
archetypes are fast points and which are time sinks, and a sensible question
order.

## Phase 4 — Answer DNA: does the trick work?

Test what correct answers have in common, per question type, against the
real choices. Read `references/answer-dna.md` first; it lists the pitfalls
(ties, placeholder choices, empty passages) and results from earlier exams
to compare against.

```bash
python3 scripts/answer_dna.py items.json      # ret.py run does this too
```

It tests choice length, copying of passage words, echo of the question,
numeric value, extreme words (always, never, only), hedge words (may, some)
and answer-letter balance, with exact p-values. Call p ≤ 0.01 strong,
0.01–0.05 tentative, and state how many checks ran, because about 1 in 20
crosses 0.05 by luck. Needs full question text and 15+ questions per type;
pool as many papers as exist.

Then mine what statistics cannot reach, by counting stems and correct
choices: the relationship each transition question tests, the goal each
"which choice accomplishes…" question names, the rule each grammar question
tests.

Do not carry a verdict from one test family to another. Extreme words
predict nothing on the SAT, ACT and reading tests, yet mark wrong answers on
New York Regents history and science exams. Test each family.

## Phase 5 — What a signal is worth

```bash
python3 scripts/simulate_score.py items.json  # ret.py run does this too
```

It learns rules on some forms and scores them on forms they never saw, for a
blind guess and for a guess between two remaining choices. It prints the
gain with a 95% interval and the extra questions right per form.

- Report every answer-choice signal with its held-out gain, or not at all.
- State the gain in marks for a realistic student, who guesses on a minority
  of questions. Every exam analyzed so far came out under one question per
  test. Say that plainly; do not oversell.
- If the simulation and the p-values disagree, trust the simulation and look
  for a counting error. That disagreement is how a tie-counting bug was
  found.

## Phase 6 — Official question banks and difficulty

Some makers publish a bank with their own labels (College Board's SAT
Question Bank: about 3,800 questions, each with a skill and an
easy/medium/hard rating). When one exists it beats practice papers.

1. **Check your labels against it.** Run your Phase 2 classifier on bank
   questions and report agreement with the official skills. Tune on one half
   and report accuracy on the other.
2. **Find where the hard questions are and what makes them hard:**
   ```bash
   python3 scripts/difficulty_drivers.py bank_items.json
   ```
   Use official difficulty labels only, never your own guesses.
3. **Re-check strategy advice against difficulty.** "Rule-based questions
   are fast marks" was wrong for SAT punctuation, which College Board rates
   hard 46% of the time. Signals can also depend on difficulty; split by it.

Fetch politely: one request at a time with a pause, resumable, TLS
certificate checks left on.

## Phase 7 — Practice questions (on request)

Clone the recovered archetypes, aimed at the user's weak skills and traps.
Each item: question, choices with wrong answers built on the real trap
tactics, the answer, and the archetype it drills. Match the source's
difficulty. Write new questions; do not reproduce the originals.

## Phase 8 — Cheatsheet (on request)

One page a student rereads the morning of the test: the 3–6 tactics with the
most leverage, the traps to expect, the fast method per archetype, and a
timing and order plan. Include only signals that passed Phase 5, each with
its numbers.

## Output shapes

**Per-question row:**
```
Q{n} [{section} · {difficulty}] skill: {skill} | archetype: {archetype}
  trap: {trap} — {what the wrong choices reward}
  fast: {fastest reliable method}
  answer: {choice} ({official|derived}) — {one-line why}
```

Example. Input: `17. If 3x + 6 = 18, what is the value of x + 2?  A) 4  B) 6  C) 8  D) 12`
```
Q17 [Math · easy] skill: linear-solve-for | archetype: linear-solve-for
  trap: right-answer-wrong-question — A(4)=x and D(12)=3x punish not reading "x+2"
  fast: 3x+6=18 is 3(x+2)=18, so x+2=6; divide, don't solve for x first
  answer: B (derived) — x+2 = 6
```

**Signal row (Phases 4–5):**
```
{question type}: {signal} — {k} of {n} ({pct}%; chance {c}%), {strong|tentative|no signal}
  held-out: {gain} pts blind, {gain} pts two-left (±{ci}) | {established|not established}
```

**Footer, on every analysis:**
```
Coverage: {N analyzed} / {M skipped} ({reasons}).
Answers: {X official} / {Y derived}.
Checks run: {n}; expect about {n/20} below p = 0.05 by luck.
Open unknowns: {...}.
```

## Integrity

This skill studies past, released and practice papers. Do not use it to get
answers to a live, in-progress or embargoed exam. If a request looks like
live-exam help, decline and offer practice-paper analysis. Released papers
belong to their publishers: analyze them, quote sparingly, and never
redistribute question text.

## Files

- `references/evidence-model.md` — record format, coverage, unknowns, footer. Read before Phase 2.
- `references/analysis-method.md` — per-question rubric, trap names, fast methods.
- `references/pattern-library.md` — question archetypes by subject, plus what earlier runs found on the SAT, ACT and NY Regents.
- `references/answer-dna.md` — Phase 4 method, pitfalls, and results from four exam families. Read before Phase 4.
- `scripts/ret.py` — `adapters`, `ingest`, `validate`, `run`.
- `scripts/adapters/` — per-exam parsers; copy `generic.py` for a new exam.
- `scripts/ret_common.py` — the shared item schema.
- `scripts/validate_items.py` — parsing-damage checks.
- `scripts/match_items.py` — pairs questions with key or explanations by content.
- `scripts/blocks.py` — question-type labels from stems (SAT Reading & Writing, ACT English).
- `scripts/tally.py` — counts with qid citations (Phase 3).
- `scripts/answer_dna.py` — signal tests (Phase 4).
- `scripts/simulate_score.py` — held-out value of each signal (Phase 5).
- `scripts/difficulty_drivers.py` — where hard questions are and why (Phase 6).
