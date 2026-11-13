#!/usr/bin/env python3
"""
simulate_score.py: do the answer-choice signals actually earn marks?

Answer DNA finds patterns. This script measures what they are worth, honestly:
rules are learned on some test forms and scored on forms they never saw.

Method (leave-one-form-out):
  1. Hold out one form. On the remaining forms, for each block and feature
     (length, share of passage words, overlap with the question, numeric
     value), take the questions where one choice is the unique highest (or
     lowest) and count how often that choice is correct. Binomial p_low <= alpha makes an ELIMINATE rule ("cross out
     that choice"); p_high <= alpha makes a PICK rule.
  2. Apply those rules to the held-out form in two situations:
       blind    the student knows nothing and must guess among all choices
       two-left the student has narrowed to the right answer plus one wrong
                choice (each wrong choice equally likely to be the survivor)
     Without rules the student guesses evenly. With rules they drop
     eliminated choices and take a picked one.
  3. Repeat for every form. Report the gain in guess accuracy with a 95%
     confidence interval, per block and overall, and convert it to extra
     questions right per form for students who guess on 10/20/30% of items.

With a single form (or an item bank), forms are replaced by 5 stable folds of
the question id.

Usage:
  python3 simulate_score.py items.json [--alpha 0.01] [--min-n 20]

Reading it: a gain whose interval includes 0 is not established. Gains apply
only to questions the student would otherwise guess; they are not a substitute
for knowing the material.
"""
import sys
import zlib
from collections import defaultdict

from answer_dna import FEATURES, binom_tail, feature_scores, rank_counts
from ret_common import load_items


scores = feature_scores


def extreme_choice(sc, high):
    vals = list(sc.values())
    t = max(vals) if high else min(vals)
    return next(k for k, v in sc.items() if v == t) if vals.count(t) == 1 else None


def learn(train, alpha, min_n):
    """-> {block: [(feature name, fn, high?, 'elim'|'pick', k, n)]}"""
    by = defaultdict(list)
    for it in train:
        by[it.get("block") or "all"].append(it)
    rules = defaultdict(list)
    for b_, its in by.items():
        for name, fn, needs in FEATURES:
            if needs and not any(it.get(needs) for it in its):
                continue
            for high, (k, n, chance) in rank_counts(its, fn).items():
                if n < min_n:
                    continue
                if binom_tail(k, n, chance, upper=False) <= alpha:
                    rules[b_].append((name, fn, high, "elim", k, n))
                elif binom_tail(k, n, chance) <= alpha:
                    rules[b_].append((name, fn, high, "pick", k, n))
    return rules


def apply(it, rules):
    """-> (fired?, blind accuracy, two-left accuracy) for one held-out item."""
    ch, ans = list(it["choices"]), it["answer"]
    elim, picks = set(), set()
    for name, fn, high, kind, _, _ in rules:
        sc = scores(it, fn)
        if not sc:
            continue
        c = extreme_choice(sc, high)
        if c:
            (elim if kind == "elim" else picks).add(c)
    pick = next(iter(picks)) if len(picks) == 1 else None
    if pick in elim:
        pick = None
    if not elim and not pick:
        return False, 1 / len(ch), 0.5
    if pick:
        blind = 1.0 if pick == ans else 0.0
    else:
        cand = [c for c in ch if c not in elim] or ch
        blind = (1 / len(cand)) if ans in cand else 0.0
    two = 0.0
    wrong = [c for c in ch if c != ans]
    for w in wrong:
        if pick in (ans, w):
            two += pick == ans
        elif (ans in elim) != (w in elim):
            two += w in elim
        else:
            two += 0.5
    return True, blind, two / len(wrong)


def ci(deltas):
    n = len(deltas)
    if n < 2:
        return 0.0, 0.0
    m = sum(deltas) / n
    sd = (sum((d - m) ** 2 for d in deltas) / (n - 1)) ** 0.5
    return m, 1.96 * sd / n ** 0.5


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    opt = lambda name, d: (float(sys.argv[sys.argv.index(name) + 1])
                           if name in sys.argv else d)
    alpha, min_n = opt("--alpha", 0.01), int(opt("--min-n", 20))
    items = [i for p in args for i in load_items(p)]
    items, forms, how, res = simulate(items, alpha, min_n)
    report(items, forms, how, res, alpha, min_n)


