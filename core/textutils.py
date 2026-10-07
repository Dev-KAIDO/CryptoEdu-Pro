# -*- coding: utf-8 -*-
"""
Directional text utilities for mixed Arabic/Latin/numbers content.

Problem: When Arabic text contains embedded English words, numbers, or code
(e.g. "المفتاح يجب أن يكون 10 بت ثنائي (مثل 1010110011)"), the bidirectional
algorithm can reorder characters in confusing ways due to LTR/RTL mixing.

Solution: Insert LEFT-TO-RIGHT MARK (LRM, U+200E) BEFORE each LTR run.
LRM is a zero-width invisible character that forces the following LTR
content to be treated as left-to-right by the bidi algorithm.
"""
import re

# Match maximal runs of characters that are inherently LTR:
# - Latin letters (A-Za-z)
# - Digits (0-9)
# - Common code symbols
# The run must START with a strong LTR char (letter or digit) to avoid wrapping
# stray punctuation that belongs to Arabic context.

_LTR_RUN = re.compile(
    r'[A-Za-z0-9]'
    r'[A-Za-z0-9\u0020-\u002f\u003a-\u0040\u005b-\u0060\u007b-\u007e'
    r'\u00b0\u00b1\u00b2\u00b3\u00b5\u00b7\u00d7\u00f7'
    r'\u2000-\u206f\u2070-\u209f\u20a0-\u20cf\u2100-\u214f'
    r'\u2190-\u21ff\u2200-\u22ff\u2300-\u23ff\u2500-\u257f'
    r'\u2580-\u259f\u25a0-\u25ff\u2600-\u26ff\u2700-\u27bf'
    r'\u2b00-\u2bff\u2e00-\u2e7f]*'
)

_ARABIC_RANGE = re.compile(r'[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufe70-\ufeff]')

# LRM (Left-to-Right Mark) — zero-width, forces following text to LTR direction
LRM = '\u200e'


def fix_bidi(text):
    """
    Insert LRM BEFORE each LTR run (English words, numbers, code, formulas)
    inside Arabic text to prevent bidi reordering issues.

    LRM before the run tells the bidi algorithm: "the next text is LTR,
    don't reorder it into the RTL flow."

    Only acts on strings that contain Arabic characters. Pure English/number
    strings are returned unchanged (they render fine as LTR).

    Examples:
        fix_bidi("شفرة RSA")
        → "شفرة \u200eRSA"  (RSA forced LTR after Arabic)

        fix_bidi("المفتاح 10 بت ثنائي")
        → "المفتاح \u200e10 بت ثنائي"  (10 forced LTR)

        fix_bidi("HELLO WORLD")
        → "HELLO WORLD"  (no Arabic, unchanged)
    """
    if not text:
        return text
    # Quick check: if no Arabic chars, nothing to fix
    if not _ARABIC_RANGE.search(text):
        return text
    return _LTR_RUN.sub(lambda m: LRM + m.group(0), text)


def fix_bidi_if_arabic(text, lang):
    """Only apply bidi fix if lang is AR."""
    if lang == "AR":
        return fix_bidi(text)
    return text
