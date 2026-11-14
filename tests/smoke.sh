#!/usr/bin/env bash
# End-to-end check on the synthetic demo exam: ingest -> validate -> run.
# The demo plants one flaw (longest choice is right far above chance); the
# pipeline must parse every question, find the flaw, and price it held-out.
set -euo pipefail
cd "$(dirname "$0")/.."
S=skills/reverse-engineer-tests/scripts
T=$(mktemp -d)

python3 examples/make_demo.py "$T/demo" >/dev/null
for i in 1 2 3 4; do
  python3 $S/ret.py ingest auto "$T/demo/form$i.txt" "$T/demo/key$i.txt" \
    --form D$i --exam Demo -o "$T/d$i.json" >/dev/null
done
python3 $S/ret.py run "$T"/d[1-4].json --out "$T/out" >/dev/null

grep -q "usable for answer-choice statistics: 160 of 160" "$T/out/validation.txt"
grep -q "length: correct is the unique HIGHEST.*PICK SIGNAL (strong)" "$T/out/answer_dna.txt"
grep -Eq "^ALL .*\+[0-9.]+ pts ± [0-9.]+ \*" "$T/out/simulation.txt"
grep -q "PICK      the choice with the highest length" "$T/out/simulation.txt"

grep -q "Favour\*\* the longest choice" "$T/out/report.md"
grep -q "Coverage: 160 analyzed / 0 skipped" "$T/out/report.md"

echo "smoke test passed"
