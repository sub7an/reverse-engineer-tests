#!/usr/bin/env python3
"""
ret.py: one command from papers to findings.

  python3 ret.py adapters
      list the exam adapters

  python3 ret.py ingest <adapter> <inputs...> --form ID -o items.json [--exam NAME]
      parse one paper into common-schema items (see ret_common.py)

  python3 ret.py validate items.json [more.json ...]
      check for parsing damage

  python3 ret.py run items.json [more.json ...] --out DIR
          [--block-by block|category|section|skill] [--exclude qid,qid]
          [--drop swallowed,unconfirmed] [--scored-only] [--min-n 8]
      merge, validate, run answer DNA and the held-out score simulation.
      Writes DIR/items.json, validation.txt, answer_dna.txt, simulation.txt,
      key_structure.txt and report.md.

A new exam costs one adapter (copy adapters/generic.py). Everything after
ingest is shared.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from ret_common import load_items, save_items  # noqa: E402
from validate_items import validate  # noqa: E402


def split_args(argv, valued):
    pos, opt, i = [], {}, 0
    while i < len(argv):
        a = argv[i]
        if a in valued:
            opt[a.lstrip("-")] = argv[i + 1]
            i += 2
        elif a.startswith("--"):
            opt[a.lstrip("-")] = True
            i += 1
        else:
            pos.append(a)
            i += 1
    return pos, opt


def cmd_ingest(argv):
    from adapters import ADAPTERS
    pos, opt = split_args(argv, {"--form", "-o", "--exam"})
    if not pos or pos[0] not in ADAPTERS:
        raise SystemExit("adapters: " + ", ".join(ADAPTERS))
    ad = ADAPTERS[pos[0]]
    opts = {"exam": opt.get("exam")}
    items = ad.parse(pos[1:], opt.get("form") or "", opts)
    out = opt.get("o") or "items.json"
    save_items(items, out)
    for line in opts.get("log", []):
        print(line)
    print(f"{len(items)} items -> {out}")


def run_script(name, args, out_path):
    r = subprocess.run([sys.executable, os.path.join(HERE, name)] + args,
                       capture_output=True, text=True)
    open(out_path, "w").write(r.stdout + (("\n[stderr]\n" + r.stderr) if r.returncode else ""))
    return r.returncode


def cmd_run(argv):
    pos, opt = split_args(argv, {"--out", "--block-by", "--exclude", "--drop", "--min-n"})
    if not pos:
        raise SystemExit(__doc__)
    out = opt.get("out") or "ret-out"
    os.makedirs(out, exist_ok=True)
    items = [i for p in pos for i in load_items(p)]
    lines, flags = validate(items)
    open(os.path.join(out, "validation.txt"), "w").write("\n".join(lines) + "\n")
    drop = set((opt.get("exclude") or "").split(",")) - {""}
    for name in (opt.get("drop") or "").split(","):
        drop |= set(flags.get(name, []))
    kept = [i for i in items if i["qid"] not in drop
            and (not opt.get("scored-only") or i.get("scored", True))]
    by = opt.get("block-by")
    if by:
        for i in kept:
            i["block"] = str(i.get(by) or i.get("block") or "unlabelled")
    merged = os.path.join(out, "items.json")
    save_items(kept, merged)
    min_n = ["--min-n", opt["min-n"]] if opt.get("min-n") else []
    run_script("answer_dna.py", [merged] + min_n, os.path.join(out, "answer_dna.txt"))
    run_script("simulate_score.py", [merged], os.path.join(out, "simulation.txt"))
    run_script("key_structure.py", [merged], os.path.join(out, "key_structure.txt"))
    run_script("report.py", [merged], os.path.join(out, "report.md"))
    print("\n".join(lines[-12:]))
    print(f"\n{len(items)} items in, {len(items) - len(kept)} dropped, {len(kept)} analyzed")
    print(f"wrote {out}/items.json, validation.txt, answer_dna.txt, simulation.txt, "
          "key_structure.txt, report.md")


def main():
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    if a[0] == "adapters":
        from adapters import ADAPTERS
        for ad in ADAPTERS.values():
            print(f"{ad.NAME:14} {ad.USAGE}\n{' ' * 15}{ad.__doc__.strip().splitlines()[0]}")
    elif a[0] == "ingest":
        cmd_ingest(a[1:])
    elif a[0] == "validate":
        print("\n".join(validate([i for p in a[1:] for i in load_items(p)])[0]))
    elif a[0] == "run":
        cmd_run(a[1:])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
