# Corrections, and what the answer-choice signals are really worth

Scaling the work up meant building two things: a one-command pipeline, and a simulation that scores the signals on tests they were not learned from. The simulation disagreed with earlier reports, and tracing the disagreement found **two errors in my earlier analysis**. This page says what was wrong, what survives, and what the surviving signals are worth in marks. The other reports have been corrected to match.

---

## 1. What was wrong

**Error 1: ties were counted against chance (affects SAT and ACT).**
The test asked "how often is the correct answer the *uniquely* longest choice?" and compared the rate with 25%. But in many questions no choice is uniquely longest, because two or more tie. In those questions the correct answer can never count as "the longest", so the true chance rate is below 25%. Every "the X choice is almost never right" figure was pushed down by this, most of all where ties are common:

- **Word overlap with the question:** most questions use a standard stem, so most choices tie at zero shared words.
- **Math choice length:** numbers like 12, 15, 18, 21 all have the same length.

The fix: count only questions where one choice really is the unique extreme. Then 25% is the right comparison.

**Error 2: the ACT parser glued passage text onto answer choices.**
In the ACT English section the passage is printed beside the questions. In about 41 of 200 English questions, lines of passage text were attached to the last choice (D or J), making it look far longer than it is. Separately, "No Change" was measured as a 9-character choice, although it stands for the underlined text. Both distorted the ACT length figures. The parser now stops a choice at the blank line after it, and placeholder choices are left out of length comparisons.

Answers and official categories were never affected: all 684 ACT keys and all SAT answers are unchanged.

---

## 2. What survives, and what does not

| Earlier claim | Corrected result | Verdict |
|---|---|---|
| SAT verb/agreement questions: shortest often right, longest almost never | Shortest **48%** (84 of 174), longest **7%** (10 of 153). Same at every difficulty. | **Holds. Stronger than reported.** |
| SAT notes synthesis: longest often right, shortest rarely | Longest **37%** (73 of 198), shortest **14%** (28 of 195) | **Holds** |
| SAT notes synthesis: the choice sharing the fewest words with the goal is almost never right | **7%** (6 of 83) | **Holds** |
| SAT hard reading questions: the longest choice is usually wrong | **18%** on hard (54 of 295); 31% on easy | **Holds** (hard questions only) |
| ACT grammar: longest rarely right, shortest often | Longest **7%** (4 of 59), shortest **44%** (27 of 62) | **Holds. Stronger than reported.** |
| SAT/ACT: extreme words, hedges, answer letters | No effect | **Still myths** |
| **Reading: the choice sharing the fewest words with the question is almost never right** ("universal") | SAT bank: 9 of 27 (33%). ACT Reading: 1 of 7. | **Withdrawn.** A tie artifact. |
| **Math: the right answer is rarely the longest or shortest expression** ("universal") | SAT bank: longest 23%, shortest 21%. ACT: 23% and 19%. | **Withdrawn.** A tie artifact. |
| **ACT Science: longest choice, most-copied choice, most-echoing choice are rarely right** | Longest 24%, most passage words 25%, most question overlap 1 of 5 | **Withdrawn** |
| SAT punctuation boundaries: longest almost never right (7%) | 17% overall (14 of 83), not significant. **9% on hard ones** (4 of 46). | **Narrowed** to hard boundary questions |
| SAT transitions and vocab: longest usually wrong | Transitions longest 19%, vocab 23%: not significant | **Withdrawn**, replaced below |
| ACT "shortest right 47% on grammar and concision" | **48%** (38 of 79) | **Holds**, now strong |

**New findings from the corrected test:**
- **SAT transitions: the shortest choice is right 36%** (59 of 166, strong).
- **SAT evidence questions: the shortest choice is right only 14%** (35 of 250, strong).
- **SAT central ideas: the choice using the most passage words is right 35%** (45 of 128, strong, but it did not hold up in the simulation below).
- **ACT concision ("least redundant") questions: the shortest choice is right 65%** (11 of 17); the longest was never right (0 of 17). Small sample.

