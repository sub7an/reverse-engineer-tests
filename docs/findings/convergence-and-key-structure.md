# Two signals nobody checks: convergence and answer-key structure

Version 8.2 added two tests that standard test-prep advice does not cover,
and ran them on every exam analyzed so far (about 10,000 questions). Both
found real effects. One of them **withdraws an earlier conclusion of this
project**: that reading questions offer no answer-choice shortcut.

---

## 1. Convergence: the right answer looks like the wrong ones

**Idea.** A question writer usually starts from the right answer and builds
each wrong choice by changing one part of it. That leaves the right answer
the choice most similar to the rest, and leaves the "odd one out" wrong.

**Measure.** For each choice, the average overlap of its three-letter
sequences with each other choice. A question counts only when one choice is
clearly the most similar (or the least).

| Exam and question type | Most like the others is right | Odd one out is right |
|---|---|---|
| SAT bank: central ideas and details | **39%** (52 of 135) | **11%** (15 of 137) |
| SAT bank: cross-text connections | **43%** (26 of 61) | 23%, no signal |
| SAT bank: notes synthesis | **39%** (79 of 204) | 21%, no signal |
| SAT bank: inferences | **36%** (49 of 138) | **14%** (20 of 139) |
| SAT bank: text structure and purpose | **36%** (54 of 149) | **15%** (23 of 149) |
| SAT bank: verb form and agreement | **36%** (54 of 150) | **15%** (23 of 149) |
| SAT bank: evidence questions | **34%** (84 of 248) | **18%** (47 of 256) |
| SAT bank: Math | **33%** (126 of 380) | **19%** (83 of 433) |
| SAT bank: punctuation boundaries, transitions | no signal | no signal |
| SAT practice tests: reading | **39%** (77 of 197) | **14%** (28 of 202) |
| ACT: Reading | **37%** (47 of 127) | 20%, no signal |
| ACT: Math, Science | no signal | no signal |
| Regents English (all types pooled) | **30%** (175 of 577) | no signal |
| Regents US History | **28%** (386 of 1,368) | 23%, tentative |
| Regents Living Environment | **29%** (466 of 1,604) | 23%, no signal |
| Regents Global History | 25%, no signal | 25%, no signal |

Chance is 25%. Bold is strong (p ≤ 0.01).

**Correction.** Earlier reports said reading-comprehension questions give
no answer-choice shortcut on any of three test makers. That was true of the
tests then run (length, word copying, extreme words). It is not true of
convergence, which holds on SAT and ACT reading. On Regents English it is
weak: present when all questions are pooled, not established within any
single question type.

---

## 2. Answer-key structure: the key is not random

**Idea.** Whoever assembles an answer key tends to "balance" it: each
position used about equally, and few back-to-back repeats. A random key does
neither. If the key is balanced, the answers a student is sure of say
something about the ones they are not.

**Measure.** Repeat rate: how often a question has the same correct position
as the one before (25% if random). Dispersion: how much the count of each
position varies from paper to paper (1.00 if random; below 1 means
over-balanced).

| Exam | Repeat rate | Dispersion | Verdict |
|---|---|---|---|
| Regents US History (30 exams) | **13.5%** | **0.04** | Heavily balanced |
| Regents Global History (25) | **14.3%** | **0.26** | Balanced |
| Regents English (33) | **13.9%** | **0.33** | Balanced |
| Regents Living Environment (43) | **19.9%** | **0.49** | Balanced |
| ACT (4 forms, 16 sections) | **19.8%** | 0.65, tentative | Fewer repeats than chance |
| SAT (8 practice tests) | 27.4%, no signal | 1.49 | Not balanced |

In all 30 US History keys the most-used and least-used positions differ by
at most two questions out of 50; in 20 of the 30, by at most one. A random
key manages the latter about 1 time in 60.

The SAT is the opposite: one module had position counts of 14, 5, 2 and 12.
College Board does not balance keys, so no counting strategy works there.

---

