#!/usr/bin/env python3
"""
difficulty_drivers.py: what separates hard questions from easy ones?

Needs items that carry an OFFICIAL difficulty label (e.g. College Board's
Question Bank: E/M/H). Never use difficulty you inferred yourself here; that
would be circular.

Input JSON: list or {"items": [...]} of:
  {"qid": "...", "block": "skill or question type", "difficulty": "E"|"M"|"H"
   (any ordered labels work; pass --order to set them),
   "passage": "...", "stem": "...", "choices": {"A": "...", ...},
   "answer": "B", "rationale": "...official explanation (optional)..."}

For each block, compares easy vs hard on measurable features and reports the
median per difficulty plus a rank-based effect size (how often a random hard
item scores higher than a random easy item; 0.5 = no difference):
  passage_words        length of the passage
  stem_words           length of the question
  choice_words         average choice length
  distractor_closeness similarity of the closest wrong choice to the answer
                       (word overlap). High = wrong choices look like the answer.
  answer_passage_echo  word overlap between the answer and the passage.
                       Low = the answer paraphrases instead of quoting.
  rationale_words      length of the official explanation (a proxy for the
                       number of reasoning steps)
Also reports the share of each difficulty within each block, so you can say
where the hard questions live.

Usage:
  python3 difficulty_drivers.py items.json
  python3 difficulty_drivers.py items.json --order E,M,H --min-n 15

Reading it: an effect size of 0.65+ (or 0.35-) is a meaningful driver;
0.55-0.65 is mild; near 0.5 is nothing. Report drivers, and say plainly which
features did NOT matter.
"""
import json
import re
import statistics as st
import sys
from collections import defaultdict

STOP = set("the a an of to in and or that this is was were be by for with as on "
           "it its at from their they which who has have had not but also".split())


def words(t):
    return [w for w in re.findall(r"[a-z]+", (t or "").lower()) if w not in STOP]


def jac(a, b):
    a, b = set(words(a)), set(words(b))
    return len(a & b) / max(1, len(a | b))


def feats(it):
    ch = it.get("choices") or {}
    out = {"passage_words": len(words(it.get("passage"))),
           "stem_words": len(words(it.get("stem"))),
           "rationale_words": len(words(it.get("rationale")))}
    if ch and it.get("answer") in ch and len(ch) > 1:
        c = ch[it["answer"]]
        wrong = [v for k, v in ch.items() if k != it["answer"]]
        out["choice_words"] = st.mean(len(words(v)) for v in ch.values())
        out["distractor_closeness"] = max(jac(c, v) for v in wrong)
        out["answer_passage_echo"] = jac(c, it.get("passage", ""))
    return out


def effect(hard, easy):
    """P(random hard > random easy) + 0.5 * P(tie). 0.5 = no difference."""
    if not hard or not easy:
        return None
    gt = sum((h > e) + 0.5 * (h == e) for h in hard for e in easy)
    return gt / (len(hard) * len(easy))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = sys.argv[1:]
    order = ["E", "M", "H"]
    if "--order" in flags:
        order = flags[flags.index("--order") + 1].split(",")
        args = [a for a in args if a != flags[flags.index("--order") + 1]]
    min_n = 15
    if "--min-n" in flags:
        min_n = int(flags[flags.index("--min-n") + 1])
        args = [a for a in args if a != flags[flags.index("--min-n") + 1]]
    if not args:
        print(__doc__)
        sys.exit(1)
    data = json.load(open(args[0]))
    items = data.get("items", data) if isinstance(data, dict) else data
    items = [i for i in items if i.get("difficulty") in order]
    lo, hi = order[0], order[-1]
    blocks = defaultdict(list)
    for i in items:
        blocks[i.get("block", "all")].append(i)
    blocks = dict(sorted(blocks.items(), key=lambda kv: -len(kv[1])))
    blocks = {"ALL": items, **blocks}

    print(f"# Difficulty drivers: {len(items)} items, levels {order}\n")
    print("## Where the hard questions live (share of each level per block)")
    for b, its in blocks.items():
        n = len(its)
        print(f"  {b[:48]:48} n={n:<5}" + "  ".join(
            f"{l}:{sum(i['difficulty'] == l for i in its) / n:4.0%}" for l in order))
    for b, its in blocks.items():
        by = defaultdict(list)
        for i in its:
            by[i["difficulty"]].append(feats(i))
        if len(by[lo]) < min_n or len(by[hi]) < min_n:
            continue
        print(f"\n## {b} (" + ", ".join(f"{l}={len(by[l])}" for l in order) + ")")
        keys = sorted({k for f in by[lo] + by[hi] for k in f})
        for k in keys:
            vals = {l: [f[k] for f in by[l] if k in f] for l in order}
            if not vals[lo] or not vals[hi]:
                continue
            e = effect(vals[hi], vals[lo])
            tag = ("  << DRIVER" if e >= 0.65 or e <= 0.35 else
                   "  < mild" if e >= 0.55 or e <= 0.45 else "")
            meds = "  ".join(f"{l}:{st.median(vals[l]):7.2f}" for l in order if vals[l])
            print(f"  {k:22} {meds}   effect(hard>easy)={e:.2f}{tag}")


if __name__ == "__main__":
    main()
