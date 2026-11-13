#!/usr/bin/env python3
"""
tally.py — deterministic pattern counts for reverse-engineer-tests.

Input: a JSON file (the per-question Evidence records from Phase 2), either a
list of records or {"questions": [...]}. Each record SHOULD have:

  {
    "qid": "Q12",            # stable id, required
    "section": "Math",       # optional
    "skill": "linear-solve-for",   # atomic skill tag, required for distribution
    "difficulty": "med",     # easy|med|hard, optional
    "archetype": "linear-solve-for",  # template tag, required for archetypes
    "trap": "right-answer-wrong-question",  # trap tag, optional
    "answer": "C",           # optional
    "answer_source": "official"  # official|derived, optional
  }

Output: JSON to stdout with counts and the qids behind every count, so no
frequency is ever guessed. Counts are evidence, cited by qid.

Usage:
  python3 tally.py questions.json
  python3 tally.py questions.json --md      # markdown report instead of JSON
"""
import json
import sys
from collections import defaultdict


def load(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("questions") or data.get("evals") or []
    return data


def group(records, key):
    out = defaultdict(list)
    for r in records:
        qid = r.get("qid", "?")
        v = r.get(key)
        if v is None or v == "":
            out["(unlabeled)"].append(qid)
        else:
            out[str(v)].append(qid)
    # sort by count desc, then name
    return dict(sorted(out.items(), key=lambda kv: (-len(kv[1]), kv[0])))


def tally(records):
    total = len(records)
    seen_qids = [r.get("qid", "?") for r in records]
    dupes = sorted({q for q in seen_qids if seen_qids.count(q) > 1})
    missing_skill = [r.get("qid", "?") for r in records if not r.get("skill")]
    derived = [r.get("qid", "?") for r in records
               if r.get("answer_source") == "derived"]
    official = [r.get("qid", "?") for r in records
                if r.get("answer_source") == "official"]
    return {
        "total_questions": total,
        "skill_distribution": group(records, "skill"),
        "archetype_frequency": group(records, "archetype"),
        "trap_catalog": group(records, "trap"),
        "difficulty_split": group(records, "difficulty"),
        "section_split": group(records, "section"),
        "coverage": {
            "duplicate_qids": dupes,
            "questions_missing_skill_tag": missing_skill,
            "answers_official": len(official),
            "answers_derived": len(derived),
            "note": ("A pattern is real only if its qid list has 2+ entries. "
                     "A missing tag is not evidence of absence."),
        },
    }


def to_md(t):
    lines = [f"# Pattern tally ({t['total_questions']} questions)\n"]

    def block(title, d, note=None):
        lines.append(f"## {title}")
        if note:
            lines.append(f"_{note}_\n")
        if not d:
            lines.append("_none_\n")
            return
        for k, qids in d.items():
            flag = "" if len(qids) >= 2 or title.startswith("Skill") else "  (single occurrence: anecdote, not pattern)"
            lines.append(f"- **{k}** - {len(qids)}: {', '.join(qids)}{flag}")
        lines.append("")

    block("Skill distribution (where the marks live)", t["skill_distribution"])
    block("Archetype frequency", t["archetype_frequency"],
          "2+ qids = pattern; 1 qid = anecdote")
    block("Trap catalog", t["trap_catalog"])
    block("Difficulty split", t["difficulty_split"])
    block("Section split", t["section_split"])
    c = t["coverage"]
    lines.append("## Coverage & integrity")
    lines.append(f"- official answers: {c['answers_official']}, "
                 f"derived answers: {c['answers_derived']}")
    if c["duplicate_qids"]:
        lines.append(f"- duplicate qids: {', '.join(c['duplicate_qids'])}")
    if c["questions_missing_skill_tag"]:
        lines.append(f"- missing skill tag: "
                     f"{', '.join(c['questions_missing_skill_tag'])}")
    lines.append(f"- {c['note']}")
    return "\n".join(lines)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    md = "--md" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)
    records = load(args[0])
    t = tally(records)
    print(to_md(t) if md else json.dumps(t, indent=2))


if __name__ == "__main__":
    main()
