# Evidence model (ported from REA)

REA never states a conclusion without a citable evidence record, and keeps
coverage separate from completeness. Apply the same discipline to test analysis.

## The question Evidence record

Phase 2 produces one record per question. Treat it like REA's evidence object:
a stable id other claims cite, plus provenance.

```json
{
  "qid": "Q12",                     // stable id; every pattern cites these
  "section": "Math",
  "skill": "linear-solve-for",       // atomic competency tag
  "difficulty": "med",
  "archetype": "linear-solve-for",   // template tag (groups questions)
  "trap": "right-answer-wrong-question",
  "answer": "C",
  "answer_source": "official",       // official | derived  (provenance)
  "fast_method": "isolate asked expression directly",
  "notes": "distractor A rewards solving for x not 2x"
}
```

Write all records to one JSON file, then run
`scripts/tally.py records.json --md` so every frequency is counted, not
eyeballed. The tally cites the qids behind each count — that is the evidence.

## Coverage is not completeness

- Record how many questions were analyzed and how many were skipped (and why:
  unreadable scan, missing figure, cut-off page).
- A pattern absent from the analyzed subset is **not** proven absent from the
  test. Say "not observed in the 40 questions analyzed", never "the test has no
  X".
- `answer_source` must stay honest: `official` only when a real key/scoring
  guide was supplied; otherwise `derived` (you solved it).

## Unknowns (REA record_unknown analog)

When a question can't be fully cracked, log an unknown instead of bluffing:

```json
{ "qid": "Q27", "unknown": "figure illegible in scan",
  "need": "clean image of the graph", "resolved": false }
```

Report open unknowns in the final output. Resolve one only when real evidence
(a clean page, the official key) arrives — not by guessing.

## Claims are hypotheses, not laws

Borrow REA's wording discipline:

- Archetypes and traps are **observed patterns**, with qid support.
- Answer-choice "tells" are **hypotheses**, default low confidence; on
  professionally built tests (College Board, ETS) they are largely neutralized.
  Never sell a tell as reliable without a strong, cited qid list.
- A fast method is a **recommended route**, flagged if it has failure cases.

## Mandatory footer (every analysis ends with this)

```
Coverage: N analyzed / M skipped (reasons).
Answers: X official / Y derived.
Open unknowns: [...].
Tell confidence: low unless stated, with qid support.
```
