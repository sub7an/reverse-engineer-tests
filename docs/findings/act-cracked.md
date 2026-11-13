# ACT: cracked, and compared with the SAT

> **Update (v8.2):** two later tests, convergence and answer-key structure, changed part of this picture, and the held-out figures below predate them. See [convergence-and-key-structure.md](convergence-and-key-structure.md).

**Source:** all 4 official ACT practice tests that ACT currently publishes on act.org (the enhanced ACT, 2025 onward). That's **684 questions**: English 200, Math 180, Reading 144, Science 160. Every answer and every reporting category comes from ACT's own scoring keys, and the parsed category totals match the totals ACT prints on each key exactly.

The same skill and scripts used for the SAT were run on the ACT, which tests whether the skill works on "any test". Strong = p ≤ 0.01; tentative = 0.01–0.05.

> **Corrected.** Sections 2 to 5 were revised after two flaws were found: the parser had glued passage text onto some English answer choices, and ties were miscounted. The Science, Reading and Math answer-choice signals are withdrawn; the English grammar signals got stronger. Structure, keys and the NO CHANGE count are unaffected. Details: `corrections-and-score-simulation.md`.

---

## 1. Structure

| Section | Questions | Scored | Not scored (field test) |
|---|---|---|---|
| English | 50 | 40 | 10: one whole passage |
| Math | 45 | 41 | 4: single questions spread through the section |
| Reading | 36 | 27 | 9: one whole passage |
| Science (optional) | 40 | 34 | 6: one whole passage |

- **17% of ACT questions don't count** (116 of 684). The unscored passage moves between tests (English Q41–50, Q16–25, Q11–20, Q31–40 in the four tests), so you can't tell which one it is. Treat every question as real.
- **Choices alternate letters:** odd questions use A–D, even questions use F–J. The enhanced ACT has 4 choices everywhere, including Math.
- **English questions now carry explicit stems.** One stem, "Which choice makes the sentence most grammatically acceptable?", covers 74 of 200. My stem-based classifier agreed with ACT's official categories on **160 of 160** scored English questions.

**English question types (200 questions):**
| Type | Count | ACT category |
|---|---|---|
| Grammar: usage (verbs, pronouns, modifiers, agreement) | 45 | Conventions (CSE) |
| Grammar: punctuation | 33 | Conventions (CSE) |
| Rhetorical goal ("the writer wants to…") | 37 | Production of Writing (POW) |
| Concision ("least redundant") | 17 | Knowledge of Language (KLA) |
| Add a sentence? | 16 | POW |
| Transitions | 15 | POW |
| Tone / style | 11 | KLA |
| Delete a sentence? | 11 | POW |
| Clarity / word choice | 10 | KLA |
| Organization (sentence order, placement) | 5 | POW |

---

## 2. ACT folklore, tested

| Popular ACT tip | What 4 official tests show | Verdict |
|---|---|---|
| "NO CHANGE is right about a quarter of the time" | **39 of 158 = 25%**, exactly chance | True, and there's no bias either way. Don't avoid it, don't favour it. |
| "OMIT / DELETE is usually right" | "Delete the underlined portion" was right 2 of 10 times (20%) | **Myth** |
| "The shortest answer is right on grammar questions" | Grammar + concision: shortest right **48%** (38 of 79) vs 25% by chance. On concision questions alone: 65% (11 of 17). | **True** (strong, p < 0.001) |
| "Avoid extreme words" | Reading: 3% of correct vs 3% of wrong answers | **Myth** (no difference) |
| "Answer letters are random" | Reading, Science, English: balanced. **Math even-numbered questions: J is right 35 of 88 (40%), and it's the most common even letter in all 4 tests.** | Balanced, except a math quirk (see section 3) |

---

## 3. Answer-choice signals

