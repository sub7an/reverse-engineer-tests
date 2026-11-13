"""New York Regents Examination in English Language Arts (2014 onward),
Part 1: 24 reading questions on three texts, choices numbered (1)-(4).

Inputs: the exam PDF and the scoring-key PDF from nysedregents.org/hsela.
Question pages are printed in two columns, so each page is read one column
at a time (left half, then right half); plain extraction interleaves them.
Both key layouts are read: the 2019+ table ("June '25  7  3  MC") and the
older dotted list ("7 ......3......").
"""
import re
import subprocess

from ret_common import make_item

NAME = "regents-ela"
USAGE = "regents-ela <exam.pdf> <scoring-key.pdf> --form 2025-06"

Q = re.compile(r"^(\d{1,2})\s+(\S.*)$")
C = re.compile(r"\((\d)\)\s*")
FOOTER = re.compile(r"[–-]\s*(Jan|June|Aug)[a-z.]*\s*[’']\s?\d\d\b")


def _pdf(path, page=None, x=None, layout=False):
    cmd = ["pdftotext"]
    if layout:
        cmd.append("-layout")
    if page:
        cmd += ["-f", str(page), "-l", str(page)]
    if x is not None:
        cmd += ["-x", str(x), "-y", "0", "-W", "306", "-H", "792"]
    return subprocess.run(cmd + [path, "-"], capture_output=True, text=True).stdout


def _pages(path):
    out = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", out)
    return int(m.group(1)) if m else 0


def stem_block(stem):
    s = stem.lower()
    if re.search(r"most nearly means|as used in|most likely means|meaning of", s):
        return "vocab-in-context"
    if re.search(r"figurative|metaphor|simile|personification|imagery|irony|ironic|tone|"
                 r"point of view|flashback|symbol|foreshadow|example of|mood|"
                 r"narrat|repetition|literary", s):
        return "craft-device"
    if re.search(r"central idea|theme|best summar|primary purpose|purpose of the "
                 r"(text|passage|poem|article)|mainly about|as a whole", s):
        return "central-idea"
    if re.search(r"serves? to|purpose|function|structure|contribut|develop|emphasi|"
                 r"effect|introduc|establish|reinforc|creat|convey|reveal|illustrat|"
                 r"highlight|stress", s):
        return "craft-function"
    if re.search(r"evidence|best support|which (quotation|lines|statement|phrase)|"
                 r"supported by|supports the", s):
        return "evidence"
    return "detail-inference"


def parse_key(path):
    """-> {question number: "1".."4"} for the multiple-choice questions.
    Works for any Regents subject: the 2019+ table rows end
    "<number> <key> MC <credit> <weight>"; older keys are dotted lists
    ("7 . . . 3 . . ."), printed on the first pages of the rating guide."""
    txt = _pdf(path, layout=True)
    new = {}
    for q, a in re.findall(r"(?m)\s(\d{1,2})\s+([1-4])\s+MC\s+\d", txt):
        new.setdefault(int(q), a)
    if len(new) >= 20:
        return new
    part = txt.split("Correct Answers", 1)[-1] if "Correct Answers" in txt else txt
    old = {}
    for q, a in re.findall(r"(?<![\d.])(\d{1,2})\s*(?:\.\s*){3,}([1-4])\s*(?:\.\s*){3,}",
                           part[:6000]):
        old.setdefault(int(q), a)
    return old


