#!/usr/bin/env python3
"""
report.py: one readable report from parsed items.

answer_dna.py and simulate_score.py print raw numbers for the analyst. This
script turns the same computations into a report a student or tutor can read:
a verdict on each test-taking trick, what the surviving tricks are worth on
papers they were not learned from, a plain-language rulebook, the answer-key
structure, and the coverage footer.

  analyze(items) -> dict     the results as data (the upload app draws this)
  render(dict)   -> str      the same results as Markdown
  build(items)   -> str      render(analyze(items))

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
VERDICT = {"up2": "**Above chance** (strong)", "down2": "**Below chance** (strong)",
           "up1": "Above chance (tentative)", "down1": "Below chance (tentative)",
           "none": "No signal"}


def claim(name, high):
    return CLAIM.get((name, high), f"The choice with the {'highest' if high else 'lowest'} {name}")


def level(k, n, chance, alpha):
    hi, lo = binom_tail(k, n, chance), binom_tail(k, n, chance, upper=False)
    return ("up2" if hi <= alpha else "down2" if lo <= alpha else
            "up1" if hi <= 0.05 else "down1" if lo <= 0.05 else "none")


def analyze(items, alpha=0.01, min_n=15):
    total = len(items)
    usable, forms, how, res = simulate(items, alpha)
    blocks = defaultdict(list)
    for it in usable:
        blocks[it.get("block") or "all"].append(it)
    names = Counter(i.get("exam") or "" for i in usable)
    # Without --exam an adapter falls back to the form id; that is not a name.
    named = [e for e, _ in names.most_common(3) if e and e not in forms]
    d = {"title": ", ".join(named) if named and len(names) <= 3 else "This exam",
         "questions": len(usable), "total": total, "how": how, "forms": len(forms),
         "alpha": alpha, "min_n": min_n, "multi": len(blocks) > 1, "blocks": [],
         "worth": [], "rules": []}

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
                rows.append({"claim": claim(name, high), "k": k, "n": n, "chance": chance,
                             "level": level(k, n, chance, alpha)})
        d["blocks"].append({"name": b, "n": len(its), "rows": rows})
    d["checks"] = checks

    def worth(label, rs):
        (mb, hb), (mt, ht) = ci([r[1] for r in rs]), ci([r[2] for r in rs])
        fired = sum(r[0] for r in rs) / len(rs)
        return {"label": label, "n": len(rs), "fired": fired, "blind": [mb, hb],
                "two": [mt, ht], "established": bool(fired) and (mb - hb > 0 or mt - ht > 0)}

    allr = []
    for b, rs in sorted(res.items(), key=lambda kv: -len(kv[1])):
        allr += rs
        if len(res) > 1:
            d["worth"].append(worth(b, rs))
    d["all"] = worth("All questions", allr) if allr else None
    d["per_form"] = len(allr) / len(forms) if forms else 0

    final = learn(usable, alpha, 20)
    for b in sorted(final):
        for name, _, high, kind, k, n in final[b]:
            chance = 1 / len(blocks[b][0]["choices"])
            if kind == "elim":
                verb = "Cross out" if k / n <= chance / 2 else "Lean away from"
            else:
                verb = "Favour" if k / n >= chance * 1.75 else "Lean toward"
            d["rules"].append({"verb": verb, "claim": claim(name, high), "k": k, "n": n,
                               "where": b if len(blocks) > 1 else ""})

    d["letters"] = letter_line(usable) if usable else ""
    ks = key_analyze(usable) if how.endswith("leave-one-form-out") else None
    d["key"] = ks if ks and ks.get("pairs", 0) >= 100 else None
    d["key_lines"] = key_lines(d["key"])[1:] if d["key"] else []
    d["exams"] = len(names)
    src = Counter(i.get("answer_source") or "official" for i in usable)
    d["official"], d["derived"] = src.get("official", 0), src.get("derived", 0)
    return d


def render(d):
    out = [f"# {d['title']}: what the answer choices give away", "",
           f"{d['questions']} multiple-choice questions from {d['how']}.", "",
           "## 1. Do the tricks work?", "",
           "Each row counts only questions where one choice clearly is the "
           "longest, the only hedged one, and so on. \"Right\" is how often "
           "that choice was the correct answer.", ""]
    for b in d["blocks"]:
        if d["multi"]:
            out += [f"### {b['name']} ({b['n']} questions)", ""]
        if b["rows"]:
            out += ["| Trick | Right | Chance | Verdict |", "|---|---|---|---|"]
            out += [f"| {r['claim']} | {r['k']} of {r['n']} ({r['k']/r['n']:.0%}) | "
                    f"{r['chance']:.0%} | {VERDICT[r['level']]} |" for r in b["rows"]] + [""]
        else:
            out += [f"Too few questions to test (fewer than {d['min_n']} per trick).", ""]

    out += ["## 2. What it is worth", "",
            "Rules were learned on some papers and scored on papers they never "
            "saw. Gain is percentage points of guess accuracy over an even "
            "guess, with a 95% interval.", "",
            "| Question type | Questions | Rule applies | Blind guess | Two choices left | Established |",
            "|---|---|---|---|---|---|"]

    def row(w, label=None):
        label = label or w["label"]
        if not w["fired"]:
            return f"| {label} | {w['n']} | never | 0 | 0 | no rule |"
        (mb, hb), (mt, ht) = w["blind"], w["two"]
        return (f"| {label} | {w['n']} | {w['fired']:.0%} | {mb*100:+.1f} ±{hb*100:.1f} | "
                f"{mt*100:+.1f} ±{ht*100:.1f} | {'yes' if w['established'] else 'no'} |")

    out += [row(w) for w in d["worth"]]
    a = d["all"]
    if a:
        out += [row(a, "**All questions**"), ""]
    if a and a["fired"]:
        pf, (mb, hb), (mt, ht) = d["per_form"], a["blind"], a["two"]
        out += [f"**In marks:** a paper has about {pf:.0f} of these questions. "
                f"A student who must guess on 1 in 5 of them gains about "
                f"**{0.2*pf*mt:+.1f} questions per paper** when stuck between two "
                f"choices (±{0.2*pf*ht:.1f}), and {0.2*pf*mb:+.1f} on blind "
                f"guesses (±{0.2*pf*hb:.1f}). The rules help only on questions "
                "that would otherwise be guessed.", ""]
    else:
        out += ["**In marks:** no rule reached the threshold on any set of training "
                "papers. Gain: 0. On this exam the answer choices give nothing away.", ""]

    out += ["## 3. Rulebook", ""]
    if not d["rules"]:
        out += ["No rule to use.", ""]
    for r in d["rules"]:
        where = f" on {r['where']} questions" if r["where"] else ""
        out.append(f"- **{r['verb']}** {r['claim'][0].lower()}{r['claim'][1:]}{where}: "
                   f"it was right {r['k']} of {r['n']} times ({r['k']/r['n']:.0%}).")
    if d["rules"]:
        out += ["", "Use a rule only as a tie-breaker for a guess, and only if section 2 "
                "marks its question type as established.", ""]

    out += ["## 4. Answer positions", "", "```", d["letters"], "```", ""]

    if d["key"]:
        out += ["## 5. Is the answer key itself predictable?", "",
                "Counts the sequence of correct positions down each paper. A random "
                f"key repeats the previous position 1 time in {d['key']['k']} and "
                "has a dispersion of 1.00; hand-balanced keys repeat less and score "
                "below 1.", "", "```"] + d["key_lines"] + ["```", ""]
        if d["exams"] > 1:
            out += ["Several exams are pooled here; run each exam alone for its own figures.", ""]

    out += ["---", "",
            f"Coverage: {d['questions']} analyzed / {d['total'] - d['questions']} skipped "
            "(no choices, fewer than 3 choices, or answer not among the choices).  ",
            f"Answers: {d['official']} official / {d['derived']} derived.  ",
            f"Checks run: {d['checks']}; expect about {d['checks'] * 0.05:.1f} below p = 0.05 "
            f"by luck. Strong means p ≤ {d['alpha']}.  ",
            f"Held-out split: {d['how']}.", ""]
    return "\n".join(out)


def build(items, alpha=0.01, min_n=15):
    return render(analyze(items, alpha, min_n))


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