Unchanged and unaffected: everything about structure, question types, where hard questions live, what makes questions hard, the math "middle two values" lean (56%), and the ACT even-question J quirk in Math.

---

## 3. What the signals are worth in marks

**Method.** Rules are learned from some forms and scored on forms they never saw (for the Question Bank, five random groups of questions). A rule needs p ≤ 0.01 on the training forms. Two situations are scored: a **blind guess** (25% without rules) and a guess when **two choices are left** (50% without rules). Gains are percentage points of guess accuracy, with a 95% interval.

**SAT Question Bank, Reading & Writing (1,845 questions):**

| Skill | Blind guess | Two choices left |
|---|---|---|
| Verb form and agreement | **+20 points** (±6) | **+18** (±4) |
| Notes synthesis | **+11** (±6) | **+12** (±4) |
| Evidence questions | **+3** (±1) | **+7** (±3) |
| Transitions | **+6** (±5) | **+4** (±4) |
| Vocab, inferences, central ideas, structure, cross-text, boundaries | 0 (no rule holds up) | 0 |
| **All Reading & Writing** | **+4.6** (±1.2) | **+4.6** (±1.0) |

**SAT Math (1,447 questions):** no rule reaches the threshold. Gain **0**.

**8 SAT practice tests (523 questions):** grammar **+12** blind (±8), **+9** two-left (±6). Everything else 0. All questions: +2.3 blind (±2.1), +1.3 two-left (±1.7, not established).

**4 ACT tests (681 questions):** only "grammar: cross out the longest" is learned, and with 4 forms the measured gain is **+0.1 overall (±0.5), not established**. The ACT grammar signal is statistically strong in the pooled data, but four forms are too few to confirm it out of sample.

**In real marks.** A typical SAT has about 7 verb/agreement, 7 notes-synthesis, 7 transition and 9 evidence questions. A student who is stuck between two choices on *every one* of those 30 questions gains about **3 questions**. A student stuck on one in five of them gains about **0.6 of a question per test**, on the order of 10 scaled points at most. In math the gain is zero.

**33 New York Regents English exams (789 reading questions):** no rule reaches the threshold in any of 33 held-out rounds. Gain **0**. See `regents-ela-cracked.md`.

**100 Regents content exams (US History, Global History, Living Environment; 4,424 questions):** here the classic tips do hold. US History **+7.3** blind (±2.3), **+6.0** two-left (±1.8); Living Environment +2.2 two-left (±1.4); Global History under +1. See `regents-subjects-cracked.md`.

**Conclusion.** The answer-choice signals are real but small, and they live in three question types: verb/agreement, notes synthesis and (ACT) grammar. They are tie-breakers for a handful of questions, not a way to score. State content exams leak more than the national tests, but still under one question per exam. The marks are in the other findings: which skills are hard, what each question type asks, and what makes hard questions hard.

---

## 4. Why this was caught now

Earlier reports tested each signal on the same questions it was found in. The simulation is the first check that used held-out questions, and a held-out check does not care how a p-value was computed: a rule either earns marks on unseen questions or it does not. Math "eliminate the longest and shortest" predicted a gain of about 14 points and delivered 1. That gap led to the tie error.

The skill now runs the simulation on every analysis and reports a signal only with its held-out value, and its validator flags glued-on choice text before any statistics are run.

---

## 5. Evidence

`pipeline-evidence/` holds the corrected outputs: `*-answer_dna.txt` (signal tests), `*-simulation.txt` (held-out gains), `*-validation.txt` (parsing checks), for the 8 SAT tests (`sat-`), the bank's Reading & Writing (`qbrw-`) and Math (`qbm-sec-`), and the ACT (`act-`).

Coverage: SAT 524 of 528 Reading & Writing practice-test questions; Question Bank 1,845 RW and 1,447 Math multiple-choice; ACT 681 of 684. Answers: all official. Checks run: 22 (SAT tests), 52 (bank RW), 6 (bank Math), 65 (ACT), so 1 to 3 results per run could cross p < 0.05 by luck; only p ≤ 0.01 is called strong.
