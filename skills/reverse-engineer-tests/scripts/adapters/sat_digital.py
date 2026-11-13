"""Digital SAT practice test (College Board "nondigital format" PDFs).

Inputs: the test paper and its answer-explanations file (.pdf or .txt).
Reading & Writing items get full text. Math items are key-only (choices are
often drawn as images, so the PDF text is not reliable); use the cb-qbank
adapter for math choice analysis.
"""
import re

from blocks import sat_rw
from match_items import answer_quoted, match
from ret_common import make_item, to_text

NAME = "sat-digital"
USAGE = "sat-digital <paper.pdf|txt> <answer-explanations.pdf|txt> --form T10"

NOISE = re.compile(r"^(CO ?NTI ?N ?U ?E|Module|\d+|-|Unauthorized copying.*|"
                   r"\.{10,}.*|STOP|.*If you finish before time.*|"
                   r".*check your work on this module only.*|"
                   r".*Do not turn to any other module.*)$")
STEM = re.compile(r"((?:Which|What|Based on|According to|How|The student wants|Why)\b"
                  r"[^?]*\?)\s*$")
STEM_ANY = re.compile(r"((?:Which choice|Which finding|Which quotation|Which statement|"
                      r"What is the main|Based on the text|According to the text|"
                      r"The student wants)[^?]*\?)")


def parse_paper(txt):
    lines = txt.split("\n")
    starts = [i for i, l in enumerate(lines)
              if "important reading and writing skills" in l]
    mstart = next((i for i, l in enumerate(lines) if "important math skills" in l),
                  len(lines))
    out = {}
    for m, (a, b) in enumerate(zip(starts, starts[1:] + [mstart]), 1):
        L = [l.strip() for l in lines[a:b]]
        L = [l for l in L if l and not NOISE.match(l)]
        L = "\n".join(L).split("single best answer.", 1)[-1].split("\n")
        items, cur, ch = [], [], None
        for l in L:
            mm = re.match(r"^([A-D])\)\s*(.*)$", l)
            if mm:
                ch = mm.group(1)
                if ch == "A":
                    items.append({"body": cur, "choices": {}})
                    cur = []
                if items:
                    items[-1]["choices"][ch] = mm.group(2)
                continue
            if items and (ch and ch != "D" or (ch == "D" and not items[-1]["choices"].get("D"))):
                items[-1]["choices"][ch] += " " + l
                continue
            if (ch == "D" and items and not cur and re.match(r"^[a-z(,;:]", l)
                    and not re.search(r"[.?!”\"]$", items[-1]["choices"]["D"])):
                items[-1]["choices"]["D"] += " " + l
                continue
            ch = None
            cur.append(l)
        for k, it in enumerate(items, 1):
            body = " ".join(it["body"])
            sm = STEM.search(body)
            if not sm:  # scrambled column order: the question is not last
                found = list(STEM_ANY.finditer(body))
                sm = found[-1] if found else None
            out[f"RW{m}-Q{k}"] = {
                "passage": (body[:sm.start()] + " " + body[sm.end():]).strip() if sm else body,
                "stem": sm.group(1) if sm else "",
                "choices": {c: v.strip() for c, v in it["choices"].items()}}
    return out


def parse_explanations(txt):
    txt = re.sub(r"\n\s*\d*\s*SAT PRACTICE TEST #[0-9]+ ANSWER EXPLANATIONS[^\n]*", "\n", txt)
    txt = re.sub(r"\n\s*SAT ANSWER EXPLANATIONS n [^\n]*", "\n", txt)
    parts = re.split(r"\n\s*(Reading and Writing|Math)\s*\n\s*Module\s+(\d)\s*\n", txt)
    out = []
    for i in range(1, len(parts) - 2, 3):
        sec, mod, body = parts[i], parts[i + 1], parts[i + 2]
        tag = ("RW" if sec.startswith("Reading") else "M") + mod
        qs = re.split(r"\n\s*QUESTION\s+(\d+)[^\n]*\n", body)
        for j in range(1, len(qs) - 1, 2):
            b = re.sub(r"\s+", " ", qs[j + 1]).strip()
            m = re.search(r"Choice ([A-D]) is (?:the best answer|correct)|"
                          r"The correct answer is (.+?)\.(?:\s|$)", b)
            ans = (m.group(1) or m.group(2)).strip() if m else None
            out.append({"qid": f"{tag}-Q{qs[j]}", "section": tag, "answer": ans, "expl": b})
    return out


