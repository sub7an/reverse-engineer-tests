#!/usr/bin/env python3
"""
match_items.py: pair parsed question items with their answer key/explanations.

Why: two-column PDF pages often come out of text extraction in the wrong
order, so "the 4th item parsed" is not always question 4. Never trust order
alone. This script matches by content and confirms each pair by checking that
the key letter's choice text actually appears in that question's explanation.

Inputs:
  items.json  {"<section>-Q<n>": {"passage": "...", "stem": "...",
                                    "choices": {"A": "...", ...}}, ...}
  key.json    [{"qid": "<section>-Q<n>", "answer": "C", "expl": "..."}, ...]
              ("expl" may be empty if you only have a key; matching then
               falls back to order and nothing is confirmed)
  --records records.json   optional; Phase-2 records with qid + archetype or
                           block, used to fill each item's "block"
  --prefix T10-            optional; prepended to qids in the output

Output (stdout): answer_dna.py-ready JSON {"items": [...]} plus a summary on
stderr: matched, reordered, confirmed, and the unconfirmed qids to check by
hand. Sections are matched separately (items only match within a section).

Usage:
  python3 match_items.py items.json key.json --records records.json \
      --prefix T10- > matched.json
"""
import json
import re
import sys

STOP = set(("which choice completes text logical precise phrase word because "
            "answer would based passage following student").split())


def words(t):
    return {w for w in re.findall(r"[a-z]{5,}", (t or "").lower())} - STOP


def answer_quoted(choice_text, expl):
    k = re.findall(r"[a-z]{4,}", (choice_text or "").lower())[:4]
    return bool(k) and sum(w in expl.lower() for w in k) >= max(1, len(k) // 2)


def main():
    flags = sys.argv[1:]
    def opt(name):
        return flags[flags.index(name) + 1] if name in flags else None
    rec_path, prefix = opt("--records"), opt("--prefix") or ""
    skip = {rec_path, opt("--prefix")}
    args = [a for a in flags if not a.startswith("--") and a not in skip]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    items = json.load(open(args[0]))
    key = json.load(open(args[1]))
    key = key.get("questions", key) if isinstance(key, dict) else key
    blocks = {}
    if rec_path:
        recs = json.load(open(rec_path))
        recs = recs.get("questions", recs) if isinstance(recs, dict) else recs
        blocks = {r["qid"]: r.get("block") or r.get("archetype") for r in recs}
    out, reordered, unconfirmed = match(items, key, blocks, prefix)
    json.dump({"items": out}, sys.stdout, indent=1)
    print(f"matched {len(out)}, reordered {reordered}, confirmed "
          f"{len(out) - len(unconfirmed)}/{len(out)}", file=sys.stderr)
    if unconfirmed:
        print("check by hand (answer text not found in explanation): " +
              ", ".join(unconfirmed), file=sys.stderr)


def match(items, key, blocks=None, prefix=""):
    """Pair items with key entries by content. Returns (matched items,
    number reordered, unconfirmed qids). Importable by adapters."""
    blocks = blocks or {}
    kq = {k["qid"]: k for k in key}
    sec = lambda q: q.rsplit("-Q", 1)[0]
    out, reordered, unconfirmed = [], 0, []
    for s in sorted({sec(q) for q in kq}):
        iq = [q for q in items if sec(q) == s]
        eq = [q for q in kq if sec(q) == s]
        iw = {q: words(items[q].get("passage", "") + " " +
                       " ".join(items[q].get("choices", {}).values())) for q in iq}
        ew = {q: words(kq[q].get("expl", "")) for q in eq}
        def score(i, e):
            sc = len(iw[i] & ew[e]) / (1 + len(iw[i])) ** 0.5
            ch = items[i].get("choices", {}).get(kq[e]["answer"], "")
            sc += 1.0 if kq[e].get("expl") and answer_quoted(ch, kq[e]["expl"]) else 0
            return sc + (0.3 if i == e else 0)
        pairs = sorted(((score(i, e), i, e) for i in iq for e in eq), reverse=True)
        used_i, used_e = set(), set()
        for sc, i, e in pairs:
            if i in used_i or e in used_e:
                continue
            used_i.add(i)
            used_e.add(e)
            it = items[i]
            ok = bool(kq[e].get("expl")) and answer_quoted(
                it.get("choices", {}).get(kq[e]["answer"], ""), kq[e]["expl"])
            reordered += i != e
            if not ok:
                unconfirmed.append(prefix + e)
            out.append({"qid": prefix + e, "src_item": i, "match_score": round(sc, 2),
                        "answer_confirmed": ok,
                        "block": blocks.get(prefix + e) or blocks.get(e) or s,
                        "passage": it.get("passage", ""), "stem": it.get("stem", ""),
                        "choices": it.get("choices", {}), "answer": kq[e]["answer"]})
    return out, reordered, unconfirmed


if __name__ == "__main__":
    main()
