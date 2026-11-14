"""Any multiple-choice paper, layout detected automatically.

Inputs: the paper (.pdf, .docx, .txt, .md) and, optionally, a separate answer
key in any of those formats. With no key file the key is looked for inside
the paper: a per-question "Answer: C" line, or an "Answer Key" section at
the end.

What it recognizes
  questions   "12."  "12)"  "Q12"  "Q.12"  "Question 12"  "Problem 12"  "12 text"
  choices     "A."  "A)"  "(A)"  "[A]"  "a)"  "(1)"  "①", one per line or
              several on one line ("A) 4   B) 6   C) 8   D) 12"); 3 to 10 per
              question; labels must run in order, so "I. II. III." statement
              lists inside a question are not mistaken for choices
  keys        "12 C"  "12. C"  "12) (C)"  "12 - C"  "12: C", a row of numbers
              over a row of letters, or a bare run of letters in question order
  sections    numbering that restarts at 1

It tries every question style on every reading of the file (plain text,
column-preserving layout, and each page read as two half-pages) and keeps
the parse with the most usable questions and the least damage. The log says
which one won. This is a best effort: always run `ret.py validate` on the
result, and write a test-specific adapter when an exam needs one.
"""
import re
import subprocess

from ret_common import make_item, to_text
from validate_items import validate

NAME = "auto"
USAGE = "auto <paper.pdf|docx|txt> [key.pdf|docx|txt] --form X1 [--exam NAME]"

Q_STYLES = {
    "1.": re.compile(r"^\s{0,12}(\d{1,3})\s*[.)](?!\d)\s*(.*)$"),
    "Q1": re.compile(r"^\s{0,12}(?:Q|Question|Problem|Item|No\.?)\s*\.?\s*(\d{1,3})"
                     r"\s*[.:)\-]?\s*(.*)$", re.I),
    "1 ": re.compile(r"^\s{0,12}(\d{1,3})\s+(\S.*)$"),
}
CIRCLED = dict(zip("①②③④⑤⑥⑦⑧⑨", "123456789"))
# A choice marker: "(A)" "[A]" "A)" "A." "a)" "(1)" or a circled digit.
MARK = re.compile(r"(?:(?<=\s)|^)(?:[\(\[]([A-Ja-j]|\d)[\)\]]|([A-Ja-j])[\).:]|([①-⑨]))"
                  r"(?=\s|$)")
ANSWER = re.compile(r"^\s*(?:correct\s+)?(?:answer|ans|key)\s*(?:is)?\s*[:.\-–=]?\s*"
                    r"[\(\[]?([A-Ja-j]|[1-9])[\)\]]?(?![\w])", re.I)
KEY_HEAD = re.compile(r"^\s*(?:answer\s*key|answers?|scoring\s*key|mark(?:ing)?\s*scheme|"
                      r"key|solutions?)\s*:?\s*$", re.I)
NOISE = re.compile(r"^\s*(?:page\s+)?\d{1,3}(?:\s+of\s+\d{1,3})?\s*$|"
                   r"^\s*(?:go on to the next page|stop|continue)\W*$", re.I)
KEY_PAIR = re.compile(r"(?<![\w.])(\d{1,3})\s*[.):\-–=]?\s*[\(\[]?([A-Ja-j]|[1-9])[\)\]]?"
                      r"(?![\w])")
FIRST = {"A", "F", "1"}


def _label(m):
    return (m.group(1) or m.group(2) or CIRCLED.get(m.group(3), "")).upper()


def _next(label):
    return chr(ord(label) + 1)


def choice_chain(line, last):
    """The choices that start on this line, as [(label, text)], or []. The
    first marker must open the line and continue the question's sequence
    (A after nothing, C after B); later markers on the line count only if
    they continue it too. Anything else is ordinary text."""
    want = None if last is None else _next(last)
    out, pos = [], None
    for m in MARK.finditer(line):
        lab = _label(m)
        if not out and line[:m.start()].strip():
            return []
        ok = (lab in FIRST) if (want is None and not out) else lab == want
        if not ok:
            if not out:
                return []
            continue
        if out:
            out[-1] = (out[-1][0], line[pos:m.start()].strip())
        out.append((lab, ""))
        pos, want = m.end(), _next(lab)
    if out:
        out[-1] = (out[-1][0], line[pos:].strip())
    return out


