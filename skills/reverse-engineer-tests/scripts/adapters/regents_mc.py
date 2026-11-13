"""Any New York Regents exam with numbered multiple-choice questions and
choices (1)-(4): US History, Global History, Living Environment and others.

Inputs: the exam PDF and its scoring key (or "scoring key and rating guide")
PDF from nysedregents.org. The key decides which question numbers are
multiple choice; constructed-response questions are left out. Pass the
subject with --exam (it becomes the block, so subjects are analyzed apart).
Uses the two-column page reader and both key layouts from regents_ela.py.
"""
from ret_common import make_item

from .regents_ela import parse_exam, parse_key

NAME = "regents-mc"
USAGE = "regents-mc <exam.pdf> <scoring-key.pdf> --form USH-2019-06 --exam 'US History'"


def parse(inputs, form, opts):
    if len(inputs) < 2:
        raise SystemExit("usage: " + USAGE)
    key = parse_key(inputs[1])
    n = max(key) if key else 0
    raw = {i["q"]: i for i in parse_exam(inputs[0], n, numbers=key)}
    exam = opts.get("exam") or "Regents"
    cut = [q for q in raw if raw[q].get("truncated")]
    for q in cut:  # full-width questions, damaged by the two-column read
        del raw[q]
    got = [q for q in key if q in raw and len(raw[q]["choices"]) == 4]
    opts.setdefault("log", []).append(
        f"{form}: key has {len(key)} multiple-choice questions (up to Q{n}); "
        f"{len(got)} parsed with 4 choices; "
        f"{sum(bool(raw[q].get('repaired')) for q in raw)} full-width questions repaired, "
        f"{len(cut)} dropped")
    return [make_item(
        qid=f"{form}-Q{q}", exam=exam, form=form, section="MC", q=q, block=exam,
        passage="", stem=raw[q]["stem"].strip(), choices=raw[q]["choices"],
        answer=key[q]) for q in sorted(key) if q in raw]
