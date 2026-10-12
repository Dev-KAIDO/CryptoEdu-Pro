"""Theme definitions and selection for CryptoEdu Pro."""

from __future__ import annotations

from types import MappingProxyType


THEME_DEFINITIONS = {
    "Midnight": {
        "BG_DARK": "#0a0a0f",
        "BG_CARD": "#12121a",
        "BG_SIDEBAR": "#08080d",
        "BG_CARD_HOVER": "#1e1e2e",
        "BG_INPUT": "#1a1a25",
        "BG_CODE": "#111119",
        "BG_LINENUM": "#0c0c12",
        "PRIMARY": "#7c3aed",
        "PRIMARY_LIGHT": "#a78bfa",
        "PRIMARY_DARK": "#5b21b6",
        "ACCENT": "#f59e0b",
        "SECONDARY": "#06b6d4",
        "BORDER_COLOR": "#2a2a35",
        "TEXT_WHITE": "#ffffff",
        "TEXT_LIGHT": "#e2e8f0",
        "TEXT_GRAY": "#94a3b8",
        "TEXT_MUTED": "#64748b",
        "SUCCESS": "#10b981",
        "ERROR": "#ef4444",
        "WARNING": "#f59e0b",
        "WARNING_LIGHT": "#fbbf24",
        "SUCCESS_LIGHT": "#34d399",
        "ERROR_LIGHT": "#f87171",
    },
    "Ocean": {
        "BG_DARK": "#0c1222",
        "BG_CARD": "#131d30",
        "BG_SIDEBAR": "#09101e",
        "BG_CARD_HOVER": "#1a2d4a",
        "BG_INPUT": "#1a2744",
        "BG_CODE": "#0f1c30",
        "BG_LINENUM": "#0a1220",
        "PRIMARY": "#0ea5e9",
        "PRIMARY_LIGHT": "#38bdf8",
        "PRIMARY_DARK": "#0284c7",
        "ACCENT": "#f59e0b",
        "SECONDARY": "#06b6d4",
        "BORDER_COLOR": "#1e3a5f",
        "TEXT_WHITE": "#ffffff",
        "TEXT_LIGHT": "#e2e8f0",
        "TEXT_GRAY": "#94a3b8",
        "TEXT_MUTED": "#64748b",
        "SUCCESS": "#10b981",
        "ERROR": "#ef4444",
        "WARNING": "#f59e0b",
        "WARNING_LIGHT": "#fbbf24",
        "SUCCESS_LIGHT": "#34d399",
        "ERROR_LIGHT": "#f87171",
    },
    "Purple Haze": {
        "BG_DARK": "#0f0a1a",
        "BG_CARD": "#1a1230",
        "BG_SIDEBAR": "#0a0714",
        "BG_CARD_HOVER": "#261a45",
        "BG_INPUT": "#221840",
        "BG_CODE": "#15102a",
        "BG_LINENUM": "#0d0820",
        "PRIMARY": "#a855f7",
        "PRIMARY_LIGHT": "#c084fc",
        "PRIMARY_DARK": "#7c3aed",
        "ACCENT": "#f472b6",
        "SECONDARY": "#06b6d4",
        "BORDER_COLOR": "#2d1f5e",
        "TEXT_WHITE": "#ffffff",
        "TEXT_LIGHT": "#e2e8f0",
        "TEXT_GRAY": "#94a3b8",
        "TEXT_MUTED": "#64748b",
        "SUCCESS": "#10b981",
        "ERROR": "#ef4444",
        "WARNING": "#f59e0b",
        "WARNING_LIGHT": "#fbbf24",
        "SUCCESS_LIGHT": "#34d399",
        "ERROR_LIGHT": "#f87171",
    },
    "Emerald": {
        "BG_DARK": "#0a1210",
        "BG_CARD": "#12201c",
        "BG_SIDEBAR": "#08100e",
        "BG_CARD_HOVER": "#1a3528",
        "BG_INPUT": "#1a3028",
        "BG_CODE": "#0f1a16",
        "BG_LINENUM": "#0b1510",
        "PRIMARY": "#10b981",
        "PRIMARY_LIGHT": "#34d399",
        "PRIMARY_DARK": "#059669",
        "ACCENT": "#f59e0b",
        "SECONDARY": "#06b6d4",
        "BORDER_COLOR": "#1a4030",
        "TEXT_WHITE": "#ffffff",
        "TEXT_LIGHT": "#e2e8f0",
        "TEXT_GRAY": "#94a3b8",
        "TEXT_MUTED": "#64748b",
        "SUCCESS": "#10b981",
        "ERROR": "#ef4444",
        "WARNING": "#f59e0b",
        "WARNING_LIGHT": "#fbbf24",
        "SUCCESS_LIGHT": "#34d399",
        "ERROR_LIGHT": "#f87171",
    },
}


class ThemeManager:
    """Own available themes and validate theme changes outside the main window."""

    def __init__(self, default_name="Midnight"):
        self._themes = MappingProxyType({
            name: MappingProxyType(dict(colors)) for name, colors in THEME_DEFINITIONS.items()
        })
        self._current_name = default_name
        self.select(default_name)

    @property
    def names(self):
        return tuple(self._themes)

    @property
    def current_name(self):
        return self._current_name

    @property
    def current(self):
        return self._themes[self._current_name]

    def select(self, name):
        if name not in self._themes:
            raise ValueError(f"Unknown theme: {name}")
        self._current_name = name
        return self.current

    def get(self, name):
        try:
            return self._themes[name]
        except KeyError:
            raise ValueError(f"Unknown theme: {name}") from None
