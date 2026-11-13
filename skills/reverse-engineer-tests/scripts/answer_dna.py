#!/usr/bin/env python3
"""
answer_dna.py: test what correct answers have in common, against real items.

Turns test-prep "tricks" into hypotheses and checks them with counts and
binomial p-values, per question block. Works for any multiple-choice test.

Input JSON: a list (or {"items": [...]}) of items:
  {
    "qid": "T10-RW1-Q12",
    "block": "reading",          # any grouping label (question type)
    "passage": "...",            # text the question is about ("" if none)
    "stem": "Which choice ...?", # the question itself
    "choices": {"A": "...", "B": "...", "C": "...", "D": "..."},
    "answer": "B"                # official key letter
  }

Hypotheses tested per block (chance = 1 / number of choices):
  (each "uniquely X" test counts only items where one choice IS uniquely X;
   items with ties are left out, so chance really is 1 / number of choices)
  H-length-long   correct is the uniquely longest choice
  H-length-short  correct is the uniquely shortest choice
  H-copy-high     correct has the uniquely highest share of passage words
  H-copy-low      correct has the uniquely lowest share of passage words
  H-goal-high     correct shares the most words with the stem
  H-goal-low      correct shares the fewest words with the stem
  H-extreme       extreme words (always/never/only/all...) in correct vs wrong,
                  and: when only one choice has one, how often it is correct
  H-hedge         hedge words (may/suggests/some...), the same two ways
  H-letter        answer-letter distribution (chi-square vs uniform)

Usage:
  python3 answer_dna.py items.json                # all blocks
  python3 answer_dna.py items.json --min-n 8      # skip blocks with < 8 items

Reading the output: p_high is the chance of seeing this many hits or more if
there were no pattern; p_low is the chance of this few or fewer. Small p_low on
a "correct is X" line means X is a reliable ELIMINATION signal. Many checks
are run, so expect about 1 in 20 to cross p < 0.05 by luck. Trust p <= 0.01,
treat 0.01-0.05 as tentative, and say so in the report.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from math import comb

STOP = set(("the a an of to in and or that this is was were be by for with as on "
            "it its at from their they which who has have had not but also more "
            "than into these those such can will would").split())
EXTREME = re.compile(r"\b(all|always|never|only|entirely|completely|must|none|every|"
                     r"solely|cannot|proves?|proved|impossible|totally|exclusively|"
                     r"definitively)\b", re.I)
HEDGE = re.compile(r"\b(may|might|could|some|likely|suggests?|possibly|tends?|often|"
                   r"partly|perhaps|probably|potentially)\b", re.I)


def words(t):
    return [w for w in re.findall(r"[a-z]+", (t or "").lower())
            if w not in STOP and len(w) > 2]


def binom_tail(k, n, p, upper=True):
    """P(X >= k) or P(X <= k) for X ~ Binomial(n, p). Terms are computed in
    log space, so blocks of several thousand questions do not overflow."""
    from math import exp, lgamma, log
    rng = range(k, n + 1) if upper else range(0, k + 1)
    lp, lq = log(p), log(1 - p)
    return min(1.0, sum(exp(lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1)
                            + i * lp + (n - i) * lq) for i in rng))


def unique_extreme(scores, ans, high=True):
    if ans not in scores:
        return False
    vals = list(scores.values())
    target = max(vals) if high else min(vals)
    return scores[ans] == target and vals.count(target) == 1


def has_unique(scores, high=True):
    vals = list(scores.values())
    return vals.count(max(vals) if high else min(vals)) == 1


def rank_counts(items, fn):
    """-> {True/False (highest/lowest): (hits, eligible, chance)}.
    An item is eligible for a direction only when one choice is the UNIQUE
    extreme. Items with ties at the extreme are left out: there the correct
    answer cannot be "the longest", so counting them against a 1-in-4 chance
    makes every extreme look rarer than it is (a fake elimination signal)."""
    out = {}
    for high in (True, False):
        k = n = 0
        chance = None
        for it in items:
            ch = it["choices"]
            if it["answer"] not in ch or len(ch) < 3:
                continue
            sc = feature_scores(it, fn)
            if sc is None or not has_unique(sc, high):
                continue
            n += 1
            chance = 1 / len(ch)
            k += unique_extreme(sc, it["answer"], high)
        out[high] = (k, n, chance)
    return out


def rank_lines(items, fn, name):
    out = []
    for high, (k, n, chance) in rank_counts(items, fn).items():
        if not n:
            continue
        label = f"{name}: correct is the unique {'HIGHEST' if high else 'LOWEST'}"
        ph, pl = binom_tail(k, n, chance), binom_tail(k, n, chance, False)
        flag = ""
        if pl <= 0.01:
            flag = "  << ELIMINATION SIGNAL (strong)"
        elif ph <= 0.01:
            flag = "  << PICK SIGNAL (strong)"
        elif pl <= 0.05 or ph <= 0.05:
            flag = "  < tentative"
        out.append(f"  {label:52} {k:>3}/{n:<4} {k/n:5.0%} (chance {chance:.0%}; "
                   f"p_high={ph:.3f} p_low={pl:.3f}){flag}")
    return out


_PASSAGE_WORDS = {}


def passage_words(text):
    """Word set of a passage, cached: long passages are shared by many
    questions and re-tokenizing them per choice made the simulation slow."""
    s = _PASSAGE_WORDS.get(text)
    if s is None:
        if len(_PASSAGE_WORDS) > 4000:
            _PASSAGE_WORDS.clear()
        s = _PASSAGE_WORDS[text] = set(words(text))
    return s


def copy_share(it, text):
    w = words(text)
    p = passage_words(it.get("passage", ""))
    return sum(x in p for x in w) / max(1, len(w))


def goal_overlap(it, text):
    return len(set(words(text)) & set(words(it.get("stem", ""))))


def numeric_value(it, text):
    """The choice as a number, or None. Tests "the answer is a middle value"."""
    s = (text or "").replace(",", "").replace("−", "-").strip().rstrip(".")
    m = re.fullmatch(r"\$?\s*(-?\d+(?:\.\d+)?)\s*(%|°|[a-zA-Z ]{0,20})?", s)
    return float(m.group(1)) if m else None


META_CHOICE = re.compile(r"^\s*(no change|delete the underlined portion|omit the "
                         r"underlined portion|none of the above|all of the above)\W*$",
                         re.I)


def choice_length(it, text):
    """Length of the choice, or None for a placeholder such as "No Change":
    its printed length says nothing about the text it stands for."""
    return None if META_CHOICE.match(text or "") else len(text)


def feature_scores(it, fn):
    """Scores per choice, or None when the item says nothing about this
    feature. Placeholder choices are left out of length comparisons; every
    other feature needs a value for every choice."""
    sc = {k: fn(it, v) for k, v in it["choices"].items()}
    if fn is choice_length:
        sc = {k: v for k, v in sc.items() if v is not None}
        if len(sc) < 2:
            return None
    elif any(v is None for v in sc.values()):
        return None
    return None if len(set(sc.values())) == 1 else sc


def has_extreme(it, text):
    return int(bool(EXTREME.search(text or "")))


def has_hedge(it, text):
    return int(bool(HEDGE.search(text or "")))


# (name, function, item field that must be non-empty for the feature to apply)
# For the two word features, "unique HIGHEST" means the only choice that
# contains such a word; "unique LOWEST" the only choice that does not.
FEATURES = (("length", choice_length, None),
            ("share of passage words", copy_share, "passage"),
            ("overlap with the question", goal_overlap, "stem"),
            ("numeric value", numeric_value, None),
            ("extreme word", has_extreme, None),
            ("hedge word", has_hedge, None))


def rate_line(items, rx, name):
    c = sum(bool(rx.search(it["choices"][it["answer"]])) for it in items)
    w = sum(bool(rx.search(v)) for it in items for k, v in it["choices"].items()
            if k != it["answer"])
    nw = sum(len(it["choices"]) - 1 for it in items)
    return (f"  {name:52} correct {c}/{len(items)} ({c/len(items):.0%}) vs "
            f"wrong {w}/{nw} ({w/max(1, nw):.0%})")


def chi2_sf(x, df):
    """P(chi-square with df degrees of freedom >= x), via the regularized
    upper incomplete gamma function (series / continued fraction)."""
    from math import exp, lgamma, log
    a, x2 = df / 2.0, x / 2.0
    if x2 <= 0:
        return 1.0
    if x2 < a + 1:  # series for the lower incomplete gamma
        term = s = 1.0 / a
        k = a
        while abs(term) > 1e-12 * abs(s):
            k += 1
            term *= x2 / k
            s += term
        return max(0.0, 1.0 - s * exp(-x2 + a * log(x2) - lgamma(a)))
    b, c, d = x2 + 1 - a, 1e300, 1 / (x2 + 1 - a)  # continued fraction
    h = d
    for i in range(1, 300):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        h *= d * c
        if abs(d * c - 1) < 1e-12:
            break
    return min(1.0, exp(-x2 + a * log(x2) - lgamma(a)) * h)


def letter_line(items):
    """Test answer-letter balance. Items are grouped by their set of choice
    letters, because some tests alternate sets (ACT: A-D on odd questions,
    F-J on even), and pooling sets would hide or fake a bias."""
    groups = defaultdict(list)
    for it in items:
        groups["".join(sorted(it["choices"]))].append(it)
    out = []
    for letters, its in sorted(groups.items()):
        if len(its) < 20:
            continue
        c = Counter(it["answer"] for it in its)
        n = len(its)
        exp_ = n / len(letters)
        chi = sum((c[l] - exp_) ** 2 / exp_ for l in letters)
        p = chi2_sf(chi, len(letters) - 1)
        tag = ("  << SIGNIFICANT (strong)" if p <= 0.01 else
               "  < tentative" if p <= 0.05 else "  (not significant)")
        out.append(f"  answer letters [{letters}]: " +
                   " ".join(f"{l}{c[l]}" for l in letters) +
                   f"  chi-square={chi:.2f} p={p:.3f}{tag}")
    return "\n".join(out) or "  answer letters: too few items per letter set"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    min_n = 8
    if "--min-n" in sys.argv:
        min_n = int(sys.argv[sys.argv.index("--min-n") + 1])
    data = json.load(open(args[0]))
    items = data.get("items", data) if isinstance(data, dict) else data
    items = [it for it in items if it.get("answer") in it.get("choices", {})]
    blocks = defaultdict(list)
    for it in items:
        blocks[it.get("block", "all")].append(it)
    checks = 0
    print(f"# Answer DNA: {len(items)} items, {len(blocks)} blocks\n")
    print("## All items")
    print(letter_line(items))
    for b, its in sorted(blocks.items(), key=lambda kv: -len(kv[1])):
        if len(its) < min_n:
            print(f"\n## {b} (n={len(its)}): skipped, fewer than {min_n} items")
            continue
        print(f"\n## {b} (n={len(its)})")
        lines = []
        for name, fn, needs in FEATURES:
            if needs and not any(it.get(needs) for it in its):
                continue
            got = rank_lines(its, fn, name)
            # numeric choices exist in only some blocks; skip thin samples
            if name in ("numeric value", "extreme word", "hedge word") and (not got or int(
                    got[0].split("/")[1].split()[0]) < min_n):
                continue
            lines += got
        checks += len(lines)
        print("\n".join(lines))
        print(rate_line(its, EXTREME, "extreme words"))
        print(rate_line(its, HEDGE, "hedge words"))
    print(f"\n## Multiple comparisons\n  {checks} ranked checks run. "
          f"About {checks * 0.05:.1f} would cross p<0.05 by luck alone. "
          "Report p<=0.01 as strong, 0.01-0.05 as tentative.")


if __name__ == "__main__":
    main()
