"""Exam adapters. Each module exposes NAME, USAGE and parse(inputs, form, opts)
returning a list of common-schema items (see ret_common.py).

To add an exam: copy generic.py, keep the same parse() signature, and register
the module in ADAPTERS below. Parsing is exam-specific; everything after it
(validate, answer DNA, simulation) is shared.
"""
from . import act_enhanced, cb_qbank, generic, regents_ela, regents_mc, sat_digital

ADAPTERS = {m.NAME: m for m in (sat_digital, act_enhanced, cb_qbank, regents_ela, regents_mc, generic)}
