#!/usr/bin/env python3
"""
ret_common.py: the common item schema and small helpers shared by every script.

One item = one question, in this shape (every adapter emits it, every analysis
script reads it):

  qid            "ACT1-ENGL-Q7"   stable id: <form>-<section>-Q<n>
  exam           "ACT"            test family
  form           "ACT1"           one paper / administration (used for held-out splits)
  section        "English"
  q              7                question number inside the section
  block          "grammar-usage"  coarse question type; statistics are run per block
  skill          "..."            finer label when known (official if the maker gives one)
  passage        "..."            text the question is about ("" if none)
  stem           "..."            the question itself
  choices        {"A": "...", ...}  ({} for grid-in / key-only items)
  answer         "C"
  answer_source  "official" | "derived"
  scored         true             false for field-test items
  category       "CSE"            maker's reporting category, if printed on the key
  difficulty     "E" | "M" | "H" | null   official labels only, never guessed
  confirmed      true | false | null   answer text was found in the explanation
"""
import json
import subprocess

FIELDS = ("qid", "exam", "form", "section", "q", "block", "skill", "passage",
          "stem", "choices", "answer", "answer_source", "scored", "category",
          "difficulty", "confirmed")
DEFAULTS = {"block": None, "skill": None, "passage": "", "stem": "",
            "choices": {}, "answer": None, "answer_source": "official",
            "scored": True, "category": None, "difficulty": None,
            "confirmed": None}


def make_item(**kw):
    it = dict(DEFAULTS)
    it.update(kw)
    it["choices"] = dict(it["choices"] or {})
    return it


def to_text(path, layout=False):
    """Text of a .pdf (via pdftotext) or a text file. layout=True keeps the
    page's columns side by side, which key tables need."""
    if path.lower().endswith(".pdf"):
        cmd = ["pdftotext"] + (["-layout"] if layout else []) + [path, "-"]
        return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return open(path, encoding="utf-8", errors="replace").read()


def load_items(path):
    data = json.load(open(path))
    return data.get("items", data) if isinstance(data, dict) else data


def save_items(items, path):
    json.dump({"items": items}, open(path, "w"), indent=1, ensure_ascii=False)
