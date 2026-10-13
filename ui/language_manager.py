"""Language selection, translations and RTL helpers for CryptoEdu Pro."""

from __future__ import annotations

from types import MappingProxyType

from core.textutils import fix_bidi
from ui.translations import TRANSLATIONS


class LanguageManager:
    """Own supported languages and provide a stable translation interface."""

    def __init__(self, default_language="AR"):
        self._translations = MappingProxyType({
            language: MappingProxyType(dict(values))
            for language, values in TRANSLATIONS.items()
        })
        self._current = default_language
        self.select(default_language)

    @property
    def languages(self):
        return tuple(self._translations)

    @property
    def current(self):
        return self._translations[self._current]

    @property
    def current_code(self):
        return self._current

    @property
    def is_rtl(self):
        return self._current == "AR"

    @property
    def justify(self):
        return "right" if self.is_rtl else "left"

    def select(self, language):
        if language not in self._translations:
            raise ValueError(f"Unsupported language: {language}")
        self._current = language
        return self.current

    def text(self, key, default=None):
        if default is None:
            return self.current[key]
        return self.current.get(key, default)

    def localize(self, arabic, english):
        return self.bidi(arabic) if self.is_rtl else english

    def bidi(self, text):
        return fix_bidi(text) if self.is_rtl else text
