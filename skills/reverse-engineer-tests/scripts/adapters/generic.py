"""Any plainly formatted multiple-choice paper: numbered questions with
lettered or numbered choices, plus a separate answer key.

Inputs: the paper (.pdf or .txt) and the key (.pdf or .txt).
Recognized question starts: "12." or "12)" at the start of a line.
Recognized choices: "A." "A)" "(A)" with letters A-K, or "(1)".."(5)".
Recognized key entries: "12 C", "12. C", "12) (C)", "12 - 3".
When question numbers restart at 1, a new section starts (S1, S2, ...), in
both the paper and the key.

This is a starting point. Always run `ret.py validate` on the result and fix
the adapter (or copy it into a test-specific one) until the counts are right.
"""
import re

from ret_common import make_item, to_text

NAME = "generic"
USAGE = "generic <paper.pdf|txt> <key.pdf|txt> --form X1 [--exam NAME]"

Q = re.compile(r"^\s{0,8}(\d{1,3})[.)]\s+(\S.*)$")
C = re.compile(r"^\s{0,12}(?:\(([A-Ka-k1-5])\)|([A-Ka-k])[.)])\s+(\S.*)$")
KEY = re.compile(r"(?<![\w.])(\d{1,3})\s*[.):\-–]?\s*\(?([A-Ka-k1-5])\)?(?![\w])")
RESET = re.compile(r"^\s*(passage|questions?\s+\d+\s*[-–]|directions)", re.I)


def parse_key(txt):
    secs, cur, last = [], {}, 0
    for n, a in KEY.findall(txt):
        n = int(n)
        if n <= last and n == 1:
            secs.append(cur)
            cur = {}
        if n not in cur and (n == last + 1 or not cur):
            cur[n] = a.upper()
            last = n
    secs.append(cur)
    return [s for s in secs if len(s) >= 3]


def parse_paper(txt):
    secs, cur, item, passage, mode, last_c = [], [], None, [], "text", None
    for line in txt.split("\n"):
        s = line.strip()
        if not s:
            if item and mode == "choice" and len(item["choices"]) >= 4:
                mode = "text"
            continue
        m = Q.match(line)
        expect = (item["q"] + 1) if item else 1
        if m and (int(m.group(1)) == expect or (int(m.group(1)) == 1 and expect > 3)):
            if int(m.group(1)) == 1 and cur:
                secs.append(cur)
                cur = []
            item = {"q": int(m.group(1)), "stem": m.group(2), "choices": {},
                    "passage": " ".join(passage)}
            cur.append(item)
            mode = "stem"
            continue
        c = C.match(line)
        if c and item and mode in ("stem", "choice"):
            last_c = (c.group(1) or c.group(2)).upper()
            if last_c not in item["choices"]:
                item["choices"][last_c] = c.group(3)
                mode = "choice"
                continue
        if mode == "stem":
            item["stem"] += " " + s
        elif mode == "choice":
            item["choices"][last_c] += " " + s
        else:
            if RESET.match(s):
                passage = []
            passage.append(s)
    if cur:
        secs.append(cur)
    return secs


def parse(inputs, form, opts):
    if len(inputs) < 2:
        raise SystemExit("usage: " + USAGE)
    secs, keys = parse_paper(to_text(inputs[0])), parse_key(to_text(inputs[1]))
    log = opts.setdefault("log", [])
    if len(secs) != len(keys):
        log.append(f"{form}: WARNING paper has {len(secs)} sections, key has {len(keys)}")
    items = []
    for n, sec in enumerate(secs, 1):
        key = keys[n - 1] if n <= len(keys) else {}
        log.append(f"{form} S{n}: {len(sec)} questions, {len(key)} key entries")
        for it in sec:
            items.append(make_item(
                qid=f"{form}-S{n}-Q{it['q']}", exam=opts.get("exam") or form, form=form,
                section=f"S{n}", q=it["q"], block=f"S{n}", passage=it["passage"],
                stem=it["stem"].strip(),
                choices={k: v.strip() for k, v in it["choices"].items()},
                answer=key.get(it["q"])))
    return items
