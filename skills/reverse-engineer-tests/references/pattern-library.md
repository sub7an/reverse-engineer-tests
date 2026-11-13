# Pattern library — common archetypes by subject

Starter archetypes to match against. These are priors, NOT answers. Always
confirm each against the actual paper and cite Q#s. Add new archetypes you find.

## Math (SAT/ACT-style)

- **Linear solve-for** — one/two linear equations; trap: solves for the variable,
  not the asked expression. Fast: isolate the asked expression directly.
- **System of equations** — trap: finds one variable when asked for a combo.
  Fast: elimination toward the asked quantity.
- **Percent / ratio word problem** — trap: percent of wrong base, or part vs.
  whole. Fast: pick 100.
- **Function evaluation / composition** — trap: order of composition. Fast:
  work inside-out.
- **Quadratic / vertex** — trap: sign of vertex, roots vs. factors. Fast:
  complete-square or Vieta.
- **Geometry with figure** — trap: assumes not-to-scale figure is to scale.
  Fast: label knowns, use the one relation asked.
- **Data / table reading** — trap: reads wrong row/column or ignores units.
- **Exponential growth/decay** — trap: confuses rate with factor.

## Reading / verbal

- **Main idea / purpose** — trap: too narrow (a detail) or too broad.
- **Inference** — trap: outside knowledge, or overreach beyond the text.
- **Command of evidence** — paired; trap: picks a line that supports a wrong
  content answer. Use evidence-pair lock.
- **Vocabulary in context** — trap: the word's common meaning vs. its passage
  meaning.
- **Function of a sentence/paragraph** — trap: describes content, not role.
- **Two-passage compare** — trap: attributes passage A's view to passage B.
- **Data + text (graphs in reading)** — trap: data contradicts the tempting
  text-only answer.

## Writing / grammar

- **Subject-verb agreement** — trap: intervening phrase hides the subject.
- **Pronoun / antecedent** — trap: ambiguous or number-mismatched pronoun.
- **Punctuation (comma/semicolon/colon)** — trap: comma splice, or colon after
  a non-independent clause.
- **Modifier placement** — trap: dangling modifier.
- **Concision** — trap: the grammatical-but-wordy choice; shortest correct
  usually wins.
- **Transition logic** — trap: however/therefore reversed relative to the
  sentence relationship.

## ACT (enhanced, 2025+)

- **Structure:** English 50, Math 45, Reading 36, Science 40 (optional). About
  17% of items are unscored field tests: one whole passage in English (10),
  Reading (9) and Science (6), plus 4 single Math items. Their position varies.
- **Letters alternate:** odd questions A–D, even questions F–J; 4 choices
  everywhere, including Math.
- **English stems are standardized:** "most grammatically acceptable" (about
  37%), "least redundant", "maintains the essay's tone", "transition…most
  logical", "clearest and most precise", add/delete a sentence, sentence
  order. Stems map 1:1 onto ACT's categories (CSE / KLA / POW).
- **Folklore checked (4 forms):** NO CHANGE right 25% (no bias); "Delete the
  underlined portion" right 2/10 (myth); shortest right on grammar and
  concision 48% (38/79) vs 25% chance; longest right 5%.
- **Parsing trap:** in English the passage is printed beside the questions, so
  passage lines get glued onto choice D/J unless a choice ends at the blank
  line after it. `validate_items.py` flags this as "swallowed".

## NY Regents ELA (Part 1, 2014+)

- **Structure:** 24 reading questions on three texts, choices numbered
  (1)–(4), nearly every stem cites line numbers. 33 public forms with keys at
  nysedregents.org/hsela (adapter: `regents-ela`).
- **Types (792 items, stem-labelled):** detail/inference 27%, purpose of a
  part 26%, device/tone 22%, central idea 14%, vocab in context 8%, best
  evidence 3%. Q24 is a central-idea question in 13/33 forms.
- **Answer-choice signals:** none. Length, passage-word and question-overlap
  tests all at chance; held-out gain 0 over 33 forms. Positions balanced.
- **Parsing trap:** question pages are two-column; read each half-page
  separately (`pdftotext -x 0 -W 306`, then `-x 306`), or questions interleave.

## NY Regents content exams (US History, Global History, Living Environment)

- **Archives:** nysedregents.org, 25–45 public forms per subject with keys
  (adapter: `regents-mc`, pass the subject with `--exam`). 50 MC per history
  exam; Living Environment has about 52, some mixed into later parts.
- **Folklore works here** (100 forms, 4,720 items, confirmed held-out): the
  only choice with an extreme word is right 8% (US History, Living
  Environment); the only hedged choice is right 49–64% (all three); the
  longest choice is right 33% in US History and 28% in Living Environment.
  Global History shows only the hedge effect. Held-out gain: US History +7
  points blind, +6 with two choices left; still under one question per exam.
- **Lesson:** content exams written by state committees leak surface tells
  that College Board, ACT and reading tests do not. Test folklore per exam
  family; do not carry a "myth" verdict from one family to another.
- **Parsing traps:** stimulus questions are printed full-width on two-column
  pages (the adapter detects and re-reads them); footers and "Base your
  answer to question N" lines get glued onto the last choice.

## AP / subject exams (free response + MCQ)

- **Stimulus-based MCQ** — document/graph/scenario drives several questions;
  archetype repeats per stimulus type.
- **FRQ rubric points** — each point is a discrete claim+evidence; reverse the
  rubric to see what phrasing earns each point.

## Answer-choice structure (use with low default confidence)

Only report when it genuinely recurs with citations. On professionally built
tests (College Board, ETS) these are deliberately neutralized — do not oversell:

- Longest / most-qualified choice bias
- Choices that merely restate the stem
- "All/none of the above" placement
- Numeric choices clustered to hide the trap value in the middle
