# New York Regents English: 33 exams, 789 questions

> **Update (v8.2):** two later tests, convergence and answer-key structure, changed part of this picture, and the held-out figures below predate them. See [convergence-and-key-structure.md](convergence-and-key-structure.md).

**Source:** every Regents Examination in English Language Arts published on nysedregents.org from June 2014 to August 2026: **33 exams**, each with 24 multiple-choice reading questions (Part 1), **792 questions** in total, 789 analyzed. Answers come from New York State's official scoring keys. The list of files is in `regents-evidence/sources.txt`.

**Why this exam:** it has by far the largest free archive of the tests tried so far (33 forms against 8 for the SAT and 4 for the ACT), which is what a held-out check needs. The LSAT was the first choice, but official LSAT tests require an LSAC account; only one disclosed form is freely downloadable.

This was also the first run of the new one-command pipeline on an exam it had never seen. Three more Regents subjects, with a different result, are in `regents-subjects-cracked.md`.

---

## 1. Result: there is no answer-choice shortcut

| Test | Result on 789 questions | Verdict |
|---|---|---|
| Longest choice is right | 24% (163 of 667); chance is 25% | No signal |
| Shortest choice is right | 22% (143 of 654) | No usable signal (tentative, p = 0.034) |
| Choice using the most passage words | 28% (107 of 387) | No signal |
| Choice using the fewest passage words | 23% (54 of 237) | No signal |
| Choice echoing the question most / least | 8 of 39 / 4 of 12 | No signal |
| Extreme words (always, never, only) | 2% of correct answers, 2% of wrong ones | Myth |
| Hedge words (may, some, suggests) | 2% vs 2% | Myth |
| Answer position | (1) 206, (2) 202, (3) 191, (4) 190 | Balanced (p = 0.81) |

**Held-out check:** rules were learned on 32 exams and scored on the 33rd, for every exam in turn. **Pooled, no rule reached the threshold in any round. Gain: 0.** Split by question type, one weak rule appeared in some rounds and lost marks (−0.5 points overall, ±0.4).

So on Regents reading questions, the only way to gain marks is to read the passage. This matches the SAT and ACT, where reading questions also gave no usable shortcut; the surviving shortcuts on those tests are all in grammar and "do this goal" writing questions, which the Regents Part 1 does not have.

---

## 2. What the questions ask

Question types, labelled from the question wording (my own labels; New York publishes no categories on the key, so these could not be checked against an official source):

| Type | Count | Share | Typical wording |
|---|---|---|---|
| Detail and inference | 211 | 27% | "Lines 61 through 74 reveal that…", "…can best be described as" |
| Purpose of a part of the text | 205 | 26% | "…serves to", "…emphasizes", "…contributes to" |
| Literary device, tone, point of view | 175 | 22% | "…is an example of", "the tone of…", figurative language |
| Central idea or theme | 108 | 14% | "A central idea of the passage is…" |
| Vocabulary in context | 64 | 8% | "As used in line 7, the word … most nearly means" |
| Best evidence | 26 | 3% | "Which quotation best supports…" |

- Nearly every question points at **specific line numbers**. Go to those lines before reading the choices.
- **About half the questions (48%) ask what a part of the text does or which device it uses**, not what it says. Practise naming the job of a sentence or image.
- **The last question (Q24) is the most likely place for a central-idea question:** 13 of 33 exams.
- **Vocabulary questions are few** (about 2 per exam) and test the meaning in context: in 19 of 19 spot-checked, the key matched the plain contextual sense of the word.

---

## 3. Across three exam makers

| Pattern | SAT (College Board) | ACT | Regents (New York State) |
|---|---|---|---|
| Reading questions: any length or wording shortcut | None that earns marks | None | **None** (33 forms) |
| Extreme words predict wrong answers | No | No | **No** |
| Answer positions balanced | Yes | Yes, except even-numbered Math | **Yes** |
| Grammar: shortest often right, longest rarely | Yes (48% / 7%) | Yes (44% / 7%) | Not tested (no grammar questions) |

Three independent test makers, the same result: reading comprehension questions are built so that surface features of the choices tell you nothing.

---

## 4. Coverage and limits

- **Coverage:** 789 of 792 Part 1 questions from 33 of 33 published exams. 8 questions printed across the full page width had been cut in half by the two-column reader; 5 were repaired and 3 dropped. This did not change any result. Parts 2 and 3 (essays) were not analyzed.
- **Answers:** 789 official. Key alignment was spot-checked on 19 vocabulary questions from 16 exams, covering both key layouts (2014–2018 and 2019 onward) and the 2021 special form; all 19 keyed answers were plainly correct.
- **Parsing checks:** all clean (no missing answers, no missing choices, no glued-on text, no duplicate choices).
- **Open unknowns:** question-type labels are mine and unverified. No official difficulty data, so no "where the hard questions are" analysis.
- **Tell confidence:** the null result is well supported: 42 checks by type and 10 pooled (including the extreme-word and hedge-word tests), none strong, and the held-out gain is 0 across 33 forms.
- Evidence files are in `regents-evidence/`. Passages are not stored there; they belong to their authors and to New York State.
