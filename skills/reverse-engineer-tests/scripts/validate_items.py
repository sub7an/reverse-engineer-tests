#!/usr/bin/env python3
"""
validate_items.py: catch parsing damage before any statistics are run.

Every check here exists because the damage it catches once produced a wrong
or blurred finding. Run it on every ingest; fix the adapter until it is clean,
or pass the listed qids to `ret.py run --exclude`.

Checks, per form and section:
  count            questions found, and gaps in the numbering
  choices          how many choices each question has (the odd ones are listed)
  no-answer        the key gave no answer
  answer-missing   the key letter is not among the parsed choices
  letter-set       choice letters break the paper's odd/even alternation
  swallowed        one choice is far longer than its siblings: text from the
                   passage or the next question was glued onto it. This
                   corrupts every length-based statistic.
  duplicate        two choices have identical text
  empty-stem       choices but no question text
  unconfirmed      the adapter could not find the answer text in the explanation

Usage:
  python3 validate_items.py items.json [more.json ...]
"""
import sys
from collections import Counter, defaultdict

from ret_common import load_items


def swallowed(choices):
    lens = sorted(len(v) for v in choices.values())
    return len(lens) >= 3 and lens[-1] > 2.5 * lens[-2] + 15


def validate(items):
    """Returns (report lines, {check: [qids]})."""
    flags = defaultdict(list)
    groups = defaultdict(list)
    dup = [q for q, n in Counter(i["qid"] for i in items).items() if n > 1]
    flags["duplicate-qid"] = dup
    for it in items:
        groups[(it.get("form"), it.get("section"))].append(it)
    lines = [f"# Validation: {len(items)} items, {len(groups)} form-sections", ""]
    for (form, sec), its in sorted(groups.items(), key=lambda kv: str(kv[0])):
        mc = [i for i in its if i.get("choices")]
        nums = sorted(i["q"] for i in its if isinstance(i.get("q"), int))
        gaps = sorted(set(range(1, max(nums) + 1)) - set(nums)) if nums else []
        sizes = Counter(len(i["choices"]) for i in mc)
        usual = sizes.most_common(1)[0][0] if sizes else 0
        sets = Counter("".join(sorted(i["choices"])) for i in mc if len(i["choices"]) == usual)
        main_sets = {s for s, n in sets.items() if n >= 0.15 * max(1, len(mc))}
        par = defaultdict(Counter)
        for i in mc:
            if isinstance(i.get("q"), int):
                par["".join(sorted(i["choices"]))][i["q"] % 2] += 1
        alternates = len(main_sets) == 2 and all(
            min(par[s].values() or [0]) <= 0.1 * sum(par[s].values()) or len(par[s]) == 1
            for s in main_sets)
        for i in its:
            ch, q = i.get("choices") or {}, i["qid"]
            if not i.get("answer"):
                flags["no-answer"].append(q)
            if not ch:
                continue
            if len(ch) != usual:
                flags["choices"].append(q)
            if i.get("answer") and i["answer"] not in ch:
                flags["answer-missing"].append(q)
            if alternates and isinstance(i.get("q"), int) and len(ch) == usual:
                s = "".join(sorted(ch))
                if s in main_sets and par[s].most_common(1)[0][0] != i["q"] % 2:
                    flags["letter-set"].append(q)
            if swallowed(ch):
                flags["swallowed"].append(q)
            texts = [v.strip().lower() for v in ch.values()]
            if len(set(texts)) < len(texts):
                flags["duplicate"].append(q)
            if not (i.get("stem") or "").strip():
                flags["empty-stem"].append(q)
            if i.get("confirmed") is False:
                flags["unconfirmed"].append(q)
        lines.append(
            f"{form} / {sec}: {len(its)} questions, {len(mc)} with choices"
            + (f", numbering gaps {gaps[:12]}" if gaps else "")
            + f", choices per question {dict(sizes)}"
            + (", letters alternate by odd/even" if alternates else ""))
    lines.append("")
    total_mc = sum(1 for i in items if i.get("choices"))
    for name in ("duplicate-qid", "no-answer", "answer-missing", "choices", "letter-set",
                 "swallowed", "duplicate", "empty-stem", "unconfirmed"):
        qs = flags.get(name) or []
        lines.append(f"{name:15} {len(qs):>4}" + (f"  ({len(qs)/max(1,total_mc):.1%} of "
                     f"multiple-choice)  e.g. {', '.join(qs[:6])}" if qs else ""))
    usable = [i for i in items if i.get("choices") and i.get("answer") in i["choices"]]
    lines += ["", f"usable for answer-choice statistics: {len(usable)} of {len(items)}"]
    return lines, dict(flags)


if __name__ == "__main__":
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not paths:
        print(__doc__)
        sys.exit(1)
    allit = [i for p in paths for i in load_items(p)]
    print("\n".join(validate(allit)[0]))