def parse_paper(text, style):
    """-> (sections, embedded key text). A section is a list of question
    dicts; a new one starts when numbering restarts at 1."""
    rx = Q_STYLES[style]
    secs, cur, item, passage = [], [], None, []
    mode, fresh, lines = "text", False, text.split("\n")
    done = lambda sec: sum(len(q["choices"]) >= 2 for q in sec)
    for n, line in enumerate(lines):
        s = line.strip()
        if KEY_HEAD.match(line) and done(cur) + sum(map(done, secs)) >= 3:
            if cur:
                secs.append(cur)
            return secs, "\n".join(lines[n + 1:])
        if not s:
            if item and mode == "choice" and len(item["choices"]) >= 3:
                mode = "after"
            continue
        if NOISE.match(line):
            continue
        if item:
            a = ANSWER.match(line)
            if a and item["choices"]:
                item["answer"] = a.group(1).upper()
                mode = "explain"
                continue
            if mode in ("stem", "choice", "after"):
                last = list(item["choices"])[-1] if item["choices"] else None
                chain = choice_chain(line, last)
                if chain:
                    for lab, txt in chain:
                        item["choices"][lab] = txt
                    mode = "choice"
                    continue
        m = rx.match(line)
        if m:
            num = int(m.group(1))
            expect = item["q"] + 1 if item else None
            complete = item is None or len(item["choices"]) >= 2
            restart = num == 1 and item is not None and item["q"] != 1
            near = (style != "1 " and item is not None and complete
                    and expect < num <= expect + 3)
            if item is None or (num == expect and complete) or restart or near:
                if restart:
                    if done(cur) >= 3:
                        secs.append(cur)
                    cur = []
                item = {"q": num, "stem": m.group(2).strip(), "choices": {},
                        "passage": " ".join(passage), "answer": None}
                cur.append(item)
                mode, fresh = "stem", True
                continue
        if mode == "stem":
            item["stem"] += " " + s
        elif mode == "choice":
            last = list(item["choices"])[-1]
            item["choices"][last] = (item["choices"][last] + " " + s).strip()
        elif mode != "explain":
            if fresh:  # new reading text after a block of questions
                passage, fresh = [], False
            passage.append(s)
    if cur:
        secs.append(cur)
    return secs, ""


def parse_key(text, numeric):
    """-> list of {question number: answer} per section."""
    allowed = (lambda a: a.isdigit()) if numeric else (lambda a: a.isalpha())
    rows = [l.split() for l in text.split("\n")]
    pairs = []
    for top, bottom in zip(rows, rows[1:]):  # a row of numbers over a row of answers
        if (len(top) >= 5 and len(top) == len(bottom) and all(t.isdigit() for t in top)
                and all(len(b) == 1 and allowed(b) for b in bottom)):
            pairs += zip(top, bottom)
    if not pairs:
        pairs = [(n, a) for n, a in KEY_PAIR.findall(text) if allowed(a)]
    secs, cur = [], {}
    for n, a in pairs:
        n = int(n)
        if n in cur:
            if n > 2:
                continue
            secs.append(cur)
            cur = {}
        cur[n] = a.upper()
    secs.append(cur)
    secs = [s for s in secs if len(s) >= 3]
    if not secs:  # a bare run of answers in question order
        run = [t.upper() for t in re.findall(r"(?<![\w])([A-Ja-j]|[1-9])(?![\w])", text)
               if allowed(t)]
        if len(run) >= 5:
            secs = [dict(enumerate(run, 1))]
    return secs


def attach_key(secs, keys):
    """Give each question its key answer. Sections pair by position; a single
    key that runs straight through a paper whose numbering restarts is dealt
    out in order."""
    total = sum(len(s) for s in secs)
    if len(keys) == 1 and len(secs) > 1 and len(keys[0]) == total:
        answers = [keys[0][k] for k in sorted(keys[0])]
        for q, a in zip((q for s in secs for q in s), answers):
            q["answer"] = q["answer"] or a
        return
    for sec, key in zip(secs, keys):
        for q in sec:
            q["answer"] = q["answer"] or key.get(q["q"])


