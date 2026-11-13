# Answer DNA: testing what correct answers have in common

Phase 3 maps *where* questions sit and *which traps* recur. Answer DNA goes one
level deeper: it treats every test-prep "trick" as a hypothesis and checks it
against the actual answer choices. It's REA's verify-don't-assume rule applied
to the answer options themselves.

## When to run it

- The user wants "deeper", "the essence", "what makes the right answer right",
  or asks whether a trick works ("is the longest answer usually right?").
- You have **full item text**: passage, question, every choice, plus the
  official key. Explanations alone are not enough.
- You have enough items per question type: 15+ per block for anything worth
  saying, 30+ to be confident. One test is usually too few; pool 2–3 tests.

## Pipeline

1. **Parse items** from the paper: passage, stem, choices A–D per question.
2. **Align items to the key.** Run `scripts/match_items.py`. Do NOT trust
   extraction order: two-column PDF pages scramble it (in one SAT test, 39 of
   66 items came out of order). The script matches by content and confirms each
   pair by finding the key letter's choice text in that question's explanation.
   Hand-check every qid it lists as unconfirmed before trusting results.
3. **Label blocks** (question types) from the Phase-2 records via
   `--records`, or set `block` yourself. Coarse blocks (5–6 types) beat fine
   archetypes here because tests need sample size.
4. **Run** `scripts/answer_dna.py matched.json`, then
   `scripts/simulate_score.py matched.json` (or `ret.py run`, which does both
   after validating).
5. **Mine content** per block where the stats can't reach: what relationship a
   transition question tests, what goal a synthesis question names, which
   grammar rule is tested. Count these from the stems and correct choices.

## Hypotheses the script tests

Per block, against chance = 1 / number of choices:

| Hypothesis | Common claim it tests |
|---|---|
| correct is the longest / shortest choice | "longest answer is right" |
| correct has the most / fewest passage words | "pick the one that uses the passage's words" |
| correct overlaps most / least with the question | "the answer echoes the question" |
| extreme words in correct vs wrong | "avoid always/never/only" |
| hedge words in correct vs wrong | "pick the hedged answer" |
| answer-letter distribution | "when in doubt pick C" |

## Reading the results

- **p_low small on "correct is uniquely X"** means X is an *elimination*
  signal: cross out the X choice. Example: "notes synthesis: correct is
  uniquely shortest 0/21, p_low = 0.002" means the shortest choice is never
  right.
- **p_high small** is a *pick* signal. These are rare on professional tests.
- **Multiple comparisons:** the script prints how many checks ran. With 20
  checks, about 1 crosses p < 0.05 by luck. Call p <= 0.01 strong,
  0.01–0.05 tentative, above 0.05 no signal. Say which in the report.
- **A non-result is a result.** "Extreme words: correct 5% vs wrong 6%" busts
  a myth. Report busted myths prominently; they save students from bad habits.

## Pitfalls (each one has happened)

- **Uninformative items inflate signals.** If an item's passage text is empty
  (graph, quotation, or parse failure), every choice scores 0 on passage
  overlap. Counting those items makes "correct is lowest" look rarer than it is.
  `answer_dna.py` skips items whose choices all score the same; hand-rolled
  analysis must do the same. (A first SAT analysis reported p = 0.006 for a
  signal that was really p = 0.08 because of this.)
