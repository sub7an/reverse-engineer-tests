#!/usr/bin/env python3
"""
key_structure.py: is the answer key itself predictable?

Answer DNA looks at the choices of one question. This looks at the sequence
of correct positions down a paper. People who assemble keys by hand, and
software that "balances" them, leave two fingerprints that a truly random
key does not have:

  1. Too few repeats. A random key repeats the previous position 1 time in
     k (25% with 4 choices). Editors who dislike "AAA" runs push that down.
  2. Over-balancing. In a random key the count of each position varies from
     paper to paper. A balanced key has counts that are too equal.

Either one means earlier answers carry information about later ones. The
script measures both and prices two fixed strategies for a student who is
sure of the earlier answers (an upper bound: real students are not):

  avoid-repeat   guess anything except the previous question's position
  least-used     guess the position used least so far in this section

and one realistic strategy:

  count-and-fill the student is sure of a random 80% (or 50%) of the answers,
                 counts them, and gives each unsure question the position that
                 is most under-used among the sure ones

Positions, not letters: the answer's rank among its question's sorted choice
labels, so A-D and F-J questions (ACT) are comparable.

Use only on real papers in their printed order. An item bank has no order.

Usage:
  python3 key_structure.py items.json [more.json ...]
"""
import random
import sys
from collections import Counter, defaultdict

from answer_dna import binom_tail, chi2_sf
from ret_common import load_items


def sequences(items):
    """{(form, section): [(q, position, k)] in question order}."""
    groups = defaultdict(list)
    for it in items:
        ch = it.get("choices") or {}
        if it.get("answer") in ch and len(ch) >= 3 and isinstance(it.get("q"), int):
            groups[(it.get("form") or "", it.get("section") or "")].append(
                (it["q"], sorted(ch).index(it["answer"]), len(ch)))
    return {g: sorted(v) for g, v in groups.items()}


def mean_ci(xs):
    n = len(xs)
    if n < 2:
        return 0.0, 0.0
    m = sum(xs) / n
    sd = (sum((x - m) ** 2 for x in xs) / (n - 1)) ** 0.5
    return m, 1.96 * sd / n ** 0.5


def count_and_fill(seqs, k, known, reps=20):
    """Mean gain over a blind guess on the unsure questions, with a 95%
    interval across paper sections. Deterministic (fixed seed)."""
    rng, per_section = random.Random(0), []
    for s in seqs.values():
        s = [x for x in s if x[2] == k]
        if len(s) < 5 * k:
            continue
        accs = []
        for _ in range(reps):
            sure = [rng.random() < known for _ in s]
            used = Counter(pos for (_, pos, _), ok in zip(s, sure) if ok)
            low = min(used[p] for p in range(k))
            cands = [p for p in range(k) if used[p] == low]
            accs += [(1 / len(cands) if pos in cands else 0.0)
                     for (_, pos, _), ok in zip(s, sure) if not ok]
        if accs:
            per_section.append(sum(accs) / len(accs) - 1 / k)
    return mean_ci(per_section)


def analyze(items):
    seqs = sequences(items)
    sizes = Counter(k for s in seqs.values() for _, _, k in s)
    if not sizes:
        return None
    k = sizes.most_common(1)[0][0]
    rep = pairs = 0
    avoid, least = [], []
    chi_total = df = papers = 0
    for s in seqs.values():
        s = [x for x in s if x[2] == k]
        used = Counter()
        for i, (q, pos, _) in enumerate(s):
            if i and s[i - 1][0] == q - 1:  # printed consecutively
                same = pos == s[i - 1][1]
                pairs += 1
                rep += same
                avoid.append(0.0 if same else 1 / (k - 1))
            if i >= 2 * k:  # enough history for "least used" to mean something
                low = min(used[p] for p in range(k))
                cands = [p for p in range(k) if used[p] == low]
                least.append(1 / len(cands) if pos in cands else 0.0)
            used[pos] += 1
        n = len(s)
        if n >= 5 * k:
            papers += 1
            chi_total += sum((used[p] - n / k) ** 2 / (n / k) for p in range(k))
            df += k - 1
    out = {"k": k, "sections": len(seqs), "pairs": pairs, "repeats": rep}
    if pairs:
        out["repeat_p_low"] = binom_tail(rep, pairs, 1 / k, upper=False)
        out["repeat_p_high"] = binom_tail(rep, pairs, 1 / k)
        m, h = mean_ci(avoid)
        out["avoid_gain"] = (m - 1 / k, h)
    if df:
        out["papers"] = papers
        out["dispersion"] = chi_total / df  # 1.0 = random; below 1 = over-balanced
        out["balance_p_low"] = 1 - chi2_sf(chi_total, df)
        out["balance_p_high"] = chi2_sf(chi_total, df)
    if least:
        m, h = mean_ci(least)
        out["least_n"] = len(least)
        out["least_gain"] = (m - 1 / k, h)
    if df:
        out["fill80"] = count_and_fill(seqs, k, 0.8)
        out["fill50"] = count_and_fill(seqs, k, 0.5)
    return out


def tag(p_low, p_high):
    p = min(p_low, p_high)
    return "strong" if p <= 0.01 else "tentative" if p <= 0.05 else "no signal"


def lines(r):
    if not r:
        return ["no usable multiple-choice sequences"]
    k, out = r["k"], []
    out.append(f"# Answer-key structure: {r['sections']} paper sections, {k} choices per question")
    if r.get("pairs"):
        rate = r["repeats"] / r["pairs"]
        out += ["", "## Repeats",
                f"  same position as the previous question: {r['repeats']}/{r['pairs']} "
                f"({rate:.1%}; chance {1/k:.0%}; p_low={r['repeat_p_low']:.3f} "
                f"p_high={r['repeat_p_high']:.3f})  [{tag(r['repeat_p_low'], r['repeat_p_high'])}]"]
        m, h = r["avoid_gain"]
        out.append(f"  avoid-repeat strategy: {m*100:+.1f} pts ±{h*100:.1f} over a blind guess"
                   f"{' *' if m - h > 0 else ''}")
    if "dispersion" in r:
        out += ["", "## Balance",
                f"  dispersion of position counts across {r['papers']} sections: "
                f"{r['dispersion']:.2f} (1.00 = random; below 1 = over-balanced; "
                f"p_low={r['balance_p_low']:.3f} p_high={r['balance_p_high']:.3f})  "
                f"[{tag(r['balance_p_low'], r['balance_p_high'])}]"]
    if "least_gain" in r:
        m, h = r["least_gain"]
        out.append(f"  least-used strategy ({r['least_n']} questions): {m*100:+.1f} pts "
                   f"±{h*100:.1f} over a blind guess{' *' if m - h > 0 else ''}")
    for key, pct in (("fill80", 80), ("fill50", 50)):
        if key in r:
            m, h = r[key]
            out.append(f"  count-and-fill, sure of {pct}% of answers: {m*100:+.1f} pts ±{h*100:.1f} "
                       f"on the unsure questions{' *' if m - h > 0 else ''}")
    out += ["", "  * = the 95% interval excludes 0. avoid-repeat and least-used assume the student is",
            "  sure of every earlier answer (upper bounds). count-and-fill is the realistic one."]
    return out


def main():
    paths = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not paths:
        print(__doc__)
        sys.exit(1)
    print("\n".join(lines(analyze([i for p in paths for i in load_items(p)]))))


if __name__ == "__main__":
    main()