| Signal | Evidence | Strength |
|---|---|---|
| **English grammar: the longest choice is rarely right** | 4 of 59 (7%) | Strong. **Same as the SAT** (verb/agreement 7%). |
| **English grammar: the shortest choice is often right** | 27 of 62 (44%) | Strong. **Same as the SAT** (verb/agreement 48%). |
| **English concision ("least redundant"): pick the shortest** | Shortest right 11 of 17 (65%); longest right 0 of 17 | Strong, but only 17 questions |
| **Math numeric choices: the right value leans to the middle two** | 31 of 48 (65%) | Tentative (p = 0.03). Same direction as the SAT. |
| Withdrawn: "Reading: the choice sharing the fewest words with the question is almost never right" | Only 7 questions have a unique such choice; it was right in 1. The earlier "1 of 37" counted tied questions as failures. | **Withdrawn** |
| Withdrawn: Science signals (longest, most-copied, most-echoing choice rarely right) | Longest 16 of 66 (24%); most passage words 6 of 24 (25%); most question overlap 1 of 5 | **Withdrawn** |
| Withdrawn: "Math: the right answer is rarely the longest or shortest expression" | Longest 11 of 48 (23%), shortest 11 of 59 (19%) | **Withdrawn** |
| **Math, even-numbered questions: J is right more often** | 35 of 88 (40%); the top even letter in all 4 tests; F only 13 | Strong in these 4 tests (p = 0.006), but **only 4 test forms**, and odd questions don't mirror it (D is the *rarest* odd letter). Use it **only as a last-resort blind guess** on even math questions. |
| English rhetorical questions: fuller choices lean right | Shortest right 4 of 37 (11%); longest 12 of 35 (34%) | Tentative (p = 0.03). Same direction as the SAT notes-synthesis signal. |

**Held-out check:** when rules are learned from 3 tests and scored on the 4th, only "grammar: cross out the longest" is learned, and its measured gain is not established (+0.1 points overall, ±0.5). Four tests are too few to confirm any ACT tie-breaker out of sample; the grammar ones are trusted mainly because the SAT shows the same pattern on far more questions.

---

## 4. SAT vs ACT: what's universal

| Pattern | SAT (3,767 bank + 960 test questions) | ACT (684 questions) | Verdict |
|---|---|---|---|
| Grammar: the longest choice is rarely right | 7% (verb/agreement) | 7% | **Universal** |
| Grammar: the shortest choice is often right | 48% (verb/agreement) | 44% (48% with concision) | **Universal** |
| Rhetorical/synthesis: fuller choices win | Strong (longest right 37%, shortest 14%) | Same direction (shortest right 11%), tentative | Likely universal; needs more ACT data |
| Math numeric answers lean to the middle two values | 56% | 65% | Same direction, weak on both |
| Extreme words predict wrong answers | No | No | **Universal myth** |
| Answer letters balanced | Yes | Yes, except ACT even-question math | Mostly |
| Choice sharing the fewest words with the question is almost never right (reading) | 33% once ties are excluded | 1 of 7 | **Withdrawn on both** |
| Math: the right answer isn't the longest or shortest expression | 21–23% | 19–23% | **Withdrawn on both** |

**Bottom line:** two patterns hold on both tests. In grammar, the correct answer is the leanest correct wording, so the shortest choice is right nearly half the time and the longest almost never. In "do this goal" writing questions, the correct answer has to carry the whole goal, so fuller choices win. Reading, science and math give no answer-choice shortcut on either test.

---

## 5. ACT test-day tie-breakers

Use only after narrowing to two choices:
- **English grammar and concision:** prefer the shortest correct option; the longest is rarely right. This is the one ACT tie-breaker with solid support.
- **English "the writer wants to…" questions:** lean away from the shortest choice.
- **English "NO CHANGE":** it's right 1 in 4. Judge it like any other choice.
- **Reading and Science:** no tie-breaker works. Go back to the passage or the data.
- **Math:** no length tie-breaker works. If you must guess blind on an even-numbered math question, J has been the most common answer.
- **Never leave a blank:** the ACT has no guessing penalty, and 17% of questions don't count anyway.

---

## 6. Coverage and limits

- **Coverage:** 684 questions from 4 official tests, with answers and categories from ACT's keys. Choice-level analysis used 681; 3 Science questions were excluded because their choices are tables the PDF text couldn't capture.
- **Key parsing:** checked three ways. Every key letter matches its question's letter set (odd A–D, even F–J), every question's answer letter exists among its parsed choices, and category totals match ACT's printed totals in all 4 tests.
- **No official difficulty:** ACT's practice tests don't publish difficulty ratings, so there's no ACT equivalent of the SAT Question Bank analysis.
- **Small sample:** 4 test forms. Signals marked strong held at p ≤ 0.01, but 65 checks were run in total, so roughly 3 could cross p < 0.05 by chance. Each "longest/shortest" test counts only questions where one choice is the unique extreme, and "No Change" and "Delete the underlined portion" are left out of length comparisons. The J effect in particular could be a quirk of these 4 forms.
- **Math choices** were flattened from the PDF; formulas drawn as images came through empty, so "expression length" covers 101 of 180 math questions.