- **Ties are not hits, and tied questions are not misses either.** Count a
  question for "uniquely longest" only when one choice IS uniquely longest.
  Counting tied questions in the denominator against a 1-in-4 chance makes
  every extreme look rare. This produced two fake "universal" signals on the
  SAT and ACT ("the choice sharing the fewest words with the question is
  never right", really 9/27; "math answers are rarely the longest or
  shortest", really 21–23%). `answer_dna.py` now does this correctly.
- **Glued-on choice text fakes length signals.** If the page prints passage
  text beside the questions, the last choice can swallow it. Run
  `validate_items.py` and clear every "swallowed" flag first.
- **Placeholder choices have no length.** "No Change" stands for text printed
  elsewhere. `answer_dna.py` leaves such choices out of length comparisons.
- **An in-sample p-value is not a result.** Always run `simulate_score.py`
  and report each signal with its held-out value. A signal that earns nothing
  on unseen forms is not reported as usable, whatever its p-value.
- **Order-based alignment silently corrupts everything.** Always run the
  matcher and hand-check the unconfirmed list.
- **Word lists are choices, not facts.** The extreme/hedge lists are
  heuristics; say so, and don't over-read small differences.
- **Professional tests are built to neutralize tells.** Expect most surface
  hypotheses to fail on College Board / ETS tests. Teacher-made tests often
  leak far more (longest-answer and "all of the above" biases are common).

## Worked prior: SAT (8 practice tests + the official Question Bank)

All figures use the corrected tie handling. Held-out gain is guess accuracy
over even guessing, two choices left, from `simulate_score.py`.

| Signal (Question Bank, 1,845 RW items) | Count | Held-out gain |
|---|---|---|
| Verb/agreement: shortest right, longest not | 48% (84/174), 7% (10/153) | +18 pts |
| Notes synthesis: longest right, shortest not | 37% (73/198), 14% (28/195) | +12 pts |
| Notes synthesis: fewest words shared with the goal | 7% (6/83) | (in the +12) |
| Evidence questions: shortest rarely right | 14% (35/250) | +7 pts |
| Transitions: shortest often right | 36% (59/166) | +4 pts |
| Hard reading items: longest rarely right | 18% (54/295); easy 31% | not scored |
| Every other RW skill, and all of Math | chance | 0 |

Busted: extreme words, hedges, letter bias, math longest/shortest, "fewest
words shared with the question" outside synthesis. Content findings (not
affected by ties): transition distractors almost never share the correct
relationship (164/168); "no punctuation" is the most common correct answer on
punctuation questions (24/69). **Tells can depend on difficulty**: split by
difficulty whenever official labels exist. **Overall worth:** +4.6 points of
guess accuracy across RW, under one question per test for a typical student.

## Second test: ACT (4 official forms, 684 items) — what's universal

Two patterns hold on both tests: **grammar's shortest choice is often right
and its longest rarely** (ACT 44% and 7%; with concision questions, shortest
48%), and **"do this goal" writing questions favour fuller choices** (ACT
shortest right 11%, tentative). Extreme words predict nothing on either.
Reading, Science and Math show no answer-choice signal on the ACT. With only
4 forms no ACT signal could be confirmed held-out. Treat the two patterns as
**priors for any professionally built test with grammar or rhetoric items**,
still to be verified per test. Test-specific folklore should be tested too:
"NO CHANGE" was right exactly 25% (no bias) and "Delete the underlined
portion" was right 2/10.

## Third test: NY Regents ELA (33 forms, 792 reading items)

No signal of any kind, and a held-out gain of exactly 0 across 33 forms.
Across three independent test makers, **reading-comprehension items give no
answer-choice shortcut**; expect that as the default. The shortcuts that do
exist sit in grammar and "achieve this goal" writing items. Before trusting
a null, confirm the key is aligned (spot-check items you can answer from the
stem alone, such as vocabulary): a misaligned key also produces a null.

## Fourth test: Regents content exams (100 forms, 4,424 items)

The opposite of the reading result. On US History and Living Environment the
classic tips hold and survive held-out scoring: only-choice-with-an-extreme-
word right 8–9%, only-hedged-choice right about 50%, longest right 28–33%.
So "extreme words are a myth" is true of SAT, ACT and reading tests, not of
tests in general. `answer_dna.py` now tests the word features per item
("the only choice with such a word"), which is far more sensitive than the
pooled correct-vs-wrong rate and feeds the simulation.

**Mid-line cuts are invisible to the validator.** Reading a two-column page
in halves cuts full-width questions mid-line; the pieces look like normal
short choices. Compare each parsed line with the same line in a full-page
extraction (see `adapters/regents_ela.py: mark_truncated`). 8 of 792 Regents
English items and 918 of about 5,100 content-exam items were affected.

**Group letters by letter set.** Some tests alternate choice letters (ACT:
A–D on odd questions, F–J on even). `answer_dna.py` tests each letter set
separately with an exact chi-square p-value. Pooling sets hid a real ACT math
quirk (J right 40% on even questions, p = 0.006, consistent across all 4
forms), which a pooled test with the wrong degrees of freedom missed.

**Lesson on sample size:** with 3 tests, "notes synthesis: shortest never
right" looked strong (0/21, p = 0.002). With 8 tests it fell to tentative
(8/57, p = 0.03). Pool as many tests as exist before calling anything a rule,
and re-run when more data arrives. Use this prior to check, not to copy.
