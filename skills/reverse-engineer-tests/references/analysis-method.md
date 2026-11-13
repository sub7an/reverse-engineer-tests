# Analysis method — per-question rubric and trap taxonomy

## Per-question rubric

For every question, decide these before writing the row:

1. **Stem type** — what the question literally asks (find value, best choice,
   except/least, inference, main idea, fix the sentence, etc.).
2. **Skill tested** — the atomic competency. Be specific: not "math" but
   "linear equation in one variable"; not "reading" but "command of evidence —
   locate support".
3. **Solve path, textbook vs. fast** — solve it the long way to be sure, then
   note the fastest reliable shortcut a test-taker should use under time.
4. **Distractor autopsy** — for each wrong choice, name the mistake it rewards.
   The pattern across the wrong choices IS the trap.
5. **Difficulty** — from number of steps, subtlety of the trap, and how close
   the best distractor is to correct.

## Labelling question types at scale: use the stem, not the explanation

When classifying hundreds of items automatically, key on the **question stem**
("Which choice most logically completes the text?", "...conforms to the
conventions of Standard English?"). Test makers standardize stems; explanation
wording drifts between sources and writers. On the SAT Question Bank, an
explanation-based classifier matched the official skill labels 79% of the
time on a held-out half; a stem-based one matched 97.4% (908/932). For grammar items, look at the
choices too: if they differ only in punctuation, it's a boundaries/punctuation
item; otherwise it's verb form, agreement, or structure.

Always measure a classifier against official labels on a **held-out half**
(tune rules on one half, report accuracy on the other), never on the items
you tuned on.

## Trap taxonomy (name the trap using these)

- **Off-by-one / sign flip** — arithmetic slip the distractor rewards.
- **Right answer to the wrong question** — solves a real sub-step but not what
  was asked (e.g. finds x when it asked for 2x).
- **Partial / incomplete** — true but doesn't fully answer; misses a condition.
- **Too broad / too narrow** — reading: scope mismatch with the passage claim.
- **Reversal** — negates or swaps cause/effect, before/after, more/less.
- **Trap keyword** — relies on a word that appears in the passage but out of
  context ("word-match" distractor).
- **Extreme language** — always/never/only; usually wrong on reading unless the
  text is equally absolute.
- **Unit / conversion** — right number, wrong unit or scale.
- **Plausible outside knowledge** — true in the world but unsupported by the
  passage/data given.
- **Premature stop** — stops one algebra step early.

## Fast-method toolkit (cite which applies)

- **Plug in the answers** — MCQ with numeric choices; test choices, often from
  the middle.
- **Pick numbers** — variables in choices; substitute concrete values.
- **Eliminate to two, then decide on the trap** — kill obvious distractors,
  then resolve the near-miss on its specific flaw.
- **Evidence-pair lock** — reading "evidence" question pairs: answer the content
  question only via a line that also answers the evidence question.
- **Estimate / bound** — when exact compute is slow and choices are spread.
- **Scan for the changed word** — grammar/writing: find the single edited element.

## Coverage and honesty

End every analysis with: questions analyzed, questions skipped and why,
official-key vs. derived-answer counts, and confidence on any answer-choice
tells (default: low on professionally made tests).