def parse_exam(path, max_q=24):
    items, passage, cur, last, mode, seen_q = [], [], None, None, "text", False
    for p in range(1, _pages(path) + 1):
        cols = _pdf(path, p, 0) + "\n" + _pdf(path, p, 306)
        is_q = len(re.findall(r"(?m)^\([1-4]\)", cols)) >= 3
        if not is_q:
            if cur and len(items) >= max_q:
                break
            if seen_q:  # a new text starts after a block of questions
                passage, seen_q = [], False
            passage += [l.strip() for l in _pdf(path, p).split("\n")
                        if l.strip() and not re.fullmatch(r"\d{1,3}", l.strip())]
            continue
        seen_q = True
        lines = cols.split("\n")
        for n, line in enumerate(lines):
            s = line.strip()
            nxt = len(items) + 1
            ready = cur is None or len(cur["choices"]) >= 2
            # The question number can sit alone on its line. Accept it only
            # if choices follow before the next bare number (passage line
            # markers such as 5, 10, 15 look the same).
            if s == str(nxt) and nxt <= max_q and ready:
                ahead = [l.strip() for l in lines[n + 1:n + 14] if l.strip()]
                stop = next((k for k, l in enumerate(ahead) if l.isdigit()), len(ahead))
                if any(l.startswith("(1)") for l in ahead[:stop]):
                    cur = {"q": nxt, "stem": "", "choices": {},
                           "passage": " ".join(passage), "page": p}
                    items.append(cur)
                    mode = "stem"
                    continue
            if not s or re.match(r"^(Regents Exam|\[\d+\]|\[OVER\]|\d{1,2}\]?$)", s):
                if not s and cur and mode == "choice" and len(cur["choices"]) == 4:
                    mode = "text"
                continue
            # Page footers ("U.S. Hist. & Gov't. – Aug. '19") and stimulus
            # directions end a question; without this they are glued onto
            # the last choice.
            if FOOTER.search(s) and len(s) < 60:
                continue
            if re.match(r"^(Base your answers? to|Directions)", s):
                mode = "text"
                continue
            m = Q.match(s)
            # "ready" stops a wrapped stem such as "...lines 9 through / 11
            # conveys" from being read as the start of question 11.
            if m and int(m.group(1)) == nxt and nxt <= max_q and ready:
                cur = {"q": int(m.group(1)), "stem": m.group(2), "choices": {},
                       "passage": " ".join(passage), "page": p}
                items.append(cur)
                mode = "stem"
                continue
            if cur and s.startswith("(") and C.match(s) and mode in ("stem", "choice"):
                parts = C.split(s)[1:]
                for k, v in zip(parts[0::2], parts[1::2]):
                    if k in "1234" and k not in cur["choices"]:
                        cur["choices"][k] = v.strip()
                        last = k
                mode = "choice"
                continue
            if mode == "text":
                continue
            if cur and mode == "stem":
                cur["stem"] += " " + s
            elif cur and mode == "choice" and last:
                cur["choices"][last] += " " + s
    mark_truncated(path, items)
    return items


def mark_truncated(path, items):
    """Repair questions printed across the full page width. Reading the page
    in two halves cuts their lines at the middle.

    Test: plain full-page extraction keeps each printed line whole (columns
    come out as separate lines). Find the line where the stem and each choice
    start; if a line holds more text than the half-page parse captured, the
    line crossed the middle of the page. Such a question is then re-read from
    the full-page lines. If that fails it keeps "truncated": True and callers
    should drop it rather than analyze damaged text."""
    pages = {}
    squash = lambda t: re.sub(r"\s+", "", t)

    def start(lines, label, text):
        head = text.split()[:2]
        if not head:
            return None
        rx = re.compile(r"^\s*%s\s+%s" % (label, r"\s+".join(map(re.escape, head))))
        return next((n for n, l in enumerate(lines) if rx.search(l)), None)

    for it in items:
        pg = it.get("page")
        if pg not in pages:
            pages[pg] = (_pdf(path, pg) + "\n" + _pdf(path, pg + 1)).split("\n")
        lines = pages[pg]
        parts = [(str(it["q"]), it["stem"])] + [(r"\(%s\)" % k, v)
                                                for k, v in it["choices"].items()]
        cut = False
        for label, text in parts:
            n = start(lines, label, text)
            if n is None:
                continue
            run = squash(re.sub(r"^\s*(\(\d\)|\d{1,2})", "", lines[n]))
            if not squash(text).startswith(run):
                cut = True
        it["truncated"] = cut
        if not cut:
            continue
        n = start(lines, str(it["q"]), it["stem"])
        if n is None:
            continue
        stem, choices, last = [re.sub(r"^\s*\d{1,2}\s+", "", lines[n])], {}, None
        for line in lines[n + 1:n + 40]:
            t = line.strip()
            c = re.match(r"^\((\d)\)\s*(.*)$", t)
            if c and c.group(1) in "1234" and c.group(1) not in choices:
                last = c.group(1)
                choices[last] = c.group(2)
            elif not t:
                if len(choices) == 4:
                    break
            elif FOOTER.search(t) or re.match(r"^(Base your answers? to|\d{1,2}\s+[A-Z“])", t):
                break
            elif last:
                choices[last] += " " + t
            else:
                stem.append(t)
        if len(choices) == 4 and all(choices.values()):
            it.update(stem=" ".join(stem), choices=choices, truncated=False, repaired=True)


def parse(inputs, form, opts):
    if len(inputs) < 2:
        raise SystemExit("usage: " + USAGE)
    raw, key = parse_exam(inputs[0]), parse_key(inputs[1])
    raw = [i for i in raw if not i.get("truncated")]
    opts.setdefault("log", []).append(
        f"{form}: {len(raw)}/24 questions, {len(key)}/24 key entries, "
        f"{sum(len(i['choices']) == 4 for i in raw)} with 4 choices")
    return [make_item(
        qid=f"{form}-P1-Q{i['q']}", exam="Regents ELA", form=form, section="Part 1",
        q=i["q"], block=stem_block(i["stem"]), passage=i["passage"], stem=i["stem"].strip(),
        choices=i["choices"], answer=key.get(i["q"])) for i in raw]