## 3. What they are worth

**Convergence**, learned on some papers and scored on papers never seen,
combined with the earlier signals:

| Exam | Blind guess | Two choices left | Before 8.2 |
|---|---|---|---|
| SAT bank, Reading & Writing | **+6.7** (±1.7) | **+6.6** (±1.2) | +4.6 / +4.6 |
| SAT bank: central ideas | **+13.3** (±8.1) | **+13.6** (±5.5) | 0 |
| SAT bank: evidence questions | **+8.8** (±4.9) | **+9.7** (±3.7) | +3 / +7 |
| SAT bank: verb form and agreement | **+18.6** (±6.5) | **+17.4** (±4.1) | +20 / +18 |
| SAT bank, Math | **+2.1** (±1.3) | **+1.5** (±1.1) | 0 |
| SAT practice tests, reading | **+13.0** (±6.3) | **+11.4** (±4.5) | 0 |
| ACT Reading | **+6.6** (±6.4) | **+4.4** (±4.2) | 0 |
| Regents US History | **+7.8** (±2.4) | **+6.9** (±1.8) | +7.3 / +6.0 |
| Regents Living Environment | **+5.5** (±1.9) | **+5.0** (±1.5) | +2.6 / +3.3 |
| Regents English, pooled | **+3.9** (±2.7) | **+2.6** (±1.8) | 0 |

Gains are percentage points of guess accuracy over an even guess, with 95%
intervals. In marks this is still about **0.4 to 1 question per paper** for
a student who guesses on one question in five.

**Key structure.** The realistic strategy is "count and fill": count the
positions of the answers you are sure of, and give each unsure question the
most under-used position. Simulated with the student sure of a random 80%
(or 50%) of answers:

| Exam | Sure of 80% | Sure of 50% |
|---|---|---|
| Regents US History | **+14.3** (±0.9) | **+6.9** (±0.4) |
| Regents English | **+9.7** (±2.9) | **+6.3** (±1.4) |
| Regents Global History | **+9.0** (±1.8) | **+4.9** (±0.9) |
| Regents Living Environment | **+5.2** (±1.9) | **+3.4** (±1.1) |
| ACT | +4.0 (±3.7) | +2.7 (±2.0) |
| SAT | −5.9 (±4.4): it loses marks | −3.9 (±3.1) |

On a 50-question US History exam, a student sure of 40 answers and guessing
10 gets about 3.9 of the 10 right instead of 2.5: **about 1.4 extra
questions**. This is the first strategy in the project worth more than one
question per exam.

---

## 4. Limits

- **Count-and-fill assumes the "sure" answers are right.** Wrong sure
  answers corrupt the count. The gain shrinks as the student's accuracy
  falls, and at 50% sure it is already half.
- **It has not been tested stacked** with the answer-choice rules; the two
  gains should not simply be added.
- **Regents US History, Global History and Living Environment are the older
  exam frameworks.** New York has replaced or is replacing them. Whether
  the new exams balance their keys is untested.
- **ACT: 4 forms only.** The repeat effect is strong; the balance effect
  and the strategy gain are tentative.
- **Key-structure counts use parsed questions only.** A few questions per
  exam were dropped in parsing, which breaks some adjacent pairs and
  slightly blurs the counts. It does not create the effect.
- **Convergence is measured on letters, not meaning.** It will miss
  paraphrased near-duplicates and can be fooled by shared boilerplate.
- **The rule combiner changed in 8.2.** Rules now vote with weights (their
  log-odds on the training papers) instead of cancelling when they
  disagree. Held-out numbers from before 8.2 are not directly comparable;
  the "Before 8.2" column is the previously published figure.
- Checks run: 2 convergence checks per question type, 2 key-structure
  checks per exam. Everything called strong is at p ≤ 0.01 and, for
  convergence, confirmed held-out.

Coverage: SAT 523 practice-test and 3,292 bank questions; ACT 681; Regents
English 789; Regents content exams 4,720. Answers: all official.