def _norm(s):
    return re.sub(r"[^a-z ]", "", (s or "").lower()).strip()


def repair_by_quote(matched, key):
    """When an explanation opens by quoting the correct choice and the paired
    item's choice text differs, swap content with the item in the same section
    whose choice does match. Catches near-identical items the matcher confused
    (transitions share almost all their words)."""
    kq = {k["qid"]: k for k in key}
    by = {m["qid"]: m for m in matched}
    swaps = []
    for q, i in by.items():
        m = re.match(r"Choice [A-D] is the best answer\. “([^”]+)”", kq[q]["expl"])
        if not m or _norm(i["choices"].get(i["answer"])) == _norm(m.group(1)):
            continue
        for q2, j in by.items():
            if (q2 != q and q2.rsplit("-Q", 1)[0] == q.rsplit("-Q", 1)[0]
                    and _norm(j["choices"].get(i["answer"])) == _norm(m.group(1))):
                for f in ("passage", "stem", "choices", "src_item"):
                    i[f], j[f] = j[f], i[f]
                swaps.append(f"{q}<->{q2}")
                break
    for q, i in by.items():
        i["answer_confirmed"] = answer_quoted(i["choices"].get(i["answer"], ""), kq[q]["expl"])
    return swaps


def block_from_explanation(expl):
    """Fallback when the question text could not be recovered from the page.
    Less accurate than the stem (see blocks.py); used only for those items."""
    e = expl[:400].lower()
    if "convention" in e:
        return "grammar", None
    if "transition" in e:
        return "transition", "transitions"
    if "in this context" in e:
        return "vocab", "words in context"
    if "the student" in e or "the sentence" in e:
        return "notes-synthesis", "rhetorical synthesis"
    return "reading", None


def parse(inputs, form, opts):
    if len(inputs) < 2:
        raise SystemExit("usage: " + USAGE)
    raw = parse_paper(to_text(inputs[0]))
    key = parse_explanations(to_text(inputs[1]))
    rw_key = [k for k in key if k["section"].startswith("RW") and k["answer"]]
    matched, reordered, _ = match(raw, rw_key)
    swaps = repair_by_quote(matched, rw_key)
    opts.setdefault("log", []).append(
        f"{form}: RW parsed {len(raw)}, matched {len(matched)}, reordered {reordered}, "
        f"swapped {len(swaps)}, unconfirmed "
        f"{sum(not m['answer_confirmed'] for m in matched)}")
    items = []
    expl = {k["qid"]: k["expl"] for k in rw_key}
    for m in matched:
        sec, q = m["qid"].rsplit("-Q", 1)
        block, skill = (sat_rw(m["stem"], m["choices"]) if m["stem"] else
                        block_from_explanation(expl[m["qid"]]))
        items.append(make_item(
            qid=f"{form}-{m['qid']}", exam="SAT", form=form, section=sec, q=int(q),
            block=block, skill=skill, passage=m["passage"], stem=m["stem"],
            choices=m["choices"], answer=m["answer"], confirmed=m["answer_confirmed"]))
    for k in key:
        if k["section"].startswith("M") and k["answer"]:
            sec, q = k["qid"].rsplit("-Q", 1)
            items.append(make_item(
                qid=f"{form}-{k['qid']}", exam="SAT", form=form, section=sec, q=int(q),
                block="math-mcq" if k["answer"] in "ABCD" else "math-grid-in",
                answer=k["answer"]))
    return sorted(items, key=lambda i: (i["section"], i["q"]))
