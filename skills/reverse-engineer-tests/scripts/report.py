#!/usr/bin/env python3
"""
report.py: one readable Markdown report from parsed items.

answer_dna.py and simulate_score.py print raw numbers for the analyst. This
script turns the same computations into a report a student or tutor can read:
a verdict on each test-taking trick, what the surviving tricks are worth on
papers they were not learned from, a plain-language rulebook, and the
coverage footer.

Usage:
  python3 report.py items.json [more.json ...] [--min-n 15] [--alpha 0.01] [-o report.md]

A row needs --min-n eligible questions (questions where one choice is the
unique extreme). Verdicts: p <= alpha is strong, p <= 0.05 tentative.
"""
import sys
from collections import Counter, defaultdict

from answer_dna import FEATURES, binom_tail, letter_line, rank_counts
from key_structure import analyze as key_analyze
from key_structure import lines as key_lines
from ret_common import load_items
from simulate_score import ci, learn, simulate

CLAIM = {
    ("length", True): "The longest choice",
    ("length", False): "The shortest choice",
    ("share of passage words", True): "The choice using the most passage words",
    ("share of passage words", False): "The choice using the fewest passage words",
    ("overlap with the question", True): "The choice echoing the question most",
    ("overlap with the question", False): "The choice echoing the question least",
    ("numeric value", True): "The largest number",
    ("numeric value", False): "The smallest number",
    ("extreme word", True): "The only choice with an extreme word (always, never, only)",
    ("extreme word", False): "The only choice without an extreme word",
    ("hedge word", True): "The only choice with a hedge word (may, some, often)",
    ("hedge word", False): "The only choice without a hedge word",
    ("similarity to the other choices", True): "The choice most like the other choices",
    ("similarity to the other choices", False): "The odd one out (least like the other choices)",
}


def claim(name, high):
    return CLAIM.get((name, high), f"The choice with the {'highest' if high else 'lowest'} {name}")


def verdict(k, n, chance, alpha):
    hi, lo = binom_tail(k, n, chance), binom_tail(k, n, chance, upper=False)
    if hi <= alpha:
        return "**Above chance** (strong)"
    if lo <= alpha:
        return "**Below chance** (strong)"
    if hi <= 0.05:
        return "Above chance (tentative)"
    if lo <= 0.05:
        return "Below chance (tentative)"
    return "No signal"


