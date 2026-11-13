"""College Board SAT Suite Question Bank (SAT, PSAT/NMSQT & PSAT 10, PSAT 8/9).

Inputs: metadata.json, a directory of fetched item JSON files, and optionally
a second directory of "ibn" items (older disclosed items, a different format).
Every item carries College Board's own skill label and E/M/H difficulty.

Fetching (public endpoints, no login). Run this file directly:
  python3 adapters/cb_qbank.py meta <event> <test> <out.json>
      event: 99 SAT, 100 PSAT/NMSQT & PSAT 10, 102 PSAT 8/9
      test:  1 Reading & Writing, 2 Math
  python3 adapters/cb_qbank.py items <metadata.json> <outdir> [<ibn_outdir>]
Fetching is one request at a time with a pause, and resumable. It calls curl,
so TLS certificates are checked by the system store; never disable that check.

The bank has no test forms, so `form` is a stable 5-way fold of the question
id ("fold0".."fold4"), which gives held-out splits for the simulation.
"""
import html
import json
import os
import re
import subprocess
import sys
import time
import zlib

NAME = "cb-qbank"
USAGE = "cb-qbank <metadata.json> <items_dir> [<ibn_items_dir>] --form SATQB"

API = "https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/digital/"
IBN = "https://saic.collegeboard.org/disclosed/{}.json"
DOMAINS = {1: "INI,CAS,EOI,SEC", 2: "H,P,Q,S"}
RW_DOMAINS = {"INI", "CAS", "EOI", "SEC"}


def clean(h):
    h = re.sub(r"<svg\b.*?</svg>", " [FIGURE] ", h or "", flags=re.S)
    h = re.sub(r"<(mo|mn|mi|mtext)[^>]*>", " ", h)  # keep math text, drop tags
    h = re.sub(r"<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(h)).strip()


def _curl(args):
    return subprocess.run(["curl", "-sf", "-m", "30"] + args,
                          capture_output=True, check=True).stdout


def fetch_meta(event, test, out):
    body = _curl(["-X", "POST", API + "get-questions", "-H", "Content-Type: application/json",
                  "-d", json.dumps({"asmtEventId": int(event), "test": int(test),
                                    "domain": DOMAINS[int(test)]})])
    data = json.loads(body)
    json.dump(data, open(out, "w"))
    print(f"{len(data)} metadata rows -> {out}")


def fetch_items(meta_path, outdir, ibn_dir=None):
    meta = json.load(open(meta_path))
    jobs = [(os.path.join(outdir, m["external_id"] + ".json"),
             ["-X", "POST", API + "get-question", "-H", "Content-Type: application/json",
              "-d", json.dumps({"external_id": m["external_id"]})])
            for m in meta if m.get("external_id")]
    if ibn_dir:
        jobs += [(os.path.join(ibn_dir, m["ibn"] + ".json"), [IBN.format(m["ibn"])])
                 for m in meta if m.get("ibn") and not m.get("external_id")]
    for d in filter(None, (outdir, ibn_dir)):
        os.makedirs(d, exist_ok=True)
    done = fail = 0
    for n, (path, args) in enumerate(jobs):
        if os.path.exists(path):
            done += 1
            continue
        for attempt in range(3):
            try:
                body = _curl(args)
                json.loads(body)
                open(path, "wb").write(body)
                done += 1
                break
            except Exception:
                time.sleep(2 * (attempt + 1))
        else:
            fail += 1
        time.sleep(0.2)
        if n % 200 == 0:
            print(f"{n}/{len(jobs)} done={done} fail={fail}", flush=True)
    print(f"finished: done={done} fail={fail} of {len(jobs)}", flush=True)


def _base(m, form):
    qid = m["questionId"]
    return dict(qid=qid, exam=m.get("program") or "SAT",
                form=f"{form}-fold{zlib.crc32(qid.encode()) % 5}" if form else
                f"fold{zlib.crc32(qid.encode()) % 5}",
                section="RW" if m.get("primary_class_cd") in RW_DOMAINS else "Math",
                q=None, block=m["skill_desc"].strip().lower(), skill=m["skill_desc"].strip(),
                category=m.get("primary_class_cd_desc"), difficulty=m.get("difficulty"),
                band=m.get("score_band_range_cd"))


def parse(inputs, form, opts):
    from ret_common import make_item
    if len(inputs) < 2:
        raise SystemExit("usage: " + USAGE)
    meta_rows = json.load(open(inputs[0]))
    meta = {m["external_id"]: m for m in meta_rows if m.get("external_id")}
    items, skipped = [], 0
    for f in sorted(os.listdir(inputs[1])):
        d = json.load(open(os.path.join(inputs[1], f)))
        m = meta.get(d.get("externalid") or f[:-5])
        if not m:
            skipped += 1
            continue
        opts_ = d.get("answerOptions") or []
        ca = (d.get("correct_answer") or [None])[0]
        mcq = d.get("type") == "mcq" and len(opts_) >= 2 and ca in ("A", "B", "C", "D")
        items.append(make_item(
            **_base(m, form), type="mcq" if mcq else "spr",
            passage=clean(d.get("stimulus")), stem=clean(d.get("stem")),
            choices={"ABCD"[i]: clean(o.get("content")) for i, o in enumerate(opts_[:4])}
            if mcq else {},
            answer=ca, rationale=clean(d.get("rationale"))))
    if len(inputs) > 2:
        ibn_meta = {m["ibn"]: m for m in meta_rows
                    if m.get("ibn") and not m.get("external_id")}
        for f in sorted(os.listdir(inputs[2])):
            raw = json.load(open(os.path.join(inputs[2], f)))
            d = raw[0] if isinstance(raw, list) else raw
            m = ibn_meta.get(d.get("item_id") or f[:-5])
            if not m:
                skipped += 1
                continue
            a = d.get("answer") or {}
            ch = a.get("choices") or {}
            cc = (a.get("correct_choice") or "").upper()
            mcq = isinstance(ch, dict) and bool(ch) and cc in ("A", "B", "C", "D")
            items.append(make_item(
                **_base(m, form), type="mcq" if mcq else "spr", source="ibn",
                stem=clean(d.get("prompt")),
                choices={k.upper(): clean(v.get("body")) for k, v in sorted(ch.items())[:4]}
                if mcq else {},
                answer=cc if mcq else str(a.get("correct_choice") or ""),
                rationale=clean(a.get("rationale"))))
    opts.setdefault("log", []).append(
        f"{form or 'bank'}: {len(items)} items "
        f"({sum(i['type'] == 'mcq' for i in items)} multiple-choice), "
        f"{skipped} files without metadata skipped")
    return items


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 4 and a[0] == "meta":
        fetch_meta(a[1], a[2], a[3])
    elif len(a) >= 3 and a[0] == "items":
        fetch_items(a[1], a[2], a[3] if len(a) > 3 else None)
    else:
        print(__doc__)
