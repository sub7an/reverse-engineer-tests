"""Enhanced ACT (2025+) practice test booklet, the single PDF from act.org that
holds the four tests plus the scoring keys.

Inputs: the booklet .pdf. (Or two text files: plain `pdftotext` output, then
`pdftotext -layout` output; the keys need the layout version.)

Answers, scored/unscored flags and reporting categories come from ACT's own
scoring-key tables. English questions are typed from their stems.
"""
import re

from blocks import act_english
from ret_common import make_item, to_text

NAME = "act-enhanced"
USAGE = "act-enhanced <booklet.pdf> --form ACT1   (or <plain.txt> <layout.txt>)"

SECS = [("ENGLISH TEST", "English", 50), ("MATHEMATICS TEST", "Mathematics", 45),
        ("READING TEST", "Reading", 36), ("SCIENCE TEST", "Science", 40)]
CODES = {"English": "POW|KLA|CSE", "Mathematics": "IES|MOD|A|F|G|N|S",
         "Reading": "KID|CS|IKI", "Science": "IOD|SIN|EMI"}
NOISE = re.compile(r"^(\d\.\s+(Illustrative figures|Geometric figures|The word .line.|"
                   r"The word .average.).*|GO ON TO THE NEXT PAGE\.?|©.*|STOP!?.*|\d|"
                   r"END OF TEST.*|DO NOT RETURN.*)$")


def tag(form, sec, q):
    return f"{form}-{sec[:4].upper()}-Q{q}"


def parse_items(txt, form):
    lines = [l.rstrip() for l in txt.split("\n")]
    heads = [next(i for i, l in enumerate(lines) if l.strip() == h and i > 200)
             for h, _, _ in SECS]
    stop = next((i for i, l in enumerate(lines)
                 if "Scoring Key" in l and i > heads[-1]), len(lines))
    items = {}
    for k, (_, sec, n_q) in enumerate(SECS):
        L = lines[heads[k] + 1:(heads[k + 1] if k + 1 < len(SECS) else stop)]
        cur, passage, mode, seen, last = None, [], "text", set(), None
        for l in L:
            s = l.strip()
            if not s:
                # A blank line after the 4th choice ends the question. Without
                # this, passage text printed beside the questions (English) is
                # glued onto the last choice and corrupts length statistics.
                if cur and mode == "choice" and len(cur["choices"]) == 4:
                    mode = "text"
                continue
            if NOISE.match(s):
                continue
            if re.match(r"^PASSAGE [IVX]+", s):
                passage, mode = [], "text"
                continue
            m = re.match(r"^(\d{1,2})\.\s+(.*)$", s)
            if (m and int(m.group(1)) not in seen and 1 <= int(m.group(1)) <= n_q
                    and int(m.group(1)) - max(seen | {0}) <= 10):
                q = int(m.group(1))
                seen.add(q)
                cur = {"q": q, "section": sec, "stem": m.group(2), "choices": {},
                       "passage": " ".join(passage)}
                items[tag(form, sec, q)] = cur
                mode = "stem"
                continue
            c = re.match(r"^([A-DF-J])\.\s*(.*)$", s)
            if c and cur and mode in ("stem", "choice") and len(cur["choices"]) < 4:
                cur["choices"][c.group(1)] = c.group(2)
                last, mode = c.group(1), "choice"
                continue
            if mode == "stem" and cur:
                cur["stem"] += " " + s
                continue
            if mode == "choice" and cur and (len(cur["choices"]) < 4 or
                                             (s[0].islower() and len(s) < 60)):
                cur["choices"][last] += " " + s
                continue
            mode = "text"
            passage.append(s)
    return items


def parse_keys(layout, form):
    lines = layout.split("\n")
    secs = [(i, m.group(1)) for i, l in enumerate(lines)
            if (m := re.match(r"\s*(English|Mathematics|Reading|Science) Scoring Key", l))]
    out = {}
    for k, (start, sec) in enumerate(secs):
        end = secs[k + 1][0] if k + 1 < len(secs) else start + 130
        cur = None
        for l in lines[start + 1:end]:
            left = l[:56]  # the conversion table sits to the right of column 56
            m = re.match(r"\s{0,6}(\d{1,2})(?=\s|$)(.*)$", l[:44])
            if m and 1 <= int(m.group(1)) <= 60 and not re.match(r"\s*\d", m.group(2)):
                q = int(m.group(1))
                rest, off = left[m.end(1):], m.end(1)
                if out.get(tag(form, sec, q), {}).get("answer"):
                    cur = None
                    continue
                cur = {"q": q, "section": sec, "answer": None, "scored": True,
                       "category": None}
                out[tag(form, sec, q)] = cur
            elif (cur is not None and re.match(r"\s+[A-K]\b", left)
                  and len(left) - len(left.lstrip()) < 18):
                rest, off = left, 0
            elif (cur is not None and left.strip()
                  and re.match(r"\s+([A-Z]{1,4}|Not Scored)\s*$", left)):
                rest, off = left, 0
            else:
                continue
            a = re.match(r"\s*([A-K])\b", rest)
            if a and cur["answer"] is None and off + a.start(1) < 18:
                cur["answer"] = a.group(1)
                rest = rest[a.end():]
            if "—" in rest:
                cur["scored"] = False
            if "Not Scored" in rest:
                cur["scored"] = False
                rest = rest.replace("Not Scored", "")
            c = re.search(rf"(?<![(\w])({CODES[sec]})(?![)\w])", rest)
            if c and cur["category"] is None:
                cur["category"] = c.group(1)
    return out


def parse(inputs, form, opts):
    if not inputs:
        raise SystemExit("usage: " + USAGE)
    if len(inputs) == 1 and not inputs[0].lower().endswith(".pdf"):
        raise SystemExit("act-enhanced needs the PDF, or plain text plus layout text")
    plain = to_text(inputs[0])
    layout = to_text(inputs[1] if len(inputs) > 1 else inputs[0], layout=True)
    raw, keys = parse_items(plain, form), parse_keys(layout, form)
    log = opts.setdefault("log", [])
    items = []
    for _, sec, n_q in SECS:
        got = [q for q in range(1, n_q + 1) if tag(form, sec, q) in raw]
        keyed = [q for q in range(1, n_q + 1) if keys.get(tag(form, sec, q), {}).get("answer")]
        parity = [q for q in keyed
                  if (keys[tag(form, sec, q)]["answer"] in "ABCD") != (q % 2 == 1)]
        log.append(f"{form} {sec}: items {len(got)}/{n_q}, keys {len(keyed)}/{n_q}, "
                   f"unscored {sum(not keys[tag(form, sec, q)]['scored'] for q in keyed)}, "
                   f"key letters with wrong odd/even set: {parity or 'none'}")
        for q in range(1, n_q + 1):
            t = tag(form, sec, q)
            it, key = raw.get(t), keys.get(t)
            if not it and not key:
                continue
            it = it or {"stem": "", "choices": {}, "passage": ""}
            key = key or {"answer": None, "scored": True, "category": None}
            choices = {c: v.strip() for c, v in it["choices"].items()}
            block, skill = (act_english(it["stem"], choices) if sec == "English"
                            else (sec.lower(), None))
            items.append(make_item(
                qid=t, exam="ACT", form=form, section=sec, q=q, block=block, skill=skill,
                passage=it["passage"], stem=it["stem"], choices=choices,
                answer=key["answer"], scored=key["scored"], category=key["category"]))
    return items
