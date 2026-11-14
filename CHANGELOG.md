# Changelog

## 8.3.0

- **`auto` adapter**: reads a paper in a layout it has never seen (numbering
  and choice styles, choices on one line, embedded keys, per-question answer
  lines, sections, PDF / Word / text), and hands SAT, ACT and NY Regents
  papers to their own adapters. 13 layout tests.
- **Upload page** (`ret.py serve`): drop papers and keys in a browser, get
  the report with a gauge per trick. Local by default, files deleted after
  each request. `Dockerfile` for hosting.
- `report.py` split into `analyze()` (data) and `render()` (Markdown).
- `.docx` input, standard library only.

## 8.2.0

- **Convergence test**: is the right answer the choice most like the others?
  New feature in `answer_dna.py`, the simulation and the report.
- **Answer-key structure** (`key_structure.py`): repeat rate, balance of
  position counts, and the value of counting strategies. Written by
  `ret.py run` as `key_structure.txt` and section 5 of `report.md`.
- **Weighted rule voting** in the simulation: rules that disagree no longer
  cancel; the stronger one wins. Held-out figures change with this version.
- **40x faster simulation**: leave-one-form-out now runs in one pass
  (41 s to 0.7 s on 4,700 questions), with identical results.
- **Correction:** "reading questions give no answer-choice shortcut" is
  withdrawn. See `docs/findings/convergence-and-key-structure.md`.
- 17 unit tests.

## 8.1.0

- `ret.py run` now writes `report.md`: a verdict per trick, held-out worth,
  a plain-language rulebook and the coverage footer (`scripts/report.py`).
- Unit tests for the statistics (`tests/test_stats.py`): exact tail
  probabilities, tie handling, placeholder choices, the simulation on a
  planted flaw and on a fair exam, the glued-text check.
- `regents-mc`: the parser no longer stops at the first written-answer
  question. Living Environment coverage rose from 1,732 to 2,028 of 2,305
  questions; findings updated (same direction, slightly larger held-out
  gain). "Note:" lines are no longer glued onto the last choice.

## 8.0.0

- Packaged as a public repository and Claude Code plugin.
- `SKILL.md` rewritten: phases numbered 1–8, a lane table, the ingest checks
  in one place, a signal-row output shape, and a dependency line.
- Synthetic demo exam (`examples/make_demo.py`) and an end-to-end smoke test.

## 7

- `regents-mc` adapter for NY Regents content exams. Full-width questions on
  two-column pages are detected and re-read.
- Extreme-word and hedge-word tests now run per question and feed the
  simulation.
- Significance test moved to log space; it overflowed above about 1,000
  questions per group.

## 6

- One-command pipeline (`ret.py ingest | validate | run`) and per-exam
  adapters on a shared item schema.
- Held-out score simulation (`simulate_score.py`).
- **Fix:** tied questions were counted as misses, which made every "the X
  choice is rarely right" figure look stronger than it was. Several earlier
  signals were withdrawn. See `docs/findings/corrections-and-score-simulation.md`.
- **Fix:** the ACT parser glued passage text onto answer choices.
- `regents-ela` adapter.

## 1–5

- Per-question records and counted pattern reports, answer DNA, official
  question-bank analysis, difficulty drivers, ACT support.
