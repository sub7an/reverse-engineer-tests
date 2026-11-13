# Contributing

The most useful contribution is **an adapter for a new exam**, with the
findings it produced.

## Add an exam

1. Copy `skills/reverse-engineer-tests/scripts/adapters/generic.py` to
   `<exam>.py`. Set `NAME` and `USAGE`, and write `parse(inputs, form, opts)`
   so it returns items built with `make_item` (schema in `ret_common.py`).
2. Register it in `adapters/__init__.py`.
3. Ingest every public form you can find, each with its own `--form`.
4. Run `ret.py validate` until every flag is cleared or explained.
5. Spot-check 15+ keyed answers on questions you can answer yourself. A
   misaligned key looks exactly like "no pattern".
6. Run `ret.py run` and write the result up in `docs/findings/`, including
   the null results and the coverage footer.

## Rules

- **No exam content in the repository.** No PDFs, no parsed question text,
  no `items.json`. Counts, percentages and short stem patterns are fine.
  Link to the publisher's own archive instead.
- **No signal without its held-out value.** A finding that reports p-values
  but not the simulation result will be sent back.
- **Report nulls.** "Nothing works on this exam" is a finding.
- Standard library only; `pdftotext` is the single external tool.
- `bash tests/smoke.sh` must pass.

## Reporting a wrong finding

Open an issue with the exam, the claim, and what you counted. Corrections
are published, not buried; see
`docs/findings/corrections-and-score-simulation.md` for the precedent.
