#!/usr/bin/env python3
"""
blocks.py: label question types from the question stem.

Stems are standardized on professional tests, so stem rules beat rules written
against answer explanations (SAT bank, held-out half: 97.4% vs 79%).
Each classifier returns (block, skill): block is the coarse type statistics
are run on, skill is the finer label.
"""
import re


def punct_only(choices):
    """True when the choices differ only in punctuation (a boundary question)."""
    sig = lambda s: re.sub(r"[^.,;:?!—–-]", "", s.replace(" ", ""))
    avg_words = sum(len(v.split()) for v in choices.values()) / max(1, len(choices))
    return len({sig(v) for v in choices.values()}) >= 2 and avg_words <= 6


def sat_rw(stem, choices):
    s = (stem or "").lower()
    if "conventions of standard english" in s:
        return "grammar", ("boundaries" if punct_only(choices)
                           else "form, structure, and sense")
    if "transition" in s:
        return "transition", "transitions"
    if "wants to" in s or "notes" in s:
        return "notes-synthesis", "rhetorical synthesis"
    if re.search(r"precise word or phrase|most nearly mean", s):
        return "vocab", "words in context"
    if re.search(r"text 1|text 2|based on the texts", s):
        return "reading", "cross-text connections"
    if re.search(r"main purpose|overall structure|function of the underlined|"
                 r"functions in the text|best describes the function|purpose of the", s):
        return "reading", "text structure and purpose"
    if re.search(r"quotation|would most directly (support|weaken|challenge|undermine)|"
                 r"if true|most effectively uses data|data from the (table|graph)|"
                 r"illustrate|completes the (example|statement)|graph|table|chart", s):
        return "reading", "command of evidence"
    if "most logically completes the text" in s:
        return "reading", "inferences"
    return "reading", "central ideas and details"


ACT_ENGLISH_CATEGORY = {
    "grammar-punctuation": "CSE", "grammar-usage": "CSE", "concision": "KLA",
    "tone-style": "KLA", "clarity-word-choice": "KLA", "transition": "POW",
    "delete-question": "POW", "add-question": "POW", "organization": "POW",
    "rhetorical-goal": "POW"}


def act_english(stem, choices):
    s = (stem or "").lower()
    if "grammatically acceptable" in s:
        real = {k: v for k, v in choices.items() if v.lower() != "no change"}
        t = "grammar-punctuation" if punct_only(real or choices) else "grammar-usage"
    elif re.search(r"redundan|wordiness", s):
        t = "concision"
    elif "tone" in s or "stylistic" in s:
        t = "tone-style"
    elif "transition" in s:
        t = "transition"
    elif re.search(r"clearest|most precise", s):
        t = "clarity-word-choice"
    elif re.search(r"delete|deleting", s):
        t = "delete-question"
    elif re.search(r"adding|add the following|add here|if added", s):
        t = "add-question"
    elif re.search(r"sequence of sentences|placement|should be placed|most logical place", s):
        t = "organization"
    else:
        t = "rhetorical-goal"
    return t, t