def simulate(items, alpha=0.01, min_n=20):
    """Leave-one-form-out. -> (usable items, forms, description of the split,
    {block: [(rule fired?, blind gain, two-left gain)]})."""
    items = [i for i in items
             if i.get("choices") and i.get("answer") in i["choices"] and len(i["choices"]) >= 3]
    forms = sorted({i.get("form") or "" for i in items})
    if len(forms) < 2:
        for i in items:
            i["form"] = f"fold{zlib.crc32(i['qid'].encode()) % 5}"
        forms = sorted({i["form"] for i in items})
        how = "5 folds of the question id (fewer than 2 forms)"
    else:
        how = f"{len(forms)} forms, leave-one-form-out"
    res = defaultdict(list)  # block -> [(fired, blind gain, two gain)]
    for f in forms:
        rules = learn([i for i in items if i["form"] != f], alpha, min_n)
        for it in (i for i in items if i["form"] == f):
            b = it.get("block") or "all"
            fired, blind, two = apply(it, rules.get(b, []))
            res[b].append((fired, blind - 1 / len(it["choices"]), two - 0.5))
    return items, forms, how, res


def report(items, forms, how, res, alpha, min_n):
    print(f"# Score simulation: {len(items)} items, {how}")
    print(f"# rules need p <= {alpha} on at least {min_n} training items\n")
    print(f"{'block':30} {'n':>5} {'rule fires':>10}  {'blind guess gain':>22}  "
          f"{'two-left gain':>22}")
    allr = []
    for b, rs in sorted(res.items(), key=lambda kv: -len(kv[1])):
        allr += rs
        fired = sum(r[0] for r in rs)
        (mb, hb), (mt, ht) = ci([r[1] for r in rs]), ci([r[2] for r in rs])
        mark = lambda m, h: " *" if m - h > 0 else ""
        print(f"{b[:30]:30} {len(rs):>5} {fired/len(rs):>10.0%}  "
              f"{mb*100:>+7.1f} pts ±{hb*100:4.1f}{mark(mb, hb):2}       "
              f"{mt*100:>+7.1f} pts ±{ht*100:4.1f}{mark(mt, ht):2}")
    (mb, hb), (mt, ht) = ci([r[1] for r in allr]), ci([r[2] for r in allr])
    print(f"{'ALL':30} {len(allr):>5} {sum(r[0] for r in allr)/len(allr):>10.0%}  "
          f"{mb*100:>+7.1f} pts ±{hb*100:4.1f}{' *' if mb-hb>0 else '  '}       "
          f"{mt*100:>+7.1f} pts ±{ht*100:4.1f}{' *' if mt-ht>0 else '  '}")
    print("\n  gain = percentage points of guess accuracy over even guessing "
          "(blind: 1/choices; two-left: 50%).\n  * = the 95% interval excludes 0.")
    per_form = len(allr) / len(forms)
    print(f"\n## Extra questions right per form (about {per_form:.0f} multiple-choice "
          "questions analyzed per form)")
    for g in (0.1, 0.2, 0.3):
        print(f"  guessing on {g:.0%} of questions: blind {g*per_form*mb:+.2f} "
              f"(±{g*per_form*hb:.2f}), two-left {g*per_form*mt:+.2f} (±{g*per_form*ht:.2f})")
    print("\n## Rulebook learned from all forms (use these; the gains above came from "
          "rules learned without the scored form)")
    final = learn(items, alpha, min_n)
    if not final:
        print("  no rule reached the threshold")
    for b in sorted(final):
        for name, _, high, kind, k, n in final[b]:
            what = "ELIMINATE" if kind == "elim" else "PICK"
            print(f"  {b[:28]:28} {what:9} the choice with the "
                  f"{'highest' if high else 'lowest'} {name}: correct {k}/{n} ({k/n:.0%})")


if __name__ == "__main__":
    main()