def build(items, alpha=0.01, min_n=15):
    total = len(items)
    usable, forms, how, res = simulate(items, alpha)
    blocks = defaultdict(list)
    for it in usable:
        blocks[it.get("block") or "all"].append(it)
    names = Counter(i.get("exam") or "" for i in usable)
    # Without --exam an adapter falls back to the form id; that is not a name.
    named = [e for e, _ in names.most_common(3) if e and e not in forms]
    exams = ", ".join(named) if named and len(names) <= 3 else "This exam"
    out = [f"# {exams}: what the answer choices give away", "",
           f"{len(usable)} multiple-choice questions from {how}.", ""]

    # 1. verdicts
    out += ["## 1. Do the tricks work?", "",
            "Each row counts only questions where one choice clearly is the "
            "longest, the only hedged one, and so on. \"Right\" is how often "
            "that choice was the correct answer.", ""]
    checks = 0
    for b, its in sorted(blocks.items(), key=lambda kv: -len(kv[1])):
        rows = []
        for name, fn, needs in FEATURES:
            if needs and not any(it.get(needs) for it in its):
                continue
            for high, (k, n, chance) in rank_counts(its, fn).items():
                if n < min_n:
                    continue
                checks += 1
                rows.append(f"| {claim(name, high)} | {k} of {n} ({k/n:.0%}) | "
                            f"{chance:.0%} | {verdict(k, n, chance, alpha)} |")
        if len(blocks) > 1:
            out += [f"### {b} ({len(its)} questions)", ""]
        if rows:
            out += ["| Trick | Right | Chance | Verdict |", "|---|---|---|---|"] + rows + [""]
        else:
            out += [f"Too few questions to test (fewer than {min_n} per trick).", ""]

    # 2. worth
    out += ["## 2. What it is worth", "",
            "Rules were learned on some papers and scored on papers they never "
            "saw. Gain is percentage points of guess accuracy over an even "
            "guess, with a 95% interval.", "",
            "| Question type | Questions | Rule applies | Blind guess | Two choices left | Established |",
            "|---|---|---|---|---|---|"]
    allr = []

    def row(label, rs):
        (mb, hb), (mt, ht) = ci([r[1] for r in rs]), ci([r[2] for r in rs])
        fired = sum(r[0] for r in rs) / len(rs)
        if not fired:
            return f"| {label} | {len(rs)} | never | 0 | 0 | no rule |", (mb, hb, mt, ht)
        est = "yes" if mb - hb > 0 or mt - ht > 0 else "no"
        return (f"| {label} | {len(rs)} | {fired:.0%} | {mb*100:+.1f} ±{hb*100:.1f} | "
                f"{mt*100:+.1f} ±{ht*100:.1f} | {est} |"), (mb, hb, mt, ht)

    for b, rs in sorted(res.items(), key=lambda kv: -len(kv[1])):
        allr += rs
        if len(res) > 1:
            out.append(row(b, rs)[0])
    line, (mb, hb, mt, ht) = row("**All questions**", allr)
    out += [line, ""]
    per_form = len(allr) / len(forms)
    if any(r[0] for r in allr):
        out += [f"**In marks:** a paper has about {per_form:.0f} of these questions. "
                f"A student who must guess on 1 in 5 of them gains about "
                f"**{0.2*per_form*mt:+.1f} questions per paper** when stuck between two "
                f"choices (±{0.2*per_form*ht:.1f}), and {0.2*per_form*mb:+.1f} on blind "
                f"guesses (±{0.2*per_form*hb:.1f}). The rules help only on questions "
                "that would otherwise be guessed.", ""]
    else:
        out += ["**In marks:** no rule reached the threshold on any set of training "
                "papers. Gain: 0. On this exam the answer choices give nothing away.", ""]

    # 3. rulebook
    out += ["## 3. Rulebook", ""]
    final = learn(usable, alpha, 20)
    if not final:
        out += ["No rule to use.", ""]
    for b in sorted(final):
        for name, _, high, kind, k, n in final[b]:
            where = f" on {b} questions" if len(blocks) > 1 else ""
            chance = 1 / len(blocks[b][0]["choices"])
            if kind == "elim":
                verb = "Cross out" if k / n <= chance / 2 else "Lean away from"
            else:
                verb = "Favour" if k / n >= chance * 1.75 else "Lean toward"
            out.append(f"- **{verb}** {claim(name, high)[0].lower()}{claim(name, high)[1:]}"
                       f"{where}: it was right {k} of {n} times ({k/n:.0%}).")
    if final:
        out += ["", "Use a rule only as a tie-breaker for a guess, and only if section 2 "
                "marks its question type as established.", ""]

    # 4. letters
    out += ["## 4. Answer positions", "", "```", letter_line(usable), "```", ""]

    # 5. key structure
    exams_n = len({i.get("exam") for i in usable})
    ks = key_analyze(usable) if how.endswith("leave-one-form-out") else None
    if ks and ks.get("pairs", 0) >= 100:
        out += ["## 5. Is the answer key itself predictable?", "",
                "Counts the sequence of correct positions down each paper. A random "
                "key repeats the previous position 1 time in " + str(ks["k"]) + " and "
                "has a dispersion of 1.00; hand-balanced keys repeat less and score "
                "below 1.", "", "```"] + key_lines(ks)[1:] + ["```", ""]
        if exams_n > 1:
            out += ["Several exams are pooled here; run each exam alone for its own figures.", ""]

    src = Counter(i.get("answer_source") or "official" for i in usable)
    out += ["---", "",
            f"Coverage: {len(usable)} analyzed / {total - len(usable)} skipped "
            "(no choices, fewer than 3 choices, or answer not among the choices).  ",
            f"Answers: {src.get('official', 0)} official / {src.get('derived', 0)} derived.  ",
            f"Checks run: {checks}; expect about {checks * 0.05:.1f} below p = 0.05 by luck. "
            f"Strong means p ≤ {alpha}.  ",
            f"Held-out split: {how}.", ""]
    return "\n".join(out)


def main():
    argv = sys.argv[1:]
    val = lambda name, d: argv[argv.index(name) + 1] if name in argv else d
    skip = {i + 1 for i, a in enumerate(argv) if a in ("--min-n", "--alpha", "-o")}
    paths = [a for i, a in enumerate(argv) if not a.startswith("-") and i not in skip]
    if not paths:
        print(__doc__)
        sys.exit(1)
    text = build([i for p in paths for i in load_items(p)],
                 float(val("--alpha", 0.01)), int(val("--min-n", 15)))
    if "-o" in argv:
        open(val("-o", None), "w").write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
