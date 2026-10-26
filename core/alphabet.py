# core/alphabet.py
# -*- coding: utf-8 -*-
"""Abecedaries shared by the classic ciphers: Latin 26 and Arabic 28.

الوضع العربي يُفعَّل تلقائيًا عندما يحتوي النص على أي حرف عربي،
وتُعد العمليات على فهرس 28 حرفًا بدل 26.

التطبيع يوحّد: أ إ آ ٱ → ا ، ة → ه ، ى → ي
والهمزة المنفصلة (ء) تمرّ دون تشفير كالفراغات والأرقام.
"""

ARABIC_ALPHABET = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"  # 28 حرفًا بالترتيب التقليدي
LATIN_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ARABIC_NORMALIZATION = {
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ٱ": "ا",
    "ة": "ه",
    "ى": "ي",
}

STANDALONE_HAMZA = "ء"

ARABIC_INDEX = {ch: i for i, ch in enumerate(ARABIC_ALPHABET)}
LATIN_INDEX = {ch: i for i, ch in enumerate(LATIN_ALPHABET)}

_AR_VARIANTS = set(ARABIC_INDEX) | set(ARABIC_NORMALIZATION) | {STANDALONE_HAMZA}


def is_arabic_char(ch):
    """هل الحرف ضمن الأبجدية العربية الـ28 (بعد التطبيع)."""
    return ch in ARABIC_INDEX


def is_arabic_text(text):
    """هل يحتوي النص على أي حرف عربي (بأي تكيّف إملائي شائع)."""
    return any(ch in _AR_VARIANTS for ch in text)


def normalize_arabic(text):
    """توحيد المتغيرات الإملائية إلى الأحرف الـ28 المعيارية."""
    return "".join(ARABIC_NORMALIZATION.get(ch, ch) for ch in text)


def arabic_index(ch):
    """موقع الحرف (0-27) في الأبجدية العربية؛ يفشل صراحة قبلها."""
    return ARABIC_INDEX[ch]
