# Regents US History, Global History and Living Environment: 100 exams, 4,720 questions

**Source:** every exam in three archives on nysedregents.org, with New York State's official scoring keys:

| Subject | Exams | Years | Questions analyzed |
|---|---|---|---|
| US History & Government (2005 standard) | 30 | 2010–2020 | 1,486 |
| Global History & Geography (2005 standard) | 25 | 2010–2018 | 1,206 |
| Living Environment (biology) | 45 | 2010–2026 | 2,028 |

Unlike the SAT, ACT and Regents English, these are **content exams**: most questions test knowledge, not a passage. That turns out to matter.

---

## 1. Result: here the old test-taking folklore works

On the SAT, the ACT and Regents English, "avoid extreme words" and "pick the hedged answer" were myths. On these three exams they are real.

| Tip | US History | Living Environment | Global History |
|---|---|---|---|
| **The only choice with a hedge word** (may, some, often, likely…) is right | **49%** (24 of 49) | **50%** (56 of 113) | **64%** (14 of 22) |
| **The only choice with an extreme word** (only, all, always, never, must…) is right | **8%** (8 of 99) | **8%** (17 of 211) | 19% (6 of 31), not significant |
| **The longest choice** is right | **33%** (440 of 1,353) | **28%** (484 of 1,737) | 26%, no signal |
| **The shortest choice** is right | **21%** (283 of 1,379) | **21%** (352 of 1,669) | 25%, no signal |
| Answer position | Balanced | Balanced | Balanced |

Chance is 25% in every row. Every bold figure is strong (p ≤ 0.01). The same counts on other exams, for comparison: on the SAT question bank the only choice with an extreme word is right 29% and the only hedged one 24%; on Regents English 18% and 23%. No signal there.

The length signal is not one era's quirk: in US History the longest choice is right 29% in 2010–2014 and 36% in 2015–2020, and it holds for both plain questions (34%) and questions about a cartoon, graph or passage (30%).

---

## 2. What it is worth in marks

Rules were learned on 99 exams and scored on the 100th, for every exam in turn.

| Subject | Blind guess (25% without rules) | Two choices left (50% without rules) |
|---|---|---|
| US History | **+7.3 points** (±2.3) | **+6.0** (±1.8) |
| Living Environment | **+2.6** (±1.7) | **+3.3** (±1.4) |
| Global History | +0.7 (±0.5) | +0.5 (±0.3) |
| All three | **+3.6** (±1.0) | **+3.4** (±0.8) |

In real marks: a US History exam has 50 multiple-choice questions. A student who must guess on 10 of them gains about **0.7 of a question**. The word rules are strong when they apply but apply to few questions: about 3 questions per US History exam have exactly one extreme-word choice, and fewer than 2 have exactly one hedged choice.

So the rules are real and confirmed, but again worth under one question per exam. They are best used as tie-breakers.

---

## 3. Tie-breakers for these exams

Use only when stuck between choices:
- **Cross out a choice that says only, all, always, never, must or cannot** when no other choice does. It is right about 1 time in 12.
- **Favour a choice that says may, some, often or likely** when no other choice does. It is right about half the time.
- **US History and Living Environment: lean to the longest choice and away from the shortest.**
- **Global History: none of the length rules work.** Only the hedge-word rule holds.
- No answer position is favoured.

---

## 4. Across five exam families

| Pattern | SAT | ACT | Regents English | Regents US History / Living Environment | Regents Global History |
|---|---|---|---|---|---|
| Extreme-word choice is rarely right | No | No | No | **Yes** | No |
| Hedged choice is often right | No | No | No | **Yes** | **Yes** |
| Longest choice is often right | No (only in notes synthesis) | No | No | **Yes** | No |
| Grammar: shortest often right | **Yes** | **Yes** | not tested | not tested | not tested |
| Reading questions: any shortcut | No | No | No | not tested | not tested |
| Answer positions balanced | Yes | Mostly | Yes | Yes | Yes |

The national admissions tests and reading tests have had these surface tells removed. The state content exams have not: writers of factual questions tend to make false statements absolute and true statements careful and complete. That is a hypothesis about the cause; the counts above are the evidence that the pattern exists.

---

## 5. Coverage and limits

- **Coverage:** 4,720 of 5,100 multiple-choice questions listed on the keys (93%). US History 1,486 of 1,550; Global History 1,206 of 1,245; Living Environment 2,028 of 2,305.
- **Skipped, and why:**
  - Living Environment: about 280 questions, mostly ones with diagrams as choices or full-width layouts that could not be repaired. An earlier version of the parser stopped at the first written-answer question and missed about 300 more; that is fixed, and the results did not change in direction.
  - US History August 2015 (50 questions): question 1 could not be read from the PDF, so the whole exam was left out.
  - 75 questions dropped by the parsing checks (wrong number of choices, glued-on text, duplicate choices, keyed answer not among the choices).
- **Repairs:** About 1,040 questions printed across the full page width were being cut in half by the two-column reader. They are now re-read from the full-page text; about 370 more that could not be repaired were dropped.
- **Answers:** all official. Spot-checked on 21 random questions across the three subjects, plus 14 of the Living Environment questions recovered later; every keyed answer that could be judged from the question alone was correct.
- **Word lists** are fixed lists written before this analysis (extreme: all, always, never, only, must, none, every, cannot…; hedge: may, might, could, some, likely, often, suggests…). A different list would give somewhat different counts.
- **Checks run:** 25 in this analysis, so about 1 could cross p < 0.05 by luck; the results called real here are all at p ≤ 0.01 and were confirmed on held-out exams.
- **Not done:** question-type labels, and no official difficulty data exists.
- **These archives are the older exam frameworks.** New York has since introduced new versions of the history exams and is replacing Living Environment; the patterns may not carry over.
- Evidence files are in `regents-evidence/subjects/`.