def halves(path):
    """A PDF read one half-page at a time, for two-column layouts."""
    info = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
    pages = re.search(r"Pages:\s+(\d+)", info)
    size = re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info)
    if not pages or not size or int(pages[1]) > 200:
        return ""
    w, h = int(float(size[1])), int(float(size[2]))
    out = []
    for p in range(1, int(pages[1]) + 1):
        for x in (0, w // 2):
            out.append(subprocess.run(
                ["pdftotext", "-f", str(p), "-l", str(p), "-x", str(x), "-y", "0",
                 "-W", str(w // 2), "-H", str(h), path, "-"],
                capture_output=True, text=True).stdout)
    return "\n".join(out)


def build(secs, form, exam):
    items = []
    for n, sec in enumerate(secs, 1):
        for q in sec:
            items.append(make_item(
                qid=f"{form}-S{n}-Q{q['q']}", exam=exam, form=form, section=f"S{n}",
                q=q["q"], block=f"{exam} S{n}" if len(secs) > 1 else exam,
                passage=q["passage"], stem=q["stem"].strip(),
                choices={k: v.strip() for k, v in q["choices"].items()},
                answer=q["answer"]))
    return items


def quality(items):
    usable = sum(1 for i in items if len(i["choices"]) >= 3 and i["answer"] in i["choices"])
    flags = validate(items)[1] if items else {}
    gaps = 0
    for sec in {i["section"] for i in items}:
        nums = [i["q"] for i in items if i["section"] == sec]
        gaps += max(nums) - min(nums) + 1 - len(set(nums))
    return (usable - 0.5 * gaps - len(flags.get("swallowed", []))
            - 0.5 * len(flags.get("choices", [])))


def family(head):
    """Name of the specialized adapter for this paper, judged from the text
    of its first pages, or None."""
    h = re.sub(r"[^a-z]+", " ", re.sub(r"[^\x00-\x7f]", "", head).lower())
    if "regents high school examination" in h:
        return "regents-ela" if "english language arts" in h else "regents-mc"
    if "the sat practice test" in h:
        return "sat-digital"
    if "preparing for the act" in h:
        return "act-enhanced"
    return None


def parse(inputs, form, opts):
    if not inputs:
        raise SystemExit("usage: " + USAGE)
    paper = inputs[0]
    exam = opts.get("exam") or "Exam"
    log = opts.setdefault("log", [])
    key_text = to_text(inputs[1]) if len(inputs) > 1 else None
    readings = [("plain text", lambda: to_text(paper))]
    if paper.lower().endswith(".pdf"):
        readings += [("column layout", lambda: to_text(paper, layout=True)),
                     ("half-pages", lambda: halves(paper))]
    best = (float("-inf"), [], "nothing")
    # A paper from a known exam family goes to that family's own adapter
    # first: two-column state and national exams defeat layout guessing.
    fam = family(to_text(paper)[:6000]) if paper.lower().endswith(".pdf") else None
    if fam:
        from . import act_enhanced, regents_ela, regents_mc, sat_digital
        mod = {m.NAME: m for m in (act_enhanced, regents_ela, regents_mc, sat_digital)}[fam]
        try:
            sub = {"exam": opts.get("exam")}
            items = mod.parse(inputs, form, sub)
            best = (quality(items), items, f"the {fam} adapter (recognized from the cover page)")
            log.extend(sub.get("log", []))
        except (Exception, SystemExit) as e:  # wrong inputs for that family: fall through
            log.append(f"{form}: looked like {fam} but that adapter failed ({e}); guessing the layout")
    if best[1] and best[0] >= 0.8 * len(best[1]):
        readings = []
    for how, read in readings:
        text = read()
        if not text.strip():
            continue
        for style in Q_STYLES:
            secs, embedded = parse_paper(text, style)
            secs = [s for s in secs if s]
            if not secs:
                continue
            labels = [next(iter(q["choices"]), "A") for s in secs for q in s]
            numeric = sum(l.isdigit() for l in labels) > len(labels) / 2
            keys = parse_key(key_text if key_text is not None else embedded, numeric)
            attach_key(secs, keys)
            items = build(secs, form, exam)
            score = quality(items)
            if score > best[0]:
                best = (score, items, f'{how}, questions written like "{style.strip()}"')
        # the half-page reading is slow; skip it when a faster one is clean
        if best[1] and best[0] >= 0.95 * len(best[1]):
            break
    _, items, how = best
    usable = sum(1 for i in items if len(i["choices"]) >= 3 and i["answer"] in i["choices"])
    if not items:
        log.append(f"{form}: no questions found. If this is a scanned PDF it has no text "
                   "layer: run OCR first (for example `ocrmypdf in.pdf out.pdf`).")
    else:
        log.append(f"{form}: {len(items)} questions found, {usable} usable "
                   f"(3+ choices and a key answer); read as {how}")
        if usable < len(items):
            log.append(f"{form}: {sum(1 for i in items if not i['answer'])} without a key "
                       f"answer, {sum(1 for i in items if len(i['choices']) < 3)} with fewer "
                       "than 3 choices")
    return items
