# main.py
import customtkinter as ctk
import sys
import os
import re
import math
import bisect
import pyperclip
from tkinter import messagebox

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.algorithms import CryptoCore
from core.service import CryptoOperationService
from core.textutils import fix_bidi
from ui.translations import TRANSLATIONS

try:
    from ui.styles import AppColors, AppFonts, AppSizes
except ImportError:
    class AppColors:
        PRIMARY = "#7c3aed"
        PRIMARY_LIGHT = "#a78bfa"
        PRIMARY_DARK = "#5b21b6"
        PRIMARY_DARKER = "#312e81"
        SECONDARY = "#06b6d4"
        SECONDARY_LIGHT = "#22d3ee"
        ACCENT = "#f59e0b"
        ACCENT_LIGHT = "#fbbf24"
        PURPLE = "#a855f7"
        PINK = "#ec4899"
        BG_DARK = "#0a0a0f"
        BG_CARD = "#12121a"
        BG_CARD_HOVER = "#1e1e2e"
        BG_INPUT = "#1a1a25"
        BG_SIDEBAR = "#08080d"
        TEXT_WHITE = "#ffffff"
        TEXT_LIGHT = "#e2e8f0"
        TEXT_GRAY = "#94a3b8"
        TEXT_MUTED = "#64748b"
        SUCCESS = "#10b981"
        SUCCESS_LIGHT = "#34d399"
        ERROR = "#ef4444"
        ERROR_LIGHT = "#f87171"
        WARNING = "#f59e0b"
        WARNING_LIGHT = "#fbbf24"
        INFO = "#3b82f6"
        ENCRYPT_COLOR = "#10b981"
        DECRYPT_COLOR = "#f59e0b"
        COPY_COLOR = "#6366f1"
        CLEAR_COLOR = "#ef4444"
        CODE_KEYWORD = "#c084fc"
        CODE_FUNCTION = "#22d3ee"
        CODE_STRING = "#34d399"
        CODE_COMMENT = "#64748b"
        CODE_NUMBER = "#fbbf24"
        CODE_OPERATOR = "#f472b6"
        BORDER_COLOR = "#2a2a35"
        BORDER_FOCUS = "#6366f1"

    class AppFonts:
        TITLE = ("Segoe UI", 28, "bold")
        SUBTITLE = ("Segoe UI", 16, "normal")
        BODY = ("Segoe UI", 13, "normal")
        BUTTON = ("Segoe UI", 14, "bold")
        BUTTON_LARGE = ("Segoe UI", 16, "bold")
        CODE = ("Cascadia Code", 12, "normal")
        CODE_BOLD = ("Cascadia Code", 12, "bold")
        CODE_LARGE = ("Cascadia Code", 14, "normal")
        SMALL = ("Segoe UI", 11, "normal")
        STAT_NUMBER = ("Segoe UI", 24, "bold")
        HERO_TITLE = ("Segoe UI", 36, "bold")

    class AppSizes:
        SIDEBAR_WIDTH = 280
        BUTTON_HEIGHT = 45
        BUTTON_HEIGHT_SMALL = 35
        INPUT_HEIGHT = 150
        CARD_RADIUS = 12
        BUTTON_RADIUS = 10

try:
    from ui.widgets import StatusBar, AnimatedButton, ExplanationCard, CodeBlock
except ImportError:
    class StatusBar(ctk.CTkFrame):
        def __init__(self, master, **kwargs):
            super().__init__(master, height=40, **kwargs)
            self.configure(fg_color="#12121a", corner_radius=0)
            self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.status_frame.pack(side="left", padx=15, pady=8)
            self.status_dot = ctk.CTkLabel(self.status_frame, text="\u25cf", font=("Segoe UI", 10), text_color="#10b981")
            self.status_dot.pack(side="left", padx=(0, 5))
            self.status_label = ctk.CTkLabel(self.status_frame, text="\u062c\u0627\u0647\u0638", font=("Segoe UI", 11), text_color="#e2e8f0")
            self.status_label.pack(side="left")
            self.count_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.count_frame.pack(side="right", padx=15, pady=8)
            self.char_label = ctk.CTkLabel(self.count_frame, text="\U0001f4dd 0", font=("Segoe UI", 11), text_color="#94a3b8")
            self.char_label.pack(side="right", padx=10)
            self.word_label = ctk.CTkLabel(self.count_frame, text="\U0001f4c4 0", font=("Segoe UI", 11), text_color="#94a3b8")
            self.word_label.pack(side="right", padx=10)

        def set_status(self, text, color="#10b981"):
            self.status_label.configure(text=text, text_color="#e2e8f0")
            self.status_dot.configure(text_color=color)

        def set_count(self, count, word_count=0):
            self.char_label.configure(text=f"\U0001f4dd {count}")
            self.word_label.configure(text=f"\U0001f4c4 {word_count}")

    class AnimatedButton(ctk.CTkButton):
        def __init__(self, master, color=None, **kwargs):
            super().__init__(master, **kwargs)
            self.configure(corner_radius=10, border_width=0, font=("Segoe UI", 14, "bold"), height=45)

    class ExplanationCard(ctk.CTkFrame):
        def __init__(self, master, code_line, explanation, index=0, **kwargs):
            super().__init__(master, fg_color="#12121a", corner_radius=10, border_width=1, border_color="#2a2a35", **kwargs)
            content = ctk.CTkFrame(self, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=10)
            if code_line.strip():
                ctk.CTkLabel(content, text=code_line, font=("Cascadia Code", 12), text_color="#ffffff", anchor="w", wraplength=400).pack(fill="x", pady=(0, 5))
            if explanation.strip():
                ctk.CTkLabel(content, text=explanation, font=("Segoe UI", 13), text_color="#e2e8f0", anchor="w", wraplength=400).pack(fill="x")

    class CodeBlock(ctk.CTkFrame):
        def __init__(self, master, code_text, **kwargs):
            super().__init__(master, fg_color="#1a1a25", corner_radius=10, **kwargs)
            self.code_text = ctk.CTkTextbox(self, font=("Cascadia Code", 12), fg_color="transparent", text_color="#ffffff", wrap="word")
            self.code_text.pack(fill="both", expand=True, padx=10, pady=10)
            self.code_text.insert("1.0", code_text)
            self.code_text.configure(state="disabled")


THEMES = {
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


class CryptoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.lang = "AR"
        self.current_cipher = "Caesar"
        self.operations_count = 0
        self.current_theme_name = "Midnight"
        self._T = THEMES[self.current_theme_name]

        self.title(TRANSLATIONS[self.lang]["title"])
        self.geometry("1400x900")
        self.minsize(1200, 700)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cryptoedu.ico")
        try:
            self.iconbitmap(icon_path)
        except Exception:
            pass

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self._crypto_built = False
        self._code_built = False
        self._code_cache = {}
        self._analysis_build_after = None
        self._analysis_defer_after = None
        self.setup_sidebar()
        self.setup_main_content()
        self.setup_crypto_tab()
        self.setup_code_tab()
        self.setup_status_bar()
        self._build_analysis_page()
        self._crypto_built = True
        self._code_built = True

    def _apply_theme(self, theme_name=None):
        if theme_name:
            self.current_theme_name = theme_name
        self._T = THEMES[self.current_theme_name]

        try:
            self.configure(fg_color=self._T["BG_DARK"])
        except Exception:
            pass

        try:
            self.sidebar.configure(fg_color=self._T["BG_SIDEBAR"])
        except Exception:
            pass

        try:
            self.main_frame.configure(fg_color=self._T["BG_DARK"])
        except Exception:
            pass

        self._apply_theme_sidebar()
        self._apply_theme_crypto_tab()
        self._apply_theme_code_tab()

    def _apply_theme_sidebar(self):
        T = self._T
        try:
            self.icon_bg.configure(fg_color=T["PRIMARY"])
        except Exception:
            pass
        try:
            self.logo.configure(text_color=T["TEXT_WHITE"])
        except Exception:
            pass
        try:
            self.author.configure(text_color=T["TEXT_MUTED"])
        except Exception:
            pass
        try:
            self.lang_btn.configure(
                selected_color=T["PRIMARY"],
                selected_hover_color=T["PRIMARY_LIGHT"],
                unselected_color=T["BG_CARD"],
                unselected_hover_color=T["BG_CARD_HOVER"]
            )
        except Exception:
            pass
        try:
            self.theme_menu.configure(
                fg_color=T["PRIMARY"],
                button_color=T["PRIMARY_DARK"],
                button_hover_color=T["PRIMARY_LIGHT"],
                dropdown_fg_color=T["BG_CARD"],
                dropdown_hover_color=T["BG_CARD_HOVER"]
            )
        except Exception:
            pass
        try:
            self.cipher_menu.configure(
                fg_color=T["PRIMARY"],
                button_color=T["PRIMARY_DARK"],
                button_hover_color=T["PRIMARY_LIGHT"],
                dropdown_fg_color=T["BG_CARD"],
                dropdown_hover_color=T["BG_CARD_HOVER"]
            )
        except Exception:
            pass
        try:
            self.cipher_info_card.configure(fg_color=T["BG_CARD"], border_color=T["BORDER_COLOR"])
            self.cipher_info_label.configure(text_color=T["TEXT_LIGHT"])
        except Exception:
            pass
        try:
            self.author_card.configure(fg_color=T["BG_CARD"], border_color=T["BORDER_COLOR"])
        except Exception:
            pass
        try:
            self.operations_card.configure(fg_color=T["BG_CARD"])
            self.ops_label.configure(text_color=T["TEXT_GRAY"])
        except Exception:
            pass
        try:
            self.status_bar.configure(fg_color=T["BG_CARD"])
        except Exception:
            pass

    def _apply_theme_crypto_tab(self):
        T = self._T
        try:
            if self._current_tab == "crypto":
                self._tab_btn_crypto.configure(fg_color=T["PRIMARY"], text_color="#ffffff", border_color="transparent")
                self._tab_btn_code.configure(fg_color="transparent", text_color=T["TEXT_GRAY"], border_color=T["BORDER_COLOR"])
            else:
                self._tab_btn_code.configure(fg_color=T["PRIMARY"], text_color="#ffffff", border_color="transparent")
                self._tab_btn_crypto.configure(fg_color="transparent", text_color=T["TEXT_GRAY"], border_color=T["BORDER_COLOR"])
        except Exception:
            pass
        try:
            self.cipher_title_label.configure(text_color=T["TEXT_WHITE"])
            self.cipher_desc_label.configure(text_color=T["TEXT_GRAY"])
        except Exception:
            pass

        for card_attr in ['_input_card', '_output_card', '_key_card']:
            try:
                card = getattr(self, card_attr)
                card.configure(fg_color=T["BG_CARD"], border_color=T["BORDER_COLOR"])
            except Exception:
                pass

        for box_attr in ['input_box', 'output_box']:
            try:
                box = getattr(self, box_attr)
                box.configure(fg_color=T["BG_INPUT"], border_color=T["BORDER_COLOR"])
            except Exception:
                pass

        try:
            self.encrypt_btn.configure(fg_color=T["SUCCESS"], hover_color="#34d399")
        except Exception:
            pass
        try:
            self.decrypt_btn.configure(fg_color=T["WARNING"], hover_color="#fbbf24")
        except Exception:
            pass
        try:
            self.copy_btn.configure(fg_color="#6366f1", hover_color=T["PRIMARY"])
        except Exception:
            pass
        try:
            self.clear_btn.configure(fg_color=T["ERROR"], hover_color="#f87171")
        except Exception:
            pass
        try:
            self.swap_btn.configure(fg_color=T["SECONDARY"], hover_color=T["PRIMARY_LIGHT"])
        except Exception:
            pass

    def _apply_theme_code_tab(self):
        T = self._T
        try:
            self.code_display.configure(fg_color=T.get("BG_CODE", T["BG_INPUT"]), border_color=T["BORDER_COLOR"])
        except Exception:
            pass
        try:
            self.line_numbers.configure(fg_color=T.get("BG_LINENUM", "#0c0c12"))
        except Exception:
            pass
        try:
            self.expl_display.configure(fg_color=T["BG_INPUT"], border_color=T["BORDER_COLOR"])
        except Exception:
            pass

    def setup_sidebar(self):
        T = self._T
        self.sidebar = ctk.CTkFrame(
            self,
            width=AppSizes.SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=T["BG_SIDEBAR"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.configure(width=AppSizes.SIDEBAR_WIDTH)

        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(25, 5))

        self.icon_bg = ctk.CTkFrame(logo_frame, fg_color=T["PRIMARY"], corner_radius=20, width=60, height=60)
        self.icon_bg.pack(pady=(0, 10))
        self.icon_bg.pack_propagate(False)
        ctk.CTkLabel(self.icon_bg, text="\U0001f510", font=("Segoe UI", 28)).pack(expand=True)

        self.logo = ctk.CTkLabel(
            logo_frame,
            text="CryptoEdu",
            font=("Segoe UI", 24, "bold"),
            text_color=T["TEXT_WHITE"]
        )
        self.logo.pack()

        self.author_card = ctk.CTkFrame(
            self.sidebar,
            fg_color=T["BG_CARD"],
            corner_radius=10,
            border_width=1,
            border_color=T["BORDER_COLOR"]
        )
        self.author_card.pack(pady=(8, 20), padx=20, fill="x")
        self.author = ctk.CTkLabel(
            self.author_card,
            text=TRANSLATIONS[self.lang]["author"],
            font=("Segoe UI", 16, "bold"),
            text_color=T["PRIMARY_LIGHT"]
        )
        self.author.pack(padx=12, pady=10)

        ctk.CTkFrame(self.sidebar, height=1, fg_color=T["BORDER_COLOR"]).pack(fill="x", padx=20, pady=10)

        lang_section = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        lang_section.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            lang_section,
            text="\U0001f310 " + TRANSLATIONS[self.lang]["language"],
            font=("Segoe UI", 11),
            text_color=T["TEXT_GRAY"]
        ).pack(anchor="w", pady=(0, 8))

        self.lang_btn = ctk.CTkSegmentedButton(
            lang_section,
            values=["AR", "EN"],
            command=self.change_language,
            font=("Segoe UI", 14, "bold"),
            selected_color=T["PRIMARY"],
            selected_hover_color=T["PRIMARY_LIGHT"],
            unselected_color=T["BG_CARD"],
            unselected_hover_color=T["BG_CARD_HOVER"],
            height=40
        )
        self.lang_btn.set(self.lang)
        self.lang_btn.pack(fill="x")

        ctk.CTkFrame(self.sidebar, height=1, fg_color=T["BORDER_COLOR"]).pack(fill="x", padx=20, pady=10)

        theme_section = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_section.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(
            theme_section,
            text="\U0001f3a8 Theme",
            font=("Segoe UI", 11),
            text_color=T["TEXT_GRAY"]
        ).pack(anchor="w", pady=(0, 8))

        self.theme_menu = ctk.CTkOptionMenu(
            theme_section,
            values=list(THEMES.keys()),
            command=self.change_theme,
            font=("Segoe UI", 14, "bold"),
            fg_color=T["PRIMARY"],
            button_color=T["PRIMARY_DARK"],
            button_hover_color=T["PRIMARY_LIGHT"],
            dropdown_fg_color=T["BG_CARD"],
            dropdown_hover_color=T["BG_CARD_HOVER"],
            height=40
        )
        self.theme_menu.set(self.current_theme_name)
        self.theme_menu.pack(fill="x")

        ctk.CTkFrame(self.sidebar, height=1, fg_color=T["BORDER_COLOR"]).pack(fill="x", padx=20, pady=10)

        cipher_section = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        cipher_section.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(
            cipher_section,
            text="\u2699\ufe0f " + TRANSLATIONS[self.lang]["select_cipher"],
            font=("Segoe UI", 11),
            text_color=T["TEXT_GRAY"]
        ).pack(anchor="w", pady=(0, 8))

        self.cipher_menu = ctk.CTkOptionMenu(
            cipher_section,
            values=["Caesar", "Affine", "Vigenere", "Playfair", "Hill", "DiffieHellman", "RSA", "SDES", "DES"],
            command=self.change_cipher,
            font=("Segoe UI", 14, "bold"),
            fg_color=T["PRIMARY"],
            button_color=T["PRIMARY_DARK"],
            button_hover_color=T["PRIMARY_LIGHT"],
            dropdown_fg_color=T["BG_CARD"],
            dropdown_hover_color=T["BG_CARD_HOVER"],
            height=40
        )
        self.cipher_menu.set(self.current_cipher)
        self.cipher_menu.pack(fill="x")

        self.cipher_info_card = ctk.CTkFrame(
            self.sidebar,
            fg_color=T["BG_CARD"],
            corner_radius=AppSizes.CARD_RADIUS,
            border_width=1,
            border_color=T["BORDER_COLOR"]
        )
        self.cipher_info_card.pack(pady=15, padx=20, fill="x")

        self.cipher_info_label = ctk.CTkLabel(
            self.cipher_info_card,
            text=TRANSLATIONS[self.lang][f"desc_{self.current_cipher.lower()}"],
            font=("Segoe UI", 11),
            text_color=T["TEXT_LIGHT"],
            wraplength=220,
            justify="right" if self.lang == "AR" else "left"
        )
        self.cipher_info_label.pack(padx=15, pady=15)

        stats_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        stats_frame.pack(pady=10, padx=20, fill="x")

        self.operations_card = ctk.CTkFrame(stats_frame, fg_color=T["BG_CARD"], corner_radius=8)
        self.operations_card.pack(fill="x", pady=5)

        ctk.CTkLabel(self.operations_card, text="\U0001f4ca", font=("Segoe UI", 14)).pack(side="left", padx=10, pady=8)
        ops_text = "عمليات" if self.lang == "AR" else "operations"
        self.ops_label = ctk.CTkLabel(self.operations_card, text=f"0 {ops_text}", font=("Segoe UI", 11), text_color=T["TEXT_GRAY"])
        self.ops_label.pack(side="left", pady=8)

        # === زر الاختبار السريع ===
        test_btn = ctk.CTkButton(
            stats_frame,
            text="\U0001f9ea " + ("اختبار سريع" if self.lang == "AR" else "Quick Test"),
            command=self._quick_test,
            font=("Segoe UI", 12, "bold"),
            fg_color=T["PRIMARY"],
            hover_color=T["PRIMARY_LIGHT"],
            corner_radius=8,
            height=35
        )
        test_btn.pack(fill="x", pady=5)

        # === سجل العمليات ===
        self.history_frame = ctk.CTkFrame(stats_frame, fg_color=T["BG_CARD"], corner_radius=8)
        self.history_frame.pack(fill="x", pady=5)

        history_header = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        history_header.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(history_header, text="\U0001f4cb " + ("السجل" if self.lang == "AR" else "History"), font=("Segoe UI", 11, "bold"), text_color=T["TEXT_LIGHT"]).pack(side="left")
        self.history_clear_btn = ctk.CTkButton(history_header, text="\U0001f5d1\ufe0f", width=25, height=25, font=("Segoe UI", 10), fg_color="transparent", hover_color=T["ERROR"], command=self._clear_history)
        self.history_clear_btn.pack(side="right")

        self.history_list_frame = ctk.CTkScrollableFrame(self.history_frame, fg_color=T["BG_INPUT"], corner_radius=6, height=120)
        self.history_list_frame.pack(fill="x", padx=8, pady=(0, 8))

        self.history_items = []

        # === زر المساعدة ===
        help_btn = ctk.CTkButton(
            stats_frame,
            text="\u2753 " + ("مساعدة" if self.lang == "AR" else "Help"),
            command=self._show_help,
            font=("Segoe UI", 12, "bold"),
            fg_color=T["ACCENT"],
            hover_color=T["WARNING_LIGHT"],
            corner_radius=8,
            height=35
        )
        help_btn.pack(fill="x", pady=5)

    def setup_main_content(self):
        T = self._T
        self.main_frame = ctk.CTkFrame(self, fg_color=T["BG_DARK"], corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        tab_bar = ctk.CTkFrame(self.main_frame, fg_color=T["BG_CARD"], corner_radius=AppSizes.CARD_RADIUS, height=42)
        tab_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(12, 0))
        tab_bar.grid_columnconfigure(0, weight=1)
        tab_bar.grid_columnconfigure(1, weight=1)
        tab_bar.grid_propagate(False)

        tab_labels = TRANSLATIONS[self.lang]

        self._tab_btn_crypto = ctk.CTkButton(
            tab_bar,
            text="\U0001f510  " + tab_labels["tab_crypto"],
            font=("Segoe UI", 13, "bold"),
            fg_color=T["PRIMARY"],
            hover_color=T["PRIMARY_LIGHT"],
            text_color="#ffffff",
            corner_radius=10,
            height=30,
            command=lambda: self._switch_tab("crypto")
        )
        self._tab_btn_crypto.grid(row=0, column=0, sticky="ew", padx=(8, 4), pady=6)

        self._tab_btn_code = ctk.CTkButton(
            tab_bar,
            text="\U0001f4dd  " + tab_labels["tab_code"],
            font=("Segoe UI", 13, "bold"),
            fg_color="transparent",
            hover_color=T["BG_CARD_HOVER"],
            text_color=T["TEXT_GRAY"],
            corner_radius=10,
            height=30,
            border_width=2,
            border_color=T["BORDER_COLOR"],
            command=lambda: self._switch_tab("code")
        )
        self._tab_btn_code.grid(row=0, column=1, sticky="ew", padx=(4, 8), pady=6)

        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(8, 12))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        self.tab_crypto = ctk.CTkScrollableFrame(content_frame, fg_color="transparent", scrollbar_button_color=T["BORDER_COLOR"], scrollbar_button_hover_color=T["PRIMARY"])
        self.tab_code = ctk.CTkFrame(content_frame, fg_color="transparent")

        self.tab_crypto.grid(row=0, column=0, sticky="nsew")
        self.tab_code.grid(row=0, column=0, sticky="nsew")
        self.tab_code.grid_remove()

        self._current_tab = "crypto"

    def _switch_tab(self, tab_name):
        T = self._T
        if tab_name == getattr(self, "_current_tab", None):
            return
        if tab_name == "crypto":
            self.tab_code.grid_remove()
            self.tab_crypto.grid(row=0, column=0, sticky="nsew")
            self._tab_btn_crypto.configure(fg_color=T["PRIMARY"], text_color="#ffffff", border_width=0)
            self._tab_btn_code.configure(fg_color="transparent", text_color=T["TEXT_GRAY"], border_width=2, border_color=T["BORDER_COLOR"])
        else:
            self.tab_crypto.grid_remove()
            self.tab_code.grid(row=0, column=0, sticky="nsew")
            self._tab_btn_code.configure(fg_color=T["PRIMARY"], text_color="#ffffff", border_width=0)
            self._tab_btn_crypto.configure(fg_color="transparent", text_color=T["TEXT_GRAY"], border_width=2, border_color=T["BORDER_COLOR"])
        self._current_tab = tab_name
        # ensure visible canvas is updated without blocking
        self.update_idletasks()

    def setup_crypto_tab(self):
        if getattr(self, '_crypto_built', False):
            self._update_crypto_labels()
            return
        T = self._T
        t = TRANSLATIONS[self.lang]

        for widget in self.tab_crypto.winfo_children():
            widget.destroy()

        header_frame = ctk.CTkFrame(self.tab_crypto, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(20, 10))
        self._header_frame = header_frame

        cipher_name = t[self.current_cipher.lower()]

        title_icon = ctk.CTkFrame(header_frame, fg_color=T["PRIMARY"], corner_radius=12, width=50, height=50)
        title_icon.pack(side="left")
        title_icon.pack_propagate(False)
        ctk.CTkLabel(title_icon, text="\U0001f510", font=("Segoe UI", 24)).pack(expand=True)

        title_text_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_text_frame.pack(side="left", padx=15)

        self.cipher_title_label = ctk.CTkLabel(
            title_text_frame,
            text=cipher_name,
            font=("Segoe UI", 22, "bold"),
            text_color=T["TEXT_WHITE"]
        )
        self.cipher_title_label.pack(anchor="w")

        self.cipher_desc_label = ctk.CTkLabel(
            title_text_frame,
            text=t[f"desc_{self.current_cipher.lower()}"],
            font=("Segoe UI", 11),
            text_color=T["TEXT_GRAY"]
        )
        self.cipher_desc_label.pack(anchor="w")

        self.security_notice_label = ctk.CTkLabel(
            title_text_frame,
            text=self._L(
                "⚠ تعليمي فقط — لا تستخدم هذه الخوارزميات لحماية بيانات حقيقية",
                "⚠ Educational only — do not use these algorithms to protect real data"
            ),
            font=("Segoe UI", 10, "bold"),
            text_color=T["WARNING_LIGHT"]
        )
        self.security_notice_label.pack(anchor="w", pady=(3, 0))

        self._input_card = ctk.CTkFrame(self.tab_crypto, fg_color=T["BG_CARD"], corner_radius=AppSizes.CARD_RADIUS, border_width=1, border_color=T["BORDER_COLOR"])
        self._input_card.pack(fill="both", expand=True, padx=25, pady=10)

        input_header = ctk.CTkFrame(self._input_card, fg_color="transparent")
        input_header.pack(fill="x", padx=15, pady=(15, 5))

        self.input_label = ctk.CTkLabel(
            input_header,
            text="\U0001f4dd " + t["input_text"],
            font=("Segoe UI", 14, "bold"),
            text_color=T["TEXT_LIGHT"]
        )
        self.input_label.pack(side="left")

        self.input_char_count = ctk.CTkLabel(
            input_header,
            text="0",
            font=("Segoe UI", 24, "bold"),
            text_color=T["PRIMARY"]
        )
        self.input_char_count.pack(side="right")

        self.input_box = ctk.CTkTextbox(
            self._input_card,
            height=120,
            font=("Segoe UI", 14),
            fg_color=T["BG_INPUT"],
            border_width=2,
            border_color=T["BORDER_COLOR"],
            corner_radius=10,
            wrap="word"
        )
        self.input_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.input_box.bind("<KeyRelease>", self.update_char_count)
        self.input_box.bind("<KeyRelease>", lambda e: self._close_analysis_page(), add="+")

        self._key_card = ctk.CTkFrame(self.tab_crypto, fg_color=T["BG_CARD"], corner_radius=AppSizes.CARD_RADIUS, border_width=1, border_color=T["BORDER_COLOR"])
        self._key_card.pack(fill="x", padx=25, pady=10)

        key_header = ctk.CTkFrame(self._key_card, fg_color="transparent")
        key_header.pack(fill="x", padx=15, pady=(15, 10))

        self.key_label = ctk.CTkLabel(
            key_header,
            text="\U0001f511 " + t["key"],
            font=("Segoe UI", 14, "bold"),
            text_color=T["TEXT_LIGHT"]
        )
        self.key_label.pack(side="left")

        self.key_frame = ctk.CTkFrame(self._key_card, fg_color="transparent")
        self.key_frame.pack(fill="x", padx=15, pady=(0, 15))
        self.update_keys()

        btn_frame = ctk.CTkFrame(self.tab_crypto, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=10)

        main_btn_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        main_btn_frame.pack(fill="x")

        self.encrypt_btn = ctk.CTkButton(
            main_btn_frame,
            text="\U0001f512 " + t["encrypt"],
            command=self.run_encrypt,
            width=180,
            height=AppSizes.BUTTON_HEIGHT,
            font=("Segoe UI", 14, "bold"),
            fg_color=T["SUCCESS"],
            hover_color="#34d399",
            corner_radius=AppSizes.BUTTON_RADIUS
        )
        self.encrypt_btn.pack(side="left", padx=(0, 10))

        self.decrypt_btn = ctk.CTkButton(
            main_btn_frame,
            text="\U0001f513 " + t["decrypt"],
            command=self.run_decrypt,
            width=180,
            height=AppSizes.BUTTON_HEIGHT,
            font=("Segoe UI", 14, "bold"),
            fg_color=T["WARNING"],
            hover_color="#fbbf24",
            corner_radius=AppSizes.BUTTON_RADIUS
        )
        self.decrypt_btn.pack(side="left", padx=(0, 10))

        self.analysis_btn = ctk.CTkButton(
            main_btn_frame,
            text="\U0001f50d " + t["analysis"],
            command=self._show_analysis,
            width=130,
            height=AppSizes.BUTTON_HEIGHT,
            font=("Segoe UI", 13, "bold"),
            fg_color=T["SECONDARY"],
            hover_color=T["PRIMARY_LIGHT"],
            corner_radius=AppSizes.BUTTON_RADIUS
        )
        self.analysis_btn.pack(side="left", padx=(0, 10))

        ctk.CTkFrame(main_btn_frame, width=2, height=30, fg_color=T["BORDER_COLOR"]).pack(side="left", padx=10)

        self.copy_btn = ctk.CTkButton(
            main_btn_frame,
            text="\U0001f4cb " + t["copy"],
            command=self.copy_result,
            width=120,
            height=AppSizes.BUTTON_HEIGHT,
            font=("Segoe UI", 14, "bold"),
            fg_color="#6366f1",
            hover_color=T["PRIMARY"],
            corner_radius=AppSizes.BUTTON_RADIUS
        )
        self.copy_btn.pack(side="left", padx=(0, 10))

        self.clear_btn = ctk.CTkButton(
            main_btn_frame,
            text="\U0001f5d1\ufe0f " + t["clear"],
            command=self.clear_texts,
            width=120,
            height=AppSizes.BUTTON_HEIGHT,
            font=("Segoe UI", 14, "bold"),
            fg_color=T["ERROR"],
            hover_color="#f87171",
            corner_radius=AppSizes.BUTTON_RADIUS
        )
        self.clear_btn.pack(side="left")

        self.swap_btn = ctk.CTkButton(
            main_btn_frame,
            text="\U0001f504",
            command=self.swap_texts,
            width=40,
            height=AppSizes.BUTTON_HEIGHT,
            font=("Segoe UI", 16),
            fg_color=T["SECONDARY"],
            hover_color=T["PRIMARY_LIGHT"],
            corner_radius=AppSizes.BUTTON_RADIUS
        )
        self.swap_btn.pack(side="right")

        ctk.CTkLabel(
            main_btn_frame,
            text="\u2194",
            font=("Segoe UI", 16),
            text_color=T["TEXT_GRAY"]
        ).pack(side="right", padx=5)

        self._output_card = ctk.CTkFrame(self.tab_crypto, fg_color=T["BG_CARD"], corner_radius=AppSizes.CARD_RADIUS, border_width=1, border_color=T["BORDER_COLOR"])
        self._output_card.pack(fill="both", expand=True, padx=25, pady=10)

        output_header = ctk.CTkFrame(self._output_card, fg_color="transparent")
        output_header.pack(fill="x", padx=15, pady=(15, 5))

        self.output_label = ctk.CTkLabel(
            output_header,
            text="\u2728 " + t["output_text"],
            font=("Segoe UI", 14, "bold"),
            text_color=T["TEXT_LIGHT"]
        )
        self.output_label.pack(side="left")

        self.output_box = ctk.CTkTextbox(
            self._output_card,
            height=170,
            font=("Segoe UI", 14),
            fg_color=T["BG_INPUT"],
            border_width=2,
            border_color=T["BORDER_COLOR"],
            corner_radius=10,
            wrap="word"
        )
        self.output_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self._build_analysis_section()

    def _build_analysis_section(self):
        """زر تحليل أنيق بجانب اسم التشفير — يظهر فقط بعد تنفيذ تشفير/فك تشفير."""
        T = self._T
        bar = ctk.CTkFrame(self._header_frame, fg_color=T["BG_CARD"], corner_radius=12, border_width=1, border_color=T["BORDER_COLOR"])
        bar.pack(side="right", padx=(15, 0), pady=4)

        ctk.CTkLabel(
            bar,
            text=self._L("\U0001f50d  تحليل التشفير", "\U0001f50d  Analysis"),
            font=("Segoe UI", 12, "bold"),
            text_color=T["PRIMARY_LIGHT"]
        ).pack(side="left", padx=(14, 6), pady=8)

        self.analysis_btn_bar = ctk.CTkButton(
            bar,
            text=self._L("عرض", "View"),
            font=("Segoe UI", 12, "bold"),
            fg_color=T["PRIMARY"],
            hover_color=T["PRIMARY_LIGHT"],
            text_color="#ffffff",
            corner_radius=9,
            height=34,
            width=74,
            command=self._show_analysis
        )
        self.analysis_btn_bar.pack(side="right", padx=6, pady=6)
        # مخفي حتى يعمل التشفير/فك التشفير أول مرة
        bar.pack_forget()
        self._analysis_bar = bar
        self.analysis_expanded = False

    def _L(self, ar, en):
        return en if self.lang == "EN" else fix_bidi(ar)

    def _fb(self, text):
        """Fix bidirectional text for Arabic. Use for direct Arabic strings outside _L."""
        if self.lang == "AR":
            return fix_bidi(text)
        return text

    def _build_analysis_page(self):
        """صفحة منفصلة كاملة لعرض التحليل — تخفي كل شيء وتقدم التحليل فقط مع زر عودة."""
        T = self._T
        page = ctk.CTkFrame(self, fg_color=T["BG_DARK"], corner_radius=0)
        page.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        page.grid_remove()

        header = ctk.CTkFrame(page, fg_color=T["BG_CARD"], corner_radius=0, height=64)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)

        self.analysis_page_back = ctk.CTkButton(
            header,
            text="\u2190  " + self._L("العودة إلى التشفير", "Back to Encryption"),
            font=("Segoe UI", 13, "bold"),
            fg_color=T["SECONDARY"],
            hover_color=T["PRIMARY_LIGHT"],
            text_color="#ffffff",
            corner_radius=10,
            height=38,
            command=self._close_analysis_page
        )
        self.analysis_page_back.grid(row=0, column=0, sticky="w", padx=(20, 0), pady=13)

        self.analysis_page_title = ctk.CTkLabel(
            header,
            text=self._L("\U0001f50d  تحليل التشفير — خطوة بخطوة", "\U0001f50d  Encryption Analysis — Step by Step"),
            font=("Segoe UI", 16, "bold"),
            text_color=T["PRIMARY_LIGHT"]
        )
        self.analysis_page_title.grid(row=0, column=1, sticky="e", padx=16)

        self.analysis_scroll = ctk.CTkScrollableFrame(
            page,
            fg_color="transparent",
            scrollbar_button_color=T["BORDER_COLOR"],
            scrollbar_button_hover_color=T["PRIMARY"]
        )
        self.analysis_scroll.grid(row=1, column=0, sticky="nsew")
        self.analysis_scroll.grid_columnconfigure(0, weight=1)
        # محتوى يملأ عرض الصفحة بالكامل مع هوامش مريحة لكي يتمدد تحليل التشفير ويبدو فخماً
        self.analysis_content = ctk.CTkFrame(self.analysis_scroll, fg_color="transparent", corner_radius=0)
        self.analysis_content.grid(row=0, column=0, sticky="nsew", padx=28, pady=(20, 40))
        self.analysis_content.grid_columnconfigure(0, weight=1)

        self.analysis_page = page

    def _open_analysis_page(self):
        if not getattr(self, "_analysis_ready", False):
            self.status_bar.set_status(
                "\u26a0\ufe0f " + ("\u0642\u0645 \u0628\u0639\u0645\u0644\u064a\u0629 \u062a\u0634\u0641\u064a\u0631 \u0623\u0648\u0644\u0627\u064b!" if self.lang == "AR" else "Run an encryption operation first!"),
                "#f59e0b"
            )
            return
        page = self.analysis_page
        page.grid()
        page.tkraise()
        self.analysis_page_title.configure(
            text=("\U0001f50d  " + self._L("تحليل التشفير", "Encryption Analysis") + " — " + self.current_cipher)
        )
        # بعد الفتح ننتظر التخطيط ثم ننزل لأعلى/أسفل حسب اللغة
        self.after(120, lambda: self._scroll_analysis_page())

    def _close_analysis_page(self):
        self.analysis_page.grid_remove()
        if hasattr(self, '_output_card'):
            try: self._output_card.update_idletasks()
            except Exception: pass

    def _scroll_analysis_page(self):
        try:
            # إبقاء أعلى الصفحة ظاهراً عند الفتح
            self.analysis_scroll._parent_canvas.yview_moveto(0.0)
        except Exception:
            pass

    def _show_analysis(self):
        self._open_analysis_page()

    def _cancel_deferred_analysis(self):
        # يلغي الاستدعاء المؤجل لبناء التحليل (race عند تغيير التشفير السريع)
        dn = getattr(self, "_analysis_defer_after", None)
        if dn:
            try: self.after_cancel(dn)
            except: pass
            self._analysis_defer_after = None

    def _schedule_analysis(self, text, result, operation):
        self._cancel_deferred_analysis()
        # التحليل يبني عناصر Tkinter كثيرة؛ النتيجة الكاملة تبقى محفوظة،
        # بينما نحلل جزءًا محدودًا فقط للحفاظ على سرعة الواجهة.
        analysis_text = text[:100]
        analysis_result = result[:100]
        self._analysis_defer_after = self.after(
            30, lambda t=analysis_text, r=analysis_result, op=operation: self._update_analysis(t, r, op)
        )

    def _update_analysis(self, input_text, output_text, operation):
        # cancel the now-running deferred callback + any pending chunked wheel builds
        self._cancel_deferred_analysis()
        if getattr(self, "_analysis_build_after", None):
            try: self.after_cancel(self._analysis_build_after)
            except: pass
            self._analysis_build_after = None
        for w in self.analysis_content.winfo_children():
            w.destroy()

        cipher = self.current_cipher
        T = self._T
        op_ar = (self._L("التشفير", "Encryption") if operation == "encrypt" else self._L("فك التشفير", "Decryption"))

        if cipher == "Caesar":
            self._analyze_caesar(input_text, operation)
        elif cipher == "Affine":
            self._analyze_affine(input_text, operation)
        elif cipher == "Vigenere":
            self._analyze_vigenere(input_text, operation)
        elif cipher == "Playfair":
            self._analyze_playfair(input_text, operation)
        elif cipher == "Hill":
            self._analyze_hill(input_text, operation)
        elif cipher == "DiffieHellman":
            self._analyze_diffiehellman(input_text, output_text)
        elif cipher == "RSA":
            self._analyze_rsa(input_text, output_text, operation)
        elif cipher == "SDES":
            self._analyze_sdes(input_text, output_text, operation)
        elif cipher == "DES":
            self._analyze_des(input_text, output_text, operation)
        else:
            self._analysis_hero(self._L("\U0001f4dd العملية", "\U0001f4dd Operation"), f"{operation}: {cipher}", T["PRIMARY"], "\U0001f4dd")

        self.analysis_page_title.configure(
            text="\U0001f50d  " + self._L("تحليل التشفير", "Encryption Analysis") + " — " + cipher
        )
        self._analysis_ready = True
        # أظهر زر التحليل بجانب اسم التشفير بعد نجاح العملية
        try:
            self._analysis_bar.pack(side="right", padx=(15, 0), pady=4, before=self._analysis_bar.master.winfo_children()[0] if self._analysis_bar.master.winfo_children() else None)
        except Exception:
            try:
                self._analysis_bar.pack(side="right", padx=(15, 0), pady=4)
            except Exception:
                pass

    def _scroll_analysis_into_view(self):
        try:
            self.tab_crypto._parent_canvas.yview_moveto(0.0)
        except Exception:
            pass

    def _analysis_hero(self, title, subtitle, color, icon):
        T = self._T
        hero = ctk.CTkFrame(self.analysis_content, fg_color=color, corner_radius=12, height=66)
        hero.pack(fill="x", pady=8, padx=6)
        hero.pack_propagate(False)
        ctk.CTkLabel(
            hero,
            text=f"{icon}  {title}",
            font=("Segoe UI", 15, "bold"),
            text_color="#ffffff",
            anchor="w"
        ).pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(
            hero,
            text=subtitle,
            font=("Segoe UI", 11),
            text_color="#ffffff",
            anchor="w",
            wraplength=1600
        ).pack(fill="x", padx=16, pady=(0, 6))

    def _analysis_card(self, color, left_box=None, formula=None):
        T = self._T
        card = ctk.CTkFrame(self.analysis_content, fg_color=T["BG_CARD"], corner_radius=12, border_width=1, border_color=T["BORDER_COLOR"])
        card.pack(fill="x", pady=4, padx=6)
        card.bind("<Enter>", lambda e, c=card, col=color: c.configure(border_color=col, border_width=2))
        card.bind("<Leave>", lambda e, c=card: c.configure(border_color=T["BORDER_COLOR"], border_width=1))
        if left_box is not None:
            left_box.pack(side="left", padx=10, pady=8)
        if formula:
            ctk.CTkLabel(
                card,
                text=formula,
                font=("Cascadia Code", 11, "bold"),
                text_color=T["TEXT_LIGHT"],
                anchor="e",
                justify="left",
                wraplength=340
            ).pack(side="right", padx=12, pady=8)
        return card

    def _analysis_tile(self, parent, text, color, sub=None, size=20, width=48, height=50):
        T = self._T
        tile = ctk.CTkFrame(parent, fg_color=color, corner_radius=8, width=width, height=height)
        tile.pack(side="left", padx=3)
        tile.pack_propagate(False)
        ctk.CTkLabel(tile, text=str(text), font=("Segoe UI", size, "bold"), text_color="#ffffff").pack(expand=True)
        if sub:
            ctk.CTkLabel(parent, text=str(sub), font=("Cascadia Code", 9), text_color=T["TEXT_GRAY"], width=40).pack(side="left", padx=2)
        return tile

    def _analysis_arrow(self, parent, color):
        ctk.CTkLabel(parent, text="\u2192", font=("Segoe UI", 18, "bold"), text_color=color, width=26).pack(side="left", padx=2)

    def _analysis_chips(self, items):
        T = self._T
        frame = ctk.CTkFrame(self.analysis_content, fg_color="transparent")
        frame.pack(fill="x", padx=6, pady=4)
        for label, value, color, icon in items:
            chip = ctk.CTkFrame(frame, fg_color=T["BG_INPUT"], corner_radius=8, border_width=1, border_color=T["BORDER_COLOR"])
            chip.pack(side="left", padx=4, pady=4)
            ctk.CTkLabel(chip, text=f"{icon} {label}", font=("Segoe UI", 10, "bold"), text_color=T["TEXT_GRAY"]).pack(padx=6, pady=(4, 0))
            ctk.CTkLabel(chip, text=str(value), font=("Cascadia Code", 14, "bold"), text_color=color).pack(padx=6, pady=(0, 4))

    def _matrix_grid(self, rows, highlight=None, base_color="#8b5cf6", cell=46):
        T = self._T
        frame = ctk.CTkFrame(self.analysis_content, fg_color=T["BG_INPUT"], corner_radius=10)
        frame.pack(fill="x", padx=6, pady=4)
        highlight = highlight or set()
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                color = base_color if (r, c) in highlight else T["BG_CARD"]
                txt = T["TEXT_LIGHT"]
                if (r, c) in highlight:
                    txt = "#ffffff"
                cell_w = ctk.CTkFrame(frame, fg_color=color, corner_radius=6, width=cell, height=40)
                cell_w.grid(row=r, column=c, padx=4, pady=4)
                cell_w.grid_propagate(False)
                ctk.CTkLabel(cell_w, text=str(val), font=("Segoe UI", 14, "bold"), text_color=txt).place(relx=0.5, rely=0.5, anchor="center")

    def _analysis_canvas(self, width, height):
        T = self._T
        canvas = ctk.CTkCanvas(
            self.analysis_content,
            width=width,
            height=height,
            bg=T["BG_INPUT"],
            highlightthickness=0,
            bd=0
        )
        canvas.pack(fill="x", padx=6, pady=4)
        return canvas

    def _analysis_note(self, text, color="#10b981", icon="\U0001f4a1"):
        T = self._T
        note = ctk.CTkFrame(self.analysis_content, fg_color=T["BG_INPUT"], corner_radius=10, border_width=1, border_color=color)
        note.pack(fill="x", padx=6, pady=4)
        ctk.CTkLabel(note, text=f"{icon}  {text}", font=("Segoe UI", 12), text_color=color, anchor="w", wraplength=1600, justify="left").pack(fill="x", padx=12, pady=8)

    # ---------- Caesar wheel (graphic) ----------
    def _caesar_wheel(self, plain_idx, res_idx, shift, color="#7c3aed", parent=None, compact=False, caption=None):
        parent = parent if parent is not None else self.analysis_content
        in_scroll = parent is not self.analysis_content or compact
        T = self._T
        if compact or in_scroll:
            # Beautiful enlarged wheel — bigger for clarity of letters & rotation
            W, H = 280, 260
            canvas = ctk.CTkCanvas(parent, width=W, height=H, bg=T["BG_INPUT"], highlightthickness=0, bd=0)
            canvas.pack(side="left", padx=6, pady=6) if in_scroll else canvas.pack(fill="x", padx=6, pady=4)
            cx, cy = 140, 112
            sc = 0.88  # scale factor vs the 360px original (enlarged for clarity)
            R, Rb, hub = int(132 * sc), int(100 * sc), int(48 * sc)
            step = 360 / 26
            def pos(i, r):
                a = math.radians(90 - i * step)
                return cx + r * math.cos(a), cy - r * math.sin(a)
            # background rings — scaled
            canvas.create_oval(cx - R, cy - R, cx + R, cy + R, fill="#171124", outline="#33284c", width=1)
            canvas.create_oval(cx - int(R * 0.77), cy - int(R * 0.77), cx + int(R * 0.77), cy + int(R * 0.77), fill="#0f0a1d", outline="")
            canvas.create_arc(cx - R + int(12 * sc), cy - R + int(12 * sc), cx + R - int(12 * sc), cy + R - int(12 * sc), start=210, extent=70, style="arc", outline="#40305f", width=max(2, int(6 * sc)))
            canvas.create_arc(cx - R + int(12 * sc), cy - R + int(12 * sc), cx + R - int(12 * sc), cy + R - int(12 * sc), start=30, extent=70, style="arc", outline="#241a3a", width=max(2, int(6 * sc)))
            canvas.create_oval(cx - Rb, cy - Rb, cx + Rb, cy + Rb, outline=color, width=2)
            for i in range(26):
                x, y = pos(i, Rb + int(13 * sc))
                x2, y2 = pos(i, Rb - int(13 * sc))
                canvas.create_line(x, y, x2, y2, fill="#2a2140", width=1)
                lx, ly = pos(i, Rb - int(32 * sc))
                canvas.create_text(lx, ly, text=chr(65 + i), font=("Segoe UI", 9, "bold"), fill="#8b84a8")
            px, py = pos(plain_idx, Rb + int(17 * sc))
            rx, ry = pos(res_idx, Rb + int(17 * sc))
            canvas.create_oval(px - 8, py - 8, px + 8, py + 8, fill=color, outline="#ffffff", width=1)
            canvas.create_text(px, py, text=chr(65 + plain_idx), font=("Segoe UI", 9, "bold"), fill="#ffffff")
            canvas.create_oval(rx - 9, ry - 9, rx + 9, ry + 9, fill="#34d399", outline="#ffffff", width=1)
            canvas.create_text(rx, ry, text=chr(65 + res_idx), font=("Segoe UI", 9, "bold"), fill="#06251a")
            # subtle arrow — scaled
            canvas.create_line(px - 4, py - 4, rx + 5, ry + 4, arrow="last", width=2, fill="#f472b6", smooth=True)
            canvas.create_oval(cx - hub, cy - hub, cx + hub, cy + hub, fill="#241a3a", outline=color, width=2)
            canvas.create_text(cx, cy - 9, text=f"{chr(65 + plain_idx)}{shift:+}", font=("Cascadia Code", 8, "bold"), fill="#a78bfa")
            canvas.create_text(cx, cy + 8, text=chr(65 + res_idx), font=("Segoe UI", 16, "bold"), fill="#ffffff")
            canvas.create_text(cx, cy + 22, text="mod 26", font=("Segoe UI", 8, "bold"), fill="#8b84a8")
            # caption drawn directly (saves a heavy CTkLabel per wheel)
            if caption:
                canvas.create_text(cx, H - 18, text=caption, font=("Segoe UI", 10, "bold"), fill=T["TEXT_LIGHT"])
            return canvas
        # Full-size wheel (legacy / single detailed view if needed)
        canvas = ctk.CTkCanvas(parent, width=360, height=320, bg=T["BG_INPUT"], highlightthickness=0, bd=0)
        canvas.pack(side="left", padx=8, pady=6) if in_scroll else canvas.pack(fill="x", padx=6, pady=4)
        cx, cy, R, Rb, hub = 180, 152, 130, 98, 46
        step = 360 / 26
        def pos(i, r):
            a = math.radians(90 - i * step)
            return cx + r * math.cos(a), cy - r * math.sin(a)
        canvas.create_oval(cx - R, cy - R, cx + R, cy + R, fill="#171124", outline="#33284c", width=2)
        canvas.create_oval(cx - R + 30, cy - R + 30, cx + R - 30, cy + R - 30, fill="#0f0a1d", outline="")
        canvas.create_arc(cx - R + 12, cy - R + 12, cx + R - 12, cy + R - 12, start=210, extent=70, style="arc", outline="#40305f", width=6)
        canvas.create_arc(cx - R + 12, cy - R + 12, cx + R - 12, cy + R - 12, start=30, extent=70, style="arc", outline="#241a3a", width=6)
        canvas.create_oval(cx - Rb, cy - Rb, cx + Rb, cy + Rb, outline=color, width=3)
        for i in range(26):
            x, y = pos(i, Rb + 12)
            x2, y2 = pos(i, Rb - 12)
            canvas.create_line(x, y, x2, y2, fill="#2a2140", width=2)
            lx, ly = pos(i, Rb - 30)
            canvas.create_text(lx, ly, text=chr(65 + i), font=("Segoe UI", 10, "bold"), fill="#8b84a8")
        px, py = pos(plain_idx, Rb + 16)
        rx, ry = pos(res_idx, Rb + 16)
        canvas.create_oval(px - 11, py - 11, px + 11, py + 11, fill=color, outline="#ffffff", width=2)
        canvas.create_text(px, py, text=chr(65 + plain_idx), font=("Segoe UI", 11, "bold"), fill="#ffffff")
        canvas.create_oval(rx - 13, ry - 13, rx + 13, ry + 13, fill="#34d399", outline="#ffffff", width=2)
        canvas.create_text(rx, ry, text=chr(65 + res_idx), font=("Segoe UI", 12, "bold"), fill="#06251a")
        canvas.create_line(px - 8, py - 8, rx + 10, ry + 8, arrow="last", width=4, fill="#f472b6", smooth=True, joinstyle="round")
        canvas.create_oval(cx - hub, cy - hub, cx + hub, cy + hub, fill="#241a3a", outline=color, width=3)
        canvas.create_text(cx, cy - 16, text=f"{chr(65 + plain_idx)} {shift:+}", font=("Cascadia Code", 12, "bold"), fill="#a78bfa")
        canvas.create_text(cx, cy + 6, text=chr(65 + res_idx), font=("Segoe UI", 30, "bold"), fill="#ffffff")
        canvas.create_text(cx, cy + 26, text="mod 26", font=("Segoe UI", 8, "bold"), fill="#8b84a8")
        return canvas

    def _build_caesar_wheels_batch(self, shown, shift, wheel_scroll, idx, truncated, letters, MAX_WHEELS):
        # guard: if analysis was cleared (cipher changed) abort gracefully
        try:
            if not wheel_scroll.winfo_exists() or not self.analysis_content.winfo_exists():
                return
        except: return
        batch = 4
        end = min(idx + batch, len(shown))
        for j in range(idx, end):
            try:
                ch = shown[j]
                card = ctk.CTkFrame(wheel_scroll, fg_color="transparent", width=292)
                card.pack(side="left", padx=4, pady=4)
                if ch.isalpha():
                    p = ord(ch) - 65
                    c = (p + shift) % 26
                    self._caesar_wheel(p, c, shift, "#7c3aed", parent=card, compact=True, caption=self._L(f"الحرف {j + 1}: «{ch}»", f"Letter {j + 1}: «{ch}»"))
                else:
                    self._caesar_wheel(0, 0, 0, "#64748b", parent=card, compact=True, caption=self._L(f"الحرف {j + 1}: غير أبجدي", f"Letter {j + 1}: non-alpha"))
                # ربط محلي (غير عام) للعجلة على البطاقة وكل أبنائها — حتى تمر أي عجلة
                # يدور الشريط أفقياً دون الحاجة إلى bind_all (وهو سبب الثقل السابق).
                try:
                    for _w in (card,) + tuple(self._walk_children(card)):
                        for _seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                            _w.bind(_seq, self._wheel_on_wheel, add="+")
                        _w.bind("<ButtonPress-1>", self._wheel_on_press, add="+")
                        _w.bind("<B1-Motion>", self._wheel_on_drag, add="+")
                except Exception:
                    pass
            except Exception:
                continue
        if end < len(shown):
            self._analysis_build_after = self.after(14, lambda: self._build_caesar_wheels_batch(shown, shift, wheel_scroll, end, truncated, letters, MAX_WHEELS))
        else:
            # اكتمل البناء — لا تركة/موقتات معلّقة
            self._analysis_build_after = None
            if truncated:
                try: ctk.CTkLabel(self.analysis_content, text=self._L(f"… و {len(letters)-MAX_WHEELS} حرف إضافي لم يُعرض للحفاظ على السرعة", f"... and {len(letters)-MAX_WHEELS} more characters hidden for performance"), font=("Segoe UI", 10), text_color=self._T["TEXT_MUTED"]).pack(pady=4)
                except: pass

    def _enable_horizontal_scroll(self, scroll_frame):
        """يجعل شريط التمرير الأفقي يستجيب لعجلة الماوس والسحب داخل منطقة الدوار.

        لا يستخدم bind_all أبداً (يتسبب بتراكم معالجات على مستوى التطبيق كله وثقل
        التمرير في كل المشروع) — يعتمد فقط على ربط محلي لكل لوحة عجلة تُضاف لاحقاً.
        """
        view = {'x': 0}
        try:
            canvas = scroll_frame._parent_canvas
        except Exception:
            canvas = None

        def _on_wheel(event):
            try:
                if canvas is None:
                    return "break"
                if hasattr(event, 'delta') and event.delta:
                    canvas.xview_scroll(int(-1 * (event.delta / 120)) * 6, "units")
                elif event.num == 4:
                    canvas.xview_scroll(-6, "units")
                elif event.num == 5:
                    canvas.xview_scroll(6, "units")
            except Exception:
                pass
            return "break"

        def _on_press(event):
            view['x'] = event.x
            return "break"

        def _on_drag(event):
            try:
                if canvas is None:
                    return "break"
                canvas.scan_mark(0, 0)
                canvas.scan_dragto(event.x, event.y, gain=1)
            except Exception:
                try:
                    dx = view['x'] - event.x
                    canvas.xview_scroll(int(dx / 10), "units")
                    view['x'] = event.x
                except Exception:
                    pass
            return "break"

        # ربط رئيسي على الحاوية نفسها (يمسك العجلة فوق المساحة الفارغة من الشريط)
        try:
            for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                scroll_frame.bind(seq, _on_wheel, add="+")
            scroll_frame.bind("<ButtonPress-1>", _on_press, add="+")
            scroll_frame.bind("<B1-Motion>", _on_drag, add="+")
        except Exception:
            pass

        # ربط محلي غير عام: أي لوحة عجلة (أو حاويتها) تُربط عند ظهورها داخل الشريط.
        # لا حاجة لـ bind_all — ببساطة نمرر نفس المعالجات لكل لوحة/بطاقة جديدة.
        self._wheel_scroll_frame = scroll_frame
        self._wheel_scroll_canvas = canvas
        self._wheel_on_wheel = _on_wheel
        self._wheel_on_press = _on_press
        self._wheel_on_drag = _on_drag

    @staticmethod
    def _walk_children(widget):
        stack = list(widget.winfo_children())
        while stack:
            node = stack.pop()
            yield node
            stack.extend(node.winfo_children())

    # ---------- Vigenere strip (graphic) ----------
    def _vigenere_strip(self, key_char, plain_idx, color="#f59e0b"):
        k = ord(key_char) - 65
        W, H = 700, 180
        canvas = self._analysis_canvas(W, H)
        cell = 14.0
        gap = 1.5
        start_x = 55
        top_y = 42
        bottom_y = 115
        shifted = lambda ci: chr(((ci + k) % 26) + 65)
        step = cell + gap

        canvas.create_text(8, top_y + cell / 2, text=self._L("الأصلي:", "Plain:"), font=("Segoe UI", 10, "bold"), fill=self._T["TEXT_GRAY"], anchor="w")
        for i in range(26):
            x = start_x + i * step
            txt_top = self._T["TEXT_LIGHT"]
            if i == plain_idx:
                canvas.create_rectangle(x - 2, top_y - 3, x + cell + 2, top_y + cell + 3, fill=color, outline="#ffffff", width=2)
                txt_top = "#ffffff"
            else:
                canvas.create_rectangle(x, top_y, x + cell, top_y + cell, fill="#241a3a", outline="#2f2745")
            canvas.create_text(x + cell / 2, top_y + cell / 2, text=chr(65 + i), font=("Segoe UI", 9, "bold"), fill=txt_top)

        mid_x = start_x + plain_idx * step + cell / 2
        canvas.create_text(mid_x, top_y + cell + 14, text=f"{self._L('الإزاحة:', 'Shift:')} +{k}", font=("Segoe UI", 11, "bold"), fill=color, anchor="center")
        canvas.create_line(mid_x, top_y + cell + 4, mid_x, bottom_y - 4, arrow="last", width=3, fill=color, dash=(5, 3))

        canvas.create_text(8, bottom_y + cell / 2, text=self._L("المشفر:", "Cipher:"), font=("Segoe UI", 10, "bold"), fill=self._T["TEXT_GRAY"], anchor="w")
        for i in range(26):
            x = start_x + i * step
            if i == plain_idx:
                canvas.create_rectangle(x - 2, bottom_y - 3, x + cell + 2, bottom_y + cell + 3, fill="#34d399", outline="#ffffff", width=2)
                tcol = "#06251a"
            else:
                canvas.create_rectangle(x, bottom_y, x + cell, bottom_y + cell, fill="#173028", outline="#1f3f33")
                tcol = "#6ee7b7"
            canvas.create_text(x + cell / 2, bottom_y + cell / 2, text=shifted(i), font=("Segoe UI", 9, "bold"), fill=tcol)

        info_x = int(start_x + 26 * step + 20)
        box_right = W - 10
        canvas.create_rectangle(info_x, 30, box_right, H - 30, fill="#0f172a", outline="#334155", width=2)
        
        s1 = 44
        canvas.create_text(info_x + 12, s1, text=self._L("الحرف الأصلي:", "Plain letter:"), font=("Segoe UI", 9, "bold"), fill="#94a3b8", anchor="nw")
        canvas.create_text(info_x + 12, s1 + 16, text=chr(65 + plain_idx), font=("Segoe UI", 20, "bold"), fill="#ffffff", anchor="nw")
        canvas.create_text(info_x + 40, s1 + 19, text=f"= {plain_idx}", font=("Segoe UI", 10), fill="#64748b", anchor="nw")
        
        s2 = s1 + 46
        canvas.create_text(info_x + 12, s2, text=self._L("الإزاحة:", "Shift:"), font=("Segoe UI", 9, "bold"), fill="#94a3b8", anchor="nw")
        canvas.create_text(info_x + 12, s2 + 16, text=f"+{k}", font=("Segoe UI", 15, "bold"), fill=color, anchor="nw")
        canvas.create_text(info_x + 40, s2 + 19, text=f"= {k}", font=("Segoe UI", 10), fill="#64748b", anchor="nw")
        
        s3 = s2 + 46
        canvas.create_text(info_x + 12, s3, text=self._L("الناتج:", "Result:"), font=("Segoe UI", 9, "bold"), fill="#94a3b8", anchor="nw")
        canvas.create_text(info_x + 12, s3 + 16, text=shifted(plain_idx), font=("Segoe UI", 16, "bold"), fill="#34d399", anchor="nw")

    # ---------- Playfair rectangle (graphic) ----------
    def _playfair_rect_canvas(self, matrix, a, b, op, color="#10b981"):
        def find(letter):
            for r in range(5):
                for c in range(5):
                    if matrix[r][c] == letter:
                        return r, c
            return 0, 0
        r1, c1 = find(a)
        r2, c2 = find(b)
        cell, gap, ox, oy = 34, 3, 12, 12
        size = 5 * (cell + gap)
        canvas = self._analysis_canvas(size + 24 + 120, size + 24)
        def xy(r, c):
            return ox + c * (cell + gap), oy + r * (cell + gap)
        for r in range(5):
            for c in range(5):
                x, y = xy(r, c)
                fill, tcol = "#241a3a", self._T["TEXT_LIGHT"]
                if (r, c) in [(r1, c1), (r2, c2)]:
                    fill, tcol = color, "#ffffff"
                if op == "encrypt" and r1 != r2 and c1 != c2:
                    if (r, c) in [(r1, c2), (r2, c1)]:
                        fill, tcol = "#34d399", "#ffffff"
                canvas.create_rectangle(x, y, x + cell, y + cell, fill=fill, outline="#2f2745")
                canvas.create_text(x + cell / 2, y + cell / 2, text=matrix[r][c], font=("Segoe UI", 12, "bold"), fill=tcol)
        if r1 == r2:
            x1, y1 = xy(r1, c1)
            x2, y2 = xy(r1, c2)
            canvas.create_line(x1 + cell + 4, y1 + cell / 2, x2 - 4, y2 + cell / 2, arrow="last", width=3, fill=color)
            rule = self._L("\u2190 نفس الصف", "\u2190 Same row")
        elif c1 == c2:
            x1, y1 = xy(r1, c1)
            x2, y2 = xy(r2, c1)
            canvas.create_line(x1 + cell / 2, y1 + cell + 4, x2 + cell / 2, y2 - 4, arrow="last", width=3, fill=color)
            rule = self._L("\u2191 نفس العمود", "\u2191 Same column")
        else:
            minr, maxr = min(r1, r2), max(r1, r2)
            minc, maxc = min(c1, c2), max(c1, c2)
            x1, y1 = xy(minr, minc)
            x2, y2 = xy(maxr, maxc)
            canvas.create_rectangle(x1 - 6, y1 - 6, x2 + cell + 6, y2 + cell + 6, outline=color, width=3, dash=(6, 3))
            px1, py1 = x1 + cell / 2, y1 + cell / 2
            canvas.create_line(px1, py1, x2 + cell / 2, y1 + cell / 2, arrow="last", width=3, fill=color)
            rule = self._L("\u25a0 مستطيل: بدّل الأعمدة", "\u25a0 Rectangle: swap columns")
        canvas.create_text(size + 24 + 60 + 12, size / 2, text=rule, font=("Segoe UI", 11, "bold"), fill=color, anchor="w")

    # ---------- Diffie-Hellman flow (graphic) ----------
    def _dh_flow_canvas(self, p, g, a, b, A, B, s_alice, s_bob):
        canvas = self._analysis_canvas(380, 200)
        canvas.create_oval(38, 34, 138, 134, fill="#701a75", outline="#c026d3", width=3)
        canvas.create_text(88, 84, text="KAIDO", font=("Segoe UI", 12, "bold"), fill="#ffffff")
        canvas.create_oval(242, 34, 342, 134, fill="#075985", outline="#38bdf8", width=3)
        canvas.create_text(292, 84, text="ALEX", font=("Segoe UI", 12, "bold"), fill="#ffffff")
        canvas.create_line(120, 52, 258, 52, arrow="last", width=3, fill="#f472b6")
        canvas.create_text(189, 32, text=f"A = g\u1d43 mod p = {A}", font=("Cascadia Code", 10, "bold"), fill="#f472b6")
        canvas.create_line(258, 116, 120, 116, arrow="last", width=3, fill="#38bdf8")
        canvas.create_text(189, 136, text=f"B = g\u1d47 mod p = {B}", font=("Cascadia Code", 10, "bold"), fill="#38bdf8")
        canvas.create_rectangle(60, 158, 320, 190, fill="#134e4a", outline="#14b8a6", width=2)
        canvas.create_text(190, 174, text=f"\U0001f511 s = B\u1d43 mod p = A\u1d47 mod p = {s_alice}",
                           font=("Cascadia Code", 11, "bold"), fill="#99f6e4")

    # ---------- RSA padlock (graphic) ----------
    def _rsa_lock_canvas(self, m_text, m, c, e, n, color="#7c3aed"):
        canvas = self._analysis_canvas(330, 100)
        canvas.create_text(24, 50, text=m_text, font=("Segoe UI", 26, "bold"), fill="#ffffff", anchor="w")
        canvas.create_text(24, 80, text=f"ascii {m}", font=("Cascadia Code", 8), fill=self._T["TEXT_GRAY"], anchor="w")
        canvas.create_line(60, 50, 96, 50, arrow="last", width=3, fill="#a78bfa")
        lx, ly = 118, 52
        canvas.create_arc(lx - 13, ly - 24, lx + 13, ly - 2, start=0, extent=180, style="arc", outline=color, width=5)
        canvas.create_rectangle(lx - 20, ly - 8, lx + 20, ly + 32, fill=color, outline="")
        canvas.create_rectangle(lx - 20, ly - 8, lx + 20, ly - 2, fill="#5b21b6", outline="")
        canvas.create_oval(lx - 4, ly + 6, lx + 4, ly + 14, fill="#ffffff")
        canvas.create_rectangle(lx - 2, ly + 12, lx + 2, ly + 24, fill="#ffffff")
        canvas.create_text(lx, ly + 42, text=f"({e}, {n})", font=("Cascadia Code", 9, "bold"), fill="#c4b5fd")
        canvas.create_line(lx + 26, 50, 236, 50, arrow="last", width=3, fill="#34d399")
        canvas.create_text(286, 42, text=str(c), font=("Cascadia Code", 19, "bold"), fill="#34d399", anchor="w")
        canvas.create_text(286, 74, text="c = m\u1d40 mod n", font=("Cascadia Code", 9, "bold"), fill="#6ee7b7", anchor="w")

    # ---------- Affine mapping ring (graphic, method 2) ----------
    def _affine_ring_canvas(self, m, k, plain_idx, res_idx, color="#06b6d4", parent=None):
        T = self._T
        parent = parent if parent is not None else self.analysis_content
        W, H = 500, 400
        canvas = ctk.CTkCanvas(parent, width=W, height=H, bg=T["BG_INPUT"], highlightthickness=0, bd=0)
        canvas.pack(side="left", padx=10, pady=10)
        cx, cy = 155, 200
        R, inn, step = 125, 84, 360 / 26
        def pos(i, r):
            a = math.radians(90 - i * step)
            return cx + r * math.cos(a), cy - r * math.sin(a)
        canvas.create_oval(cx - R, cy - R, cx + R, cy + R, fill="#0b2d3a", outline="#22d3ee", width=3)
        canvas.create_oval(cx - inn, cy - inn, cx + inn, cy + inn, fill="#06212b", outline="#0e7490", width=2)
        for i in range(26):
            ox, oy = pos(i, inn)
            ix, iy = pos(i, R)
            canvas.create_line(ox, oy, ix, iy, fill="#1e4c5e", width=1)
        for i in range(26):
            x, y = pos(i, R + 18)
            if i == plain_idx:
                canvas.create_oval(x - 14, y - 14, x + 14, y + 14, fill=color, outline="#ffffff", width=2)
                canvas.create_text(x, y, text=chr(65 + i), font=("Segoe UI", 12, "bold"), fill="#0b2d3a")
            else:
                canvas.create_oval(x - 12, y - 12, x + 12, y + 12, fill="#d1d5db", outline="#ffffff", width=1)
                canvas.create_text(x, y, text=chr(65 + i), font=("Segoe UI", 10, "bold"), fill="#1e293b")
        for i in range(26):
            res = (m * i + k) % 26
            x, y = pos(res, inn)
            if i == plain_idx:
                canvas.create_oval(x - 9, y - 9, x + 9, y + 9, fill="#22d3ee", outline="#ffffff", width=2)
                canvas.create_text(x, y, text=chr(65 + res), font=("Segoe UI", 10, "bold"), fill="#06212b")
            else:
                canvas.create_text(x, y, text=chr(65 + res), font=("Segoe UI", 10, "bold"), fill="#67e8f9")
        xp, yp = pos(plain_idx, R + 18)
        xs, ys = pos(res_idx, inn)
        canvas.create_line(xp, yp, xs, ys, arrow="last", width=3, fill=color, dash=(5, 3))
        px = 310
        canvas.create_rectangle(px, 30, W - 14, 370, fill="#08272e", outline="#155e75", width=2)
        canvas.create_text(px + 10, 58, text=self._L("الحرف الأصلي", "Plain letter"), font=("Segoe UI", 11, "bold"), fill=T["TEXT_GRAY"], anchor="nw")
        canvas.create_text(px + 10, 86, text=chr(65 + plain_idx), font=("Segoe UI", 32, "bold"), fill="#ffffff", anchor="nw")
        canvas.create_text(px + 10, 132, text=self._L("x =", "x =") + f" {plain_idx}", font=("Cascadia Code", 12, "bold"), fill="#22d3ee", anchor="nw")
        canvas.create_text(px + 10, 160, text=self._L("القيمة العددية", "Value"), font=("Segoe UI", 10, "bold"), fill=T["TEXT_GRAY"], anchor="nw")
        canvas.create_text(px + 10, 184, text=f"({m}\u00b7{plain_idx} + {k})", font=("Cascadia Code", 11, "bold"), fill="#a5f3fc", anchor="nw")
        canvas.create_text(px + 10, 208, text=f"mod 26 = {res_idx}", font=("Cascadia Code", 11, "bold"), fill="#a5f3fc", anchor="nw")
        canvas.create_text(px + 10, 238, text=self._L("الناتج", "Result"), font=("Segoe UI", 10, "bold"), fill=T["TEXT_GRAY"], anchor="nw")
        canvas.create_text(px + 10, 268, text=chr(65 + res_idx), font=("Segoe UI", 30, "bold"), fill="#67e8f9", anchor="nw")
        canvas.create_text(px + 10, 306, text=f"= {res_idx}", font=("Cascadia Code", 12, "bold"), fill="#34d399", anchor="nw")

    # ---------- Hill 2x2 matrix x vector (graphic, method 2) ----------
    def _hill_vector_canvas(self, matrix, p1, p2, c1, c2, op, color="#ec4899"):
        T = self._T
        canvas = self._analysis_canvas(340, 128)
        ox = 12
        co = color
        # matrix
        for r in range(2):
            for c in range(2):
                x, y = ox + c * 30, 26 + r * 30
                val = matrix[r][c] if False else matrix[r][c]
                canvas.create_rectangle(x, y, x + 26, y + 26, fill="#3b1052", outline=co, width=2)
                canvas.create_text(x + 13, y + 13, text=str(val), font=("Cascadia Code", 12, "bold"), fill="#fbcfe8")
        canvas.create_text(ox + 13, 14, text="K", font=("Segoe UI", 9, "bold"), fill=T["TEXT_GRAY"])
        xm = ox + 60 + 30 - 10
        # multiply x
        canvas.create_text(xm, 30, text="\u00d7", font=("Segoe UI", 18, "bold"), fill="#f472b6")
        # plain vector P = [p1, p2]
        for i, v in enumerate([p1, p2]):
            x, y = xm + 20, 26 + i * 30
            canvas.create_rectangle(x, y, x + 26, y + 26, fill="#4a1340", outline="#fb7185", width=2)
            canvas.create_text(x + 13, y + 13, text=str(v), font=("Cascadia Code", 12, "bold"), fill="#fecdd3")
        canvas.create_text(xm + 33, 14, text="P", font=("Segoe UI", 9, "bold"), fill=T["TEXT_GRAY"])
        # equals
        canvas.create_text(xm + 62, 30, text="=", font=("Segoe UI", 20, "bold"), fill="#f472b6")
        # result vector C = [c1, c2]
        for i, v in enumerate([c1, c2]):
            x, y = xm + 80, 26 + i * 30
            canvas.create_rectangle(x, y, x + 26, y + 26, fill="#fb7185", outline="#ffffff", width=2)
            canvas.create_text(x + 13, y + 13, text=str(v), font=("Cascadia Code", 12, "bold"), fill="#ffffff")
        canvas.create_text(xm + 93, 14, text="C", font=("Segoe UI", 9, "bold"), fill=T["TEXT_GRAY"])
        if op == "encrypt":
            title_label = self._L("K \u00d7 P = C  (mod 26)", "K \u00d7 P = C  (mod 26)")
            row_note = f"({matrix[0][0]}\u00b7{p1} + {matrix[0][1]}\u00b7{p2}) mod 26 = {c1}"
        else:
            title_label = self._L("K\u207b\u00b9 \u00d7 C = P  (mod 26)", "K\u207b\u00b9 \u00d7 C = P  (mod 26)")
            row_note = f"({matrix[0][0]}\u00b7{p1} + {matrix[0][1]}\u00b7{p2}) mod 26 = {c1}"
        canvas.create_text(ox + 13, 100, text=title_label, font=("Cascadia Code", 11, "bold"), fill=color, anchor="w")
        canvas.create_text(ox + 13, 116, text=row_note, font=("Cascadia Code", 9), fill=T["TEXT_GRAY"], anchor="w")

    # ---------- RSA power chain (graphic, method 2) ----------
    def _rsa_power_canvas(self, m_text, m, c, e, n, color="#7c3aed"):
        T = self._T
        canvas = self._analysis_canvas(340, 96)
        steps = [(m_text, str(m), color), ("\u2191", "m\u1d40", "#a78bfa"), (str(c), "c = m\u1d40 mod n", "#34d399")]
        x = 12
        for idx, (top, bot, col) in enumerate(steps):
            canvas.create_text(x, 26, text=top, font=("Cascadia Code", 16, "bold"), fill="#ffffff", anchor="w")
            canvas.create_text(x, 46, text=bot, font=("Cascadia Code", 9, "bold"), fill=col, anchor="w")
            w = max(30, len(top) * 9 + 6)
            if idx < len(steps) - 1:
                arrow_x = x + len(top) * 9 + 6
                canvas.create_line(arrow_x, 34, arrow_x + 22, 34, arrow="last", width=3, fill="#a78bfa")
                x = arrow_x + 30
        canvas.create_text(12, 74, text=f"{m}^{e} mod {n} = {c}", font=("Cascadia Code", 10, "bold"), fill="#fcd34d", anchor="w")

    # ---------- Caesar ----------
    def _analyze_caesar(self, text, operation):
        T = self._T
        key = int(self.key1.get())
        shift = key if operation == "encrypt" else -key
        self._analysis_hero(
            self._L("إزاحة قيصر  Caesar Shift", "Caesar Shift"),
            self._L(
                f"كُل حرف يُزاح {abs(shift)} خانه {'يميناً على الأبجدية' if shift > 0 else 'يساراً على الأبجدية'} — E(x) = (x {shift:+}) mod 26",
                f"Each letter is shifted {abs(shift)} place{'s' if abs(shift) != 1 else ''} {'right' if shift > 0 else 'left'} in the alphabet — E(x) = (x {shift:+}) mod 26"
            ),
            "#7c3aed",
            "\U0001f3a1"
        )
        self._analysis_chips([
            (self._L("المفتاح K", "Key K"), key, "#a78bfa", "\U0001f511"),
            (self._L("الإزاحة", "Shift"), f"{shift:+}", "#c4b5fd", "\U0001f3af"),
        ])
        self._analysis_note(
            self._L(
                "الأبجدية دائرة! الحروف الـ26 مرتبة على شكل حلقة — بعد حرف Z نعود مباشرة إلى A. لذلك عندما يلتقي الإزاحة بنهاية الدائرة فإنها تلتف بشكل تلقائي.",
                "The alphabet is a circle! The 26 letters are arranged on a ring — after Z we return directly to A. So when the shift reaches the end of the ring it wraps around automatically."
            ),
            "#7c3aed",
            "\U0001f501"
        )
        letters = list(text.upper())
        if letters:
            MAX_WHEELS = 8
            shown = letters[:MAX_WHEELS]
            truncated = len(letters) > MAX_WHEELS
            strip_title = ctk.CTkLabel(
                self.analysis_content,
                text=self._L(f"عجلة قيصر لكل حرف — مرّر أفقياً لرؤية الكل ({len(shown)}/{len(letters)}):", f"Caesar wheel for each letter — scroll horizontally ({len(shown)}/{len(letters)}):") + (self._L(" — تم اقتطاع الباقي للأداء", " — truncated for performance") if truncated else ""),
                font=("Segoe UI", 11, "bold"),
                text_color="#a78bfa",
                anchor="w"
            )
            strip_title.pack(fill="x", padx=10, pady=(10, 2))
            wheel_scroll = ctk.CTkScrollableFrame(
                self.analysis_content,
                orientation="horizontal",
                width=0,
                height=280,
                fg_color=T["BG_CARD"],
                border_width=1,
                border_color=T["BORDER_COLOR"],
                corner_radius=12
            )
            wheel_scroll.pack(fill="x", padx=6, pady=(2, 6))
            self._enable_horizontal_scroll(wheel_scroll)
            # build wheels in small batches to keep UI responsive
            self._build_caesar_wheels_batch(shown, shift, wheel_scroll, 0, truncated, letters, MAX_WHEELS)
            # ---- الطريقة الثانية: تحويل نصي أنيق لكل حرف ----
            rows_title = ctk.CTkLabel(
                self.analysis_content,
                text=self._L(
                    f"أو بطريقة أخرى — تحويل كل حرف نصياً ({len(shown)}/{len(letters)}):",
                    f"Or another way — each letter as plain text ({len(shown)}/{len(letters)}):"
                ),
                font=("Segoe UI", 11, "bold"),
                text_color="#c4b5fd",
                anchor="w"
            )
            rows_title.pack(fill="x", padx=10, pady=(12, 4))
            rows_card = ctk.CTkFrame(self.analysis_content, fg_color=T["BG_INPUT"], corner_radius=12, border_width=1, border_color=T["BORDER_COLOR"])
            rows_card.pack(fill="x", padx=6, pady=(0, 4))
            for i, ch in enumerate(shown):
                enc = chr(((ord(ch) - 65 + shift) % 26) + 65) if 'A' <= ch <= 'Z' else ch
                row = ctk.CTkFrame(rows_card, fg_color="#1e1a33" if i % 2 == 0 else "transparent")
                row.pack(fill="x", padx=10, pady=2)
                self._analysis_tile(row, ch, "#7c3aed")
                self._analysis_arrow(row, "#a78bfa")
                if 'A' <= ch <= 'Z':
                    self._analysis_tile(row, enc, "#f59e0b")
                    ctk.CTkLabel(
                        row,
                        text=self._L(
                            f"{ch} = {ord(ch)-65} ، {ord(ch)-65}{shift:+} mod 26 = {(ord(ch)-65+shift)%26}",
                            f"{ch}={ord(ch)-65}, ({ord(ch)-65}{shift:+}) mod 26 = {(ord(ch)-65+shift)%26}"
                        ),
                        font=("Cascadia Code", 11, "bold"),
                        text_color="#8b84a8",
                        padx=10
                    ).pack(side="left")
                else:
                    self._analysis_tile(row, ch, "#64748b")
                    ctk.CTkLabel(
                        row,
                        text=self._L("غير أبجدي — يبقى كما هو", "Non-alphabetic — stays unchanged"),
                        font=("Segoe UI", 11),
                        text_color=T["TEXT_MUTED"],
                        padx=10
                    ).pack(side="left")
            if truncated:
                ctk.CTkLabel(
                    self.analysis_content,
                    text=self._L(f"… و {len(letters)-MAX_WHEELS} حرف إضافي يُحسب بنفس الطريقة (لم يُعرض للأداء)", f"... and {len(letters)-MAX_WHEELS} more letters shifted the same way (hidden for performance)"),
                    font=("Segoe UI", 10),
                    text_color=T["TEXT_MUTED"]
                ).pack(pady=(2, 8))
            ctk.CTkLabel(
                self.analysis_content,
                text=self._L(
                    "يُظهر هذا تحويل كل حرف بطريقتين: العجلة الدائرية الكبيرة أعلى وصفوف النص هنا — مرّر أفقياً فوق العجلات أو اسحب للتنقل بين الحروف.",
                    "This shows each letter's conversion in two ways: the large circular wheels above and the text rows here — scroll horizontally over the wheels or drag to move between letters."
                ),
                font=("Segoe UI", 10),
                text_color=T["TEXT_MUTED"],
                wraplength=1600,
                justify="center"
            ).pack(fill="x", padx=12, pady=(0, 6))

    # ---------- Affine ----------
    def _analyze_affine(self, text, operation):
        T = self._T
        m = int(self.key1.get())
        k = int(self.key2.get())
        inv_m = CryptoCore.mod_inverse(m, 26)
        self._analysis_hero(
            self._L("التحويل الخطي المتآلف  Affine", "Affine Cipher"),
            self._L(
                f"معادلة {('التشفير' if operation=='encrypt' else 'فك التشفير')} على الحرف x بتطبيق (m\u00b7x + k) ثم أخذ mod 26",
                f"{'Encryption' if operation=='encrypt' else 'Decryption'} formula on letter x: apply (m\u00b7x + k) then take mod 26"
            ),
            "#06b6d4",
            "\U0001f9ee"
        )
        self._analysis_chips([
            ("a", m, "#22d3ee", "\U0001f522"),
            ("b", k, "#22d3ee", "\U0001f522"),
            ("a\u207b\u00b9", inv_m, "#67e8f9", "\U0001f504"),
            ("gcd(a,26)", math.gcd(m, 26), "#a5f3fc", "\u2714\ufe0f"),
        ])
        if math.gcd(m, 26) == 1:
            self._analysis_note(
                self._L(
                    f"شرط الحل: gcd(a, 26) = 1 يعني أن «a» أوليّ مع 26. عكسياً، لفك التشفير نضرب بالمعكوس a\u207b\u00b9 = {inv_m} لأن {m}\u00d7{inv_m} ≡ 1 (mod 26) — بهذه الطريقة يلغي التشفير نفسه.",
                    f"Solvability condition: gcd(a, 26) = 1 means a is coprime with 26. To decrypt we multiply by the modular inverse a\u207b\u00b9 = {inv_m} because {m}\u00d7{inv_m} ≡ 1 (mod 26) — this cancels the encryption perfectly."
                ),
                "#06b6d4",
                "\u2714\ufe0f"
            )
        else:
            self._analysis_note(
                self._L(
                    "انتبه: gcd(a, 26) ≠ 1 يعني أن التشفير غير قابل للفك (غير قابل للانعكاس) — يجب اختيار a أوليّ مع 26 مثل 3 أو 5 أو 7 أو 9...",
                    "Caution: gcd(a, 26) ≠ 1 means the cipher is not reversible — you must choose a coprime with 26, e.g. 3, 5, 7, 9..."
                ),
                "#ef4444",
                "\u26a0\ufe0f"
            )
        if operation == "encrypt":
            self._analysis_note(
                self._L(
                    f"خطوات التشفير: 1) حوّل الحرف إلى رقم x (A=0, B=1, ..., Z=25). 2) احسب (m\u00d7x + k) mod 26. 3) حوّل الرقم الناتج إلى حرف. النتيجة: {chr((m * (ord(text.upper()[0]) - 65) + k) % 26 + 65)}",
                    f"Encryption steps: 1) Convert letter to number x (A=0, B=1, ..., Z=25). 2) Compute (m\u00d7x + k) mod 26. 3) Convert result back to letter. Result: {chr((m * (ord(text.upper()[0]) - 65) + k) % 26 + 65)}"
                ),
                "#22d3ee",
                "\U0001f522"
            )
        else:
            self._analysis_note(
                self._L(
                    f"خطوات فك التشفير: 1) حوّل الحرف المشفر إلى رقم x. 2) احسب a\u207b\u00b9\u00d7(x - k) mod 26. 3) حوّل الرقم الناتج إلى الحرف الأصلي. النتيجة: {chr((inv_m * ((ord(text.upper()[0]) - 65) - k)) % 26 + 65)}",
                    f"Decryption steps: 1) Convert encrypted letter to number x. 2) Compute a\u207b\u00b9\u00d7(x - k) mod 26. 3) Convert result back to original letter. Result: {chr((inv_m * ((ord(text.upper()[0]) - 65) - k)) % 26 + 65)}"
                ),
                "#22d3ee",
                "\U0001f504"
            )
        upper = text.upper()
        samples = [c for c in upper if c.isalpha()]
        shown = samples[:6]
        m2_title = ctk.CTkLabel(
            self.analysis_content,
            text=self._L(
                f"أو بطريقة أخرى — خريطة دوران كل حرف على الحلقة ({len(shown)}/{len(samples)}):",
                f"Or another way — the ring mapping for each letter ({len(shown)}/{len(samples)}):"
            ),
            font=("Segoe UI", 11, "bold"),
            text_color="#22d3ee",
            anchor="w"
        )
        m2_title.pack(fill="x", padx=10, pady=(12, 2))
        for i in range(0, len(shown), 3):
            ring_row = ctk.CTkFrame(
                self.analysis_content,
                fg_color=T["BG_CARD"],
                corner_radius=12,
                border_width=1,
                border_color=T["BORDER_COLOR"]
            )
            ring_row.pack(fill="x", padx=6, pady=4)
            for j in range(3):
                if i + j < len(shown):
                    ch = shown[i + j]
                    x = ord(ch) - 65
                    res = (m * x + k) % 26 if operation == "encrypt" else (inv_m * (x - k)) % 26
                    self._affine_ring_canvas(m, k, x, res, "#06b6d4", parent=ring_row)
        if len(samples) > 6:
            ctk.CTkLabel(self.analysis_content, text=self._L("... الحروف الباقية تُرسم بنفس الطريقة (اقتطاع للأداء)", "... remaining letters drawn the same way (truncated for performance)"), font=("Segoe UI", 10), text_color=T["TEXT_MUTED"]).pack(pady=(0, 4))
        rows_title = ctk.CTkLabel(
            self.analysis_content,
            text=self._L(
                f"تفاصيل كل حرف على حدة ({len(upper)}/{len(upper)}):",
                f"Each letter individually ({len(upper)}/{len(upper)}):"
            ),
            font=("Segoe UI", 11, "bold"),
            text_color="#22d3ee",
            anchor="w"
        )
        rows_title.pack(fill="x", padx=10, pady=(8, 4))
        rows_card = ctk.CTkFrame(self.analysis_content, fg_color=T["BG_INPUT"], corner_radius=12, border_width=1, border_color=T["BORDER_COLOR"])
        rows_card.pack(fill="x", padx=6, pady=(0, 4))
        for i, ch in enumerate(upper):
            row = ctk.CTkFrame(rows_card, fg_color="#0c2a35" if i % 2 == 0 else "transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=ch, font=("Segoe UI", 18, "bold"), text_color=T["TEXT_GRAY"], width=44, fg_color=T["BG_INPUT"], corner_radius=8).pack(side="left", padx=2)
            self._analysis_arrow(row, "#06b6d4")
            if ch.isalpha():
                x = ord(ch) - 65
                if operation == "encrypt":
                    c = (m * x + k) % 26
                    formula = f"({m}\u00d7{x} + {k}) mod 26 = {c}"
                else:
                    c = (inv_m * (x - k)) % 26
                    formula = f"{inv_m}\u00d7({x} - {k}) mod 26 = {c}"
                self._analysis_tile(row, chr(c + 65), "#06b6d4")
                ctk.CTkLabel(row, text=formula, font=("Cascadia Code", 11, "bold"), text_color="#67e8f9", padx=10).pack(side="left")
            else:
                self._analysis_tile(row, ch, "#64748b")
                ctk.CTkLabel(row, text=self._L("رمز غير أبجدي", "Non-alphabetic"), font=("Segoe UI", 11), text_color=T["TEXT_MUTED"], padx=10).pack(side="left")

    # ---------- Vigenere ----------
    def _analyze_vigenere(self, text, operation):
        T = self._T
        key = self.key1.get().upper()
        if not key:
            key = "A"
        self._analysis_hero(
            self._L("شيفرة فيجينير  Vigen\u00e8re", "Vigen\u00e8re Cipher"),
            self._L(
                f"حروف المفتاح «{key}» تتكرر فوق النص كُل حرف يُزاح بإزاحة حرف المفتاح المقابل",
                f"The keyword «{key}» repeats over the text; each letter is shifted by the shift of its matching keyword letter"
            ),
            "#f59e0b",
            "\U0001f4d6"
        )
        letters = [(i, ch) for i, ch in enumerate(text.upper()) if ch.isalpha()]
        if letters:
            key_row = ctk.CTkFrame(self.analysis_content, fg_color="transparent")
            key_row.pack(fill="x", padx=8, pady=(6, 0))
            ctk.CTkLabel(key_row, text="Key:", font=("Segoe UI", 11, "bold"), text_color=T["TEXT_GRAY"]).pack(side="left", padx=2)
            for i, ch in enumerate(text.upper()):
                if ch.isalpha():
                    kv = key[i % len(key)]
                    self._analysis_tile(key_row, kv, "#f59e0b", size=16, width=38, height=38)
            fi, fch = letters[0]
            fk = key[fi % len(key)]
            self._vigenere_strip(fk, ord(fch) - 65, "#f59e0b")
            self._analysis_note(
                self._L(
                    f"المفتاح يتكرر دورياً: كُل حرف من النص يُزاح بإزاحة الحرف المقابل له من المفتاح (مثلاً K = 10)، ثم يُدوَّر الناتج حول دائرة الأبجدية بنفس فكرة قيصر.",
                    f"The keyword repeats cyclically: each plaintext letter is shifted by its matching keyword letter (e.g. K = 10), then the result wraps around the alphabet circle just like Caesar."
                ),
                "#f59e0b",
                "\U0001f504"
            )
            m2_title = ctk.CTkLabel(
                self.analysis_content,
                text=self._L(
                    f"شريط الإزاحة لكل حرف ({len(letters)}/{len(letters)}):",
                    f"Shift strip for each letter ({len(letters)}/{len(letters)}):"
                ),
                font=("Segoe UI", 11, "bold"),
                text_color="#fcd34d",
                anchor="w"
            )
            m2_title.pack(fill="x", padx=10, pady=(12, 2))
            for si, (sidx, sch) in enumerate(letters):
                sk = key[sidx % len(key)]
                self._vigenere_strip(sk, ord(sch) - 65, "#f59e0b")
            self._analysis_note(
                self._L(
                    f"خطوات {'التشفير' if operation == 'encrypt' else 'فك التشفير'}: 1) {'كرر المفتاح حتى يساوي طول النص. 2' if operation == 'encrypt' else ''}حوّل كل حرف إلى رقم (A=0, B=1, ..., Z=25). {'3) اجمع رقم الحرف مع رقم حرف المفتاح المقابل. 4' if operation == 'encrypt' else '2) اطرح رقم حرف المفتاح من رقم الحرف. 3'} خذ الناتج mod 26. {'5' if operation == 'encrypt' else '4'}) حوّل الرقم إلى حرف.",
                    f"{'Encryption' if operation == 'encrypt' else 'Decryption'} steps: 1{') Repeat the key to match text length. 2' if operation == 'encrypt' else ''}) Convert each letter to number (A=0, B=1, ..., Z=25). {'3) Add the letter number with the matching key letter number. 4' if operation == 'encrypt' else '2) Subtract the key letter number from the letter number. 3'}) Take mod 26. {'5' if operation == 'encrypt' else '4'}) Convert result back to letter."
                ),
                "#f59e0b",
                "\U0001f522"
            )
        for i, ch in enumerate(text.upper()):
            row = ctk.CTkFrame(self.analysis_content, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=4)
            ctk.CTkLabel(row, text=ch, font=("Segoe UI", 18, "bold"), text_color=T["TEXT_GRAY"], width=44, fg_color=T["BG_INPUT"], corner_radius=8).pack(side="left", padx=2)
            self._analysis_arrow(row, "#f59e0b")
            if ch.isalpha():
                p = ord(ch) - 65
                kv = key[i % len(key)]
                k = ord(kv) - 65
                if operation == "encrypt":
                    c = (p + k) % 26
                    formula = f"({p} + {k}) mod 26 = {c}"
                else:
                    c = (p - k) % 26
                    formula = f"({p} - {k}) mod 26 = {c}"
                self._analysis_tile(row, chr(c + 65), "#f59e0b")
                ctk.CTkLabel(row, text=f"[{kv} {k}]  {formula}", font=("Cascadia Code", 11, "bold"), text_color="#fcd34d", padx=10).pack(side="left")
            else:
                self._analysis_tile(row, ch, "#64748b")
                ctk.CTkLabel(row, text=self._L("رمز غير أبجدي", "Non-alphabetic"), font=("Segoe UI", 11), text_color=T["TEXT_MUTED"], padx=10).pack(side="left")

    # ---------- Playfair ----------
    def _analyze_playfair(self, text, operation):
        key = self.key1.get()
        matrix = CryptoCore.playfair_matrix(key)
        self._analysis_hero(
            self._L("شبكة بلايفير 5\u00d75  Playfair", "Playfair 5\u00d75 Grid"),
            self._L(
                f"المفتاح «{key}» — تُحذف حروف المفتاح المكررة ثم تُكمل بقية الأبجدية، و J\u2192I",
                f"Key «{key}» — duplicate key letters are removed, then the rest of the alphabet fills the grid, with J\u2192I"
            ),
            "#10b981",
            "\U0001f9f9"
        )
        seen = set()
        highlight = set()
        for ch in key.upper():
            if ch == "J":
                ch = "I"
            if ch not in seen:
                seen.add(ch)
                for r in range(5):
                    for c in range(5):
                        if matrix[r][c] == ch:
                            highlight.add((r, c))
        self._matrix_grid(matrix, highlight, base_color="#10b981")
        processed = self._playfair_prepare(text)
        note = ctk.CTkLabel(self.analysis_content, text=self._L(f"النص المُجهّز: {processed}", f"Prepared text: {processed}"), font=("Cascadia Code", 12, "bold"), text_color="#059669", anchor="w")
        note.pack(fill="x", padx=10, pady=(6, 2))
        for i in range(0, len(processed), 2):
            if i + 1 < len(processed):
                self._playfair_digraph(processed[i], processed[i + 1], matrix, operation)

    def _playfair_digraph(self, a, b, matrix, op):
        T = self._T
        def find(letter):
            for r in range(5):
                for c in range(5):
                    if matrix[r][c] == letter:
                        return r, c
            return 0, 0
        def move(r, c, dr, dc):
            return (r + dr) % 5, (c + dc) % 5
        r1, c1 = find(a)
        r2, c2 = find(b)
        self._playfair_rect_canvas(matrix, a, b, op, "#10b981")
        if r1 == r2:
            rule = (self._L("نفس الصف \u2192 إزاحة يمين", "Same row \u2192 shift right") if op == "encrypt" else self._L("نفس الصف \u2192 إزاحة يسار", "Same row \u2192 shift left"))
            (nr1, nc1), (nr2, nc2) = (move(r1, c1, 0, 1), move(r2, c2, 0, 1)) if op == "encrypt" else (move(r1, c1, 0, -1), move(r2, c2, 0, -1))
        elif c1 == c2:
            rule = (self._L("نفس العمود \u2192 إزاحة أسفل", "Same column \u2192 shift down") if op == "encrypt" else self._L("نفس العمود \u2192 إزاحة أعلى", "Same column \u2192 shift up"))
            (nr1, nc1), (nr2, nc2) = (move(r1, c1, 1, 0), move(r2, c2, 1, 0)) if op == "encrypt" else (move(r1, c1, -1, 0), move(r2, c2, -1, 0))
        else:
            rule = self._L("مستطيل \u2192 تبادل الأعمدة", "Rectangle \u2192 swap columns")
            (nr1, nc1), (nr2, nc2) = (r1, c2), (r2, c1)
        card = ctk.CTkFrame(self.analysis_content, fg_color=T["BG_CARD"], corner_radius=10, border_width=1, border_color=T["BORDER_COLOR"])
        card.pack(fill="x", pady=4, padx=6)
        card.bind("<Enter>", lambda e: card.configure(border_color="#10b981", border_width=2))
        card.bind("<Leave>", lambda e: card.configure(border_color=T["BORDER_COLOR"], border_width=1))
        row_f = ctk.CTkFrame(card, fg_color="transparent")
        row_f.pack(fill="x", padx=10, pady=8)
        self._analysis_tile(row_f, a, "#10b981", sub=f"{r1},{c1}", size=18, width=44, height=44)
        self._analysis_tile(row_f, b, "#10b981", sub=f"{r2},{c2}", size=18, width=44, height=44)
        self._analysis_arrow(row_f, "#059669")
        self._analysis_tile(row_f, matrix[nr1][nc1], "#34d399", sub=f"{nr1},{nc1}", size=18, width=44, height=44)
        self._analysis_tile(row_f, matrix[nr2][nc2], "#34d399", sub=f"{nr2},{nc2}", size=18, width=44, height=44)
        ctk.CTkLabel(row_f, text=rule, font=("Segoe UI", 11, "bold"), text_color="#059669", padx=10).pack(side="left")

    # ---------- Hill ----------
    def _analyze_hill(self, text, operation):
        matrix = CryptoCore.hill_matrix(self.key1.get())
        self._analysis_hero(
            self._L("شيفرة هيل 2\u00d72  Hill", "Hill Cipher 2\u00d72"),
            self._L(
                "تُقسم الرسالة إلى أزواج، كُل زوج يُضرب بمصفوفة المفتاح، ثم يؤخذ الناتج (mod 26)",
                "The message is split into pairs; each pair is multiplied by the key matrix, then the result is taken (mod 26)"
            ),
            "#ec4899",
            "\U0001f9ee"
        )
        self._analysis_chips([
            (self._L("مصفوفة المفتاح", "Key matrix"), f"[{matrix[0][0]} {matrix[0][1]}; {matrix[1][0]} {matrix[1][1]}]", "#f472b6", "\U0001f5c2"),
            (self._L("الحساب", "Math"), "(mod 26)", "#fda4af", "\u2211"),
        ])
        self._matrix_grid(matrix, base_color="#ec4899")
        det = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 26
        try:
            inv_det = CryptoCore.mod_inverse(det, 26)
            self._analysis_note(
                self._L(
                    f"كُل زوج يُعامَل كمتجه [x, y] ويُضرب بالمصفوفة. للتشفير خذ (mod 26)؛ للفك نوجد det = {det} ثم نفرّق على {inv_det} لأنه det\u00d7{inv_det} ≡ 1 (mod 26). لماذا يعمل؟ لأن {matrix[0][0]}\u00d7{inv_det}... إلخ تُنتج المصفوفة العكسية التي تُلغي الأولى بالضرب.",
                    f"Each pair is treated as a vector [x, y] and multiplied by the matrix. To encrypt just take (mod 26); to decrypt we compute det = {det} then scale the inverse matrix by {inv_det} because det\u00d7{inv_det} ≡ 1 (mod 26). Why does it work? The scaled cofactors produce the inverse matrix that cancels the original by multiplication."
                ),
                "#ec4899",
                "\U0001f9ee"
            )
        except Exception:
            self._analysis_note(
                self._L(
                    f"تنبيه: مصفوفة المفتاح غير قابلة للعكس لأن det = {det} ليس أوليّاً مع 26 — لن يعمل فك التشفير.",
                    f"Warning: the key matrix is not invertible because det = {det} is not coprime with 26 — decryption will not work."
                ),
                "#ef4444",
                "\u26a0\ufe0f"
            )
        processed = "".join(cc for cc in text.upper() if cc.isalpha())
        if not processed:
            return
        if len(processed) % 2:
            processed += "X"
        m2_title = ctk.CTkLabel(
            self.analysis_content,
            text=self._L(
                f"أو بطريقة أخرى — رسم ضرب المصفوفة × المتجه لكل زوج ({len(processed)//2} زوجاً):",
                f"Or another way — the matrix × vector multiplication for each pair ({len(processed)//2} pair{'s' if len(processed)//2 != 1 else ''}):"
            ),
            font=("Segoe UI", 11, "bold"),
            text_color="#f9a8d4",
            anchor="w"
        )
        m2_title.pack(fill="x", padx=10, pady=(12, 2))
        for vp in range(0, min(len(processed), 8), 2):
            p1x = ord(processed[vp]) - 65
            p2x = ord(processed[vp + 1]) - 65
            shown_matrix = matrix
            if operation == "encrypt":
                c1x = (matrix[0][0] * p1x + matrix[0][1] * p2x) % 26
                c2x = (matrix[1][0] * p1x + matrix[1][1] * p2x) % 26
            else:
                det2 = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 26
                inv2 = CryptoCore.mod_inverse(det2, 26)
                im = [[(matrix[1][1] * inv2) % 26, (-matrix[0][1] * inv2) % 26],
                      [(-matrix[1][0] * inv2) % 26, (matrix[0][0] * inv2) % 26]]
                c1x = (im[0][0] * p1x + im[0][1] * p2x) % 26
                c2x = (im[1][0] * p1x + im[1][1] * p2x) % 26
                shown_matrix = im
            self._hill_vector_canvas(shown_matrix, p1x, p2x, c1x, c2x, operation, "#ec4899")
        for i in range(0, len(processed), 2):
            p1, p2 = ord(processed[i]) - 65, ord(processed[i + 1]) - 65
            if operation == "encrypt":
                c1 = (matrix[0][0] * p1 + matrix[0][1] * p2) % 26
                c2 = (matrix[1][0] * p1 + matrix[1][1] * p2) % 26
                formula = f"[{matrix[0][0]} {matrix[0][1]}] \u00d7 [{p1}] = [{c1}]  (mod 26)"
                formula2 = f"[{matrix[1][0]} {matrix[1][1]}]   [{p2}]   [{c2}]"
            else:
                det = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 26
                inv_det = CryptoCore.mod_inverse(det, 26)
                inv_m = [[(matrix[1][1] * inv_det) % 26, (-matrix[0][1] * inv_det) % 26],
                         [(-matrix[1][0] * inv_det) % 26, (matrix[0][0] * inv_det) % 26]]
                c1 = (inv_m[0][0] * p1 + inv_m[0][1] * p2) % 26
                c2 = (inv_m[1][0] * p1 + inv_m[1][1] * p2) % 26
                formula = f"K\u207b\u00b9 \u00d7 [{p1}] = [{c1}]  (mod 26)"
                formula2 = f"         [{p2}]   [{c2}]"
            row = ctk.CTkFrame(self.analysis_content, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=4)
            self._analysis_tile(row, processed[i], "#ec4899", size=18, width=44, height=44)
            self._analysis_tile(row, processed[i + 1], "#ec4899", size=18, width=44, height=44)
            self._analysis_arrow(row, "#f472b6")
            self._analysis_tile(row, chr(c1 + 65), "#fb7185", size=18, width=44, height=44)
            self._analysis_tile(row, chr(c2 + 65), "#fb7185", size=18, width=44, height=44)
            ctk.CTkLabel(row, text=formula + "  " + formula2, font=("Cascadia Code", 10, "bold"), text_color="#fda4af", padx=10).pack(side="left")

    # ---------- DiffieHellman ----------
    def _analyze_diffiehellman(self, input_text, output_text):
        T = self._T
        try:
            parts = input_text.split()
            p, g, a, b = int(self.key1.get()), int(self.key2.get()), int(self.key3.get()), int(self.key4.get())
        except Exception:
            return
        A = pow(g, a, p)
        B = pow(g, b, p)
        s_alice = pow(B, a, p)
        s_bob = pow(A, b, p)
        self._analysis_hero(
            self._L("تبادل المفاتيح  Diffie-Hellman", "Key Exchange  Diffie-Hellman"),
            self._L(
                f"KAIDO و ALEX يتفقان علناً على القيم الأولية p = {p} و g = {g} ليشكلا معاً المفتاح السري دون تمريره",
                f"KAIDO and ALEX publicly agree on the base values p = {p} and g = {g} to both derive the secret key without ever sending it"
            ),
            "#06b6d4",
            "\U0001f510"
        )
        self._dh_flow_canvas(p, g, a, b, A, B, s_alice, s_bob)
        self._analysis_note(
            self._L(
                "العبقرية هنا: KAIDO و ALEX لا يتبادلان المفتاح إطلاقاً — كُل واحد يحسب المفتاح بنفسه من القيم العامة (A أو B). حتى لو اعترض المتطفل القناة، لن يستطيع فك الأسّ الخاص.",
                "The genius here: KAIDO and ALEX never exchange the key at all — each one derives it locally from the public values (A or B). Even if an eavesdropper intercepts the channel, they cannot recover the private exponent."
            ),
            "#06b6d4",
            "\U0001f9e9"
        )
        flow = [
            (self._L("KAIDO (الطرف الأول)", "KAIDO (party 1)"), self._L(
                f"يختار سرّياً a = {a}\nيحسب A = g\u1d43 mod p = {g}^a mod {p} = {A}",
                f"Chooses a private a = {a}\nComputes A = g\u1d43 mod p = {g}^a mod {p} = {A}"
            ), "#22d3ee"),
            (self._L("ALEX (الطرف الثاني)", "ALEX (party 2)"), self._L(
                f"يختار سرّياً b = {b}\nيحسب B = g\u1d47 mod p = {g}^b mod {p} = {B}",
                f"Chooses a private b = {b}\nComputes B = g\u1d47 mod p = {g}^b mod {p} = {B}"
            ), "#38bdf8"),
            (self._L("\U0001f517  التبادل", "\U0001f517  Public exchange"), self._L(
                f"KAIDO يُرسل A = {A} لـ ALEX، و ALEX يُرسل B = {B} لـ KAIDO (علنياً!)",
                f"KAIDO sends A = {A} to ALEX, and ALEX sends B = {B} to KAIDO (publicly!)"
            ), "#818cf8"),
        ]
        for title, desc, color in flow:
            card = ctk.CTkFrame(self.analysis_content, fg_color=T["BG_CARD"], corner_radius=12, border_width=1, border_color=T["BORDER_COLOR"])
            card.pack(fill="x", pady=4, padx=6)
            card.bind("<Enter>", lambda e, c=card, col=color: c.configure(border_color=col, border_width=2))
            card.bind("<Leave>", lambda e, c=card: c.configure(border_color=T["BORDER_COLOR"], border_width=1))
            ctk.CTkLabel(card, text=title, font=("Segoe UI", 13, "bold"), text_color=color, anchor="w").pack(fill="x", padx=12, pady=(8, 2))
            ctk.CTkLabel(card, text=desc, font=("Cascadia Code", 11), text_color=T["TEXT_LIGHT"], anchor="w", justify="left", wraplength=700).pack(fill="x", padx=12, pady=(0, 8))
        secret = ctk.CTkFrame(self.analysis_content, fg_color="#0e7490", corner_radius=14, height=70)
        secret.pack(fill="x", padx=6, pady=(10, 4))
        secret.pack_propagate(False)
        ctk.CTkLabel(secret, text=self._L("\U0001f511  المفتاح المشترك السري (ناتج العملية)", "\U0001f511  Shared Secret Key (output)"), font=("Segoe UI", 13, "bold"), text_color="#cffafe").pack(pady=(8, 0))
        ctk.CTkLabel(secret, text=f"s = B\u1d43 mod p = A\u1d47 mod p = {s_alice}", font=("Cascadia Code", 16, "bold"), text_color="#ffffff").pack(pady=(0, 6))

        shift = (int(s_alice) % 26) if (int(s_alice) % 26) != 0 else 26
        msg_letters = [ch for ch in (input_text or "").upper() if ch.isalpha()]
        enc_demo = CryptoCore.dh_encrypt(input_text, p, g, a, b, self.lang) if input_text else ""
        conv = ctk.CTkFrame(self.analysis_content, fg_color=T["BG_CARD"], corner_radius=14, border_width=1, border_color="#0e7490")
        conv.pack(fill="x", padx=6, pady=(4, 4))
        ctk.CTkLabel(conv, text=self._L(
            "\U0001f512  «ثم» يُستخدم السرّ كمفتاح لتشفير النص فعلياً",
            "\U0001f512  Then the secret is used as a key to actually encrypt the text"
        ), font=("Segoe UI", 13, "bold"), text_color="#67e8f9", anchor="w").pack(fill="x", padx=12, pady=(8, 2))
        ctk.CTkLabel(conv, text=self._L(
            f"نأخذ الإزاحة shift = السرّ mod 26 = {s_alice} mod 26 = {shift}، ثم نزيح كل حرف بهذا المقدار.",
            f"We take shift = secret mod 26 = {s_alice} mod 26 = {shift}, then shift each letter by that amount."
        ), font=("Segoe UI", 11), text_color=T["TEXT_LIGHT"], anchor="w", wraplength=1400, justify="left").pack(fill="x", padx=12, pady=(0, 2))
        out_row = ctk.CTkFrame(conv, fg_color="transparent")
        out_row.pack(fill="x", padx=12, pady=(2, 8))
        for ch in msg_letters[:8]:
            self._analysis_tile(out_row, ch, "#0891b2", size=16, width=40, height=42)
        self._analysis_arrow(out_row, "#34d399")
        for ch in enc_demo[:8]:
            self._analysis_tile(out_row, ch, "#34d399", size=16, width=40, height=42)
        ctk.CTkLabel(conv, text=self._L(
            f"النص المشفّر: {enc_demo}" + ("" if len(enc_demo) <= 8 else " ..."),
            f"Ciphertext: {enc_demo}" + ("" if len(enc_demo) <= 8 else " ...")
        ), font=("Cascadia Code", 12, "bold"), text_color="#6ee7b7", anchor="w").pack(fill="x", padx=12, pady=(0, 8))

    # ---------- RSA ----------
    def _analyze_rsa(self, input_text, output_text, operation):
        p, q, e = int(self.key1.get()), int(self.key2.get()), int(self.key3.get())
        n = p * q
        phi = (p - 1) * (q - 1)
        d = CryptoCore.mod_inverse(e, phi)
        self._analysis_hero(
            self._L("التشفير العام  RSA", "Public-Key Cryptography  RSA"),
            self._L(
                f"n = {p}\u00d7{q} = {n} — \u03c6(n) = {phi} — المفتاح العام (e, n) والمفتاح الخاص (d, n)",
                f"n = {p}\u00d7{q} = {n} — \u03c6(n) = {phi} — public key (e, n) and private key (d, n)"
            ),
            "#7c3aed",
            "\U0001f510"
        )
        self._analysis_chips([
            ("p", p, "#a78bfa", "\U0001d45d"),
            ("q", q, "#a78bfa", "\U0001d45e"),
            ("n", n, "#8b5cf6", "\U0001d45b"),
            ("\u03c6(n)", phi, "#8b5cf6", "\u03c6"),
            ("e", e, "#c4b5fd", "\U0001d452"),
            ("d", d, "#ddd6fe", "\U0001d451"),
        ])
        if operation == "encrypt":
            m2_title = ctk.CTkLabel(
                self.analysis_content,
                text=self._L(
                    f"أو بطريقة أخرى — سلسلة القوة لكل حرف ({len(input_text)} حرفاً):",
                    f"Or another way — the modular-power chain for each character ({len(input_text)} chars):"
                ),
                font=("Segoe UI", 11, "bold"),
                text_color="#c4b5fd",
                anchor="w"
            )
            m2_title.pack(fill="x", padx=10, pady=(12, 2))
            _rsa_max = 10
            _rsa_shown = input_text[:_rsa_max]
            if len(input_text) > _rsa_max:
                ctk.CTkLabel(self.analysis_content,
                    text=self._L(
                        f"\u26a0\ufe0f \u062a\u0645 \u0639\u0631\u0636 \u0623\u0648\u0644 {_rsa_max} \u062d\u0631\u0648\u0641 \u0641\u0642\u0637 ({len(input_text)} \u0625\u062c\u0645\u0627\u0644\u064a\u0627\u064b) \u0644\u0644\u062d\u0641\u0627\u0638 \u0639\u0644\u0649 \u0627\u0644\u0633\u0631\u0639\u0629",
                        f"\u26a0\ufe0f Showing first {_rsa_max} of {len(input_text)} chars for performance"
                    ),
                    font=("Segoe UI", 10), text_color=T["WARNING"]
                ).pack(pady=(0, 4))
            for ch in _rsa_shown:
                m = ord(ch)
                c = pow(m, e, n)
                self._rsa_lock_canvas(ch if ch.isprintable() else "\u25a1", m, c, e, n, "#7c3aed")
                self._rsa_power_canvas(ch if ch.isprintable() else "\u25a1", m, c, e, n, "#7c3aed")
                row = ctk.CTkFrame(self.analysis_content, fg_color="transparent")
                row.pack(fill="x", padx=8, pady=4)
                self._analysis_tile(row, ch if ch.isprintable() else "\u25a1", "#7c3aed", sub=str(m), size=18, width=44, height=44)
                self._analysis_arrow(row, "#a78bfa")
                self._analysis_tile(row, str(c), "#f59e0b", size=18, width=52, height=44)
                ctk.CTkLabel(row, text=f"{m}^{e} mod {n} = {c}", font=("Cascadia Code", 11, "bold"), text_color="#fcd34d", padx=10).pack(side="left")
        else:
            nums = [int(x) for x in re.findall(r"\d+", input_text)]
            m2_title = ctk.CTkLabel(
                self.analysis_content,
                text=self._L(
                    f"أو بطريقة أخرى — سلسلة القوة لكل رقم مشفّر ({len(nums)} رقماً):",
                    f"Or another way — the modular-power chain for each cipher number ({len(nums)} numbers):"
                ),
                font=("Segoe UI", 11, "bold"),
                text_color="#6ee7b7",
                anchor="w"
            )
            m2_title.pack(fill="x", padx=10, pady=(12, 2))
            for c in nums:
                m = pow(c, d, n)
                ch = chr(m) if 0 < m < 0x110000 else "?"
                self._rsa_power_canvas(str(c), c, m, d, n, "#10b981")
                row = ctk.CTkFrame(self.analysis_content, fg_color="transparent")
                row.pack(fill="x", padx=8, pady=4)
                self._analysis_tile(row, str(c), "#f59e0b", size=16, width=52, height=44)
                self._analysis_arrow(row, "#34d399")
                self._analysis_tile(row, ch, "#10b981", sub=str(m), size=18, width=44, height=44)
                ctk.CTkLabel(row, text=f"{c}^{d} mod {n} = {m} \u2192 '{ch}'", font=("Cascadia Code", 11, "bold"), text_color="#6ee7b7", padx=10).pack(side="left")

    def _analyze_sdes(self, input_text, output_text, operation):
        key = self.key1.get().strip().replace(' ', '')
        pt = input_text.strip().replace(' ', '')
        try:
            K1, K2 = CryptoCore.sdes_keygen(key)
        except Exception:
            self._analysis_hero(
                self._L("\U0001f9ed شفرة S-DES", "\U0001f9ed S-DES Cipher"),
                self._L("أدخل مفتاحًا صالحًا من 10 بت لرؤية التحليل", "Enter a valid 10-bit key to see the analysis"),
                "#0ea5e9", "\U0001f9ed"
            )
            return

        nbits = 8
        color = "#0ea5e9"
        self._analysis_hero(
            self._L("\U0001f9ed شفرة S-DES — خوارزمية كلاسيكية مبسّطة", "\U0001f9ed S-DES Cipher — Classic Simplified Algorithm"),
            self._L(
                f"نص ثنائي: {pt or '………'} — المفتاح: {key} — عملية: {'تشفير' if operation == 'encrypt' else 'فك تشفير'}",
                f"Binary text: {pt or '………'} — Key: {key} — Operation: {'Encrypt' if operation == 'encrypt' else 'Decrypt'}"
            ),
            color, "\U0001f9ed"
        )
        self._analysis_chips([
            ("K", key, "#7dd3fc", "\U0001d45d"),
            ("K1", K1, "#38bdf8", "K1"),
            ("K2", K2, "#0ea5e9", "K2"),
            ("IP", self._perm_str(CryptoCore.SDES_IP), "#64748b", "IP"),
            ("IP⁻¹", self._perm_str(CryptoCore.SDES_IP_INV), "#64748b", "IP⁻¹"),
        ])

        self._analysis_note(
            self._L(
                "S-DES تشفّر بلوك 8 بت بمفتاح 10 بت عبر جولتين من شبكة Feistel، مع توليد مفتاحين فرعيين K1 و K2 بتبديل P10 وإزاحة دائرية واختصار P8.",
                "S-DES encrypts an 8-bit block with a 10-bit key through two Feistel rounds, generating subkeys K1 & K2 via P10, circular shifts and P8."
            ), color, "\U0001f9ed"
        )

        if pt and len(pt) == 8 and all(c in '01' for c in pt):
            if operation == "decrypt":
                K1, K2 = K2, K1
            block = CryptoCore._sdes_permute(pt, CryptoCore.SDES_IP)
            L0, R0 = block[:4], block[4:]
            f1 = CryptoCore._sdes_f(R0, K1)
            L1, R1 = R0, CryptoCore._sdes_xor(L0, f1)
            L2, R2 = R1, CryptoCore._sdes_xor(L1, CryptoCore._sdes_f(R1, K2))
            ct = CryptoCore._sdes_permute(R2 + L2, CryptoCore.SDES_IP_INV)

            # ضع مربع التدوير يدويًا كبطاقة مطبوعة
            round1 = ctk.CTkFrame(self.analysis_content, fg_color="#0b2233", corner_radius=12, border_width=1, border_color="#7dd3fc")
            round1.pack(fill="x", pady=4, padx=6)
            ctk.CTkLabel(round1, text=self._L("\U0001f504 الجولة الأولى — Feistel Round 1", "\U0001f504 Round 1 — Feistel Round 1"), font=("Segoe UI", 13, "bold"), text_color="#7dd3fc").pack(anchor="w", padx=12, pady=(8, 0))
            self._sdes_math_row(round1, "IP", f"{pt} → {block}", ("L0", L0), ("R0", R0), "#0ea5e9")
            self._sdes_math_row(round1, "F", f"F(R0, K1) = {f1}", ("EP", CryptoCore._sdes_permute(R0, CryptoCore.SDES_EP)), ("⊕K1", CryptoCore._sdes_xor(CryptoCore._sdes_permute(R0, CryptoCore.SDES_EP), K1)), "#38bdf8")
            self._sdes_math_row(round1, "OUT", "", ("L1", L1), ("R1", R1), "#7dd3fc")
            ctk.CTkLabel(round1, text=self._L(
                f"L1 = R0 = {L1} | R1 = L0 ⊕ F(R0,K1) = {L0} ⊕ {f1} = {R1}",
                f"L1 = R0 = {L1} | R1 = L0 ⊕ F(R0,K1) = {L0} ⊕ {f1} = {R1}"
            ), font=("Cascadia Code", 11, "bold"), text_color="#7dd3fc", anchor="w").pack(fill="x", padx=12, pady=(0, 8))

            round2 = ctk.CTkFrame(self.analysis_content, fg_color="#0b2233", corner_radius=12, border_width=1, border_color="#0ea5e9")
            round2.pack(fill="x", pady=4, padx=6)
            ctk.CTkLabel(round2, text=self._L("\U0001f504 الجولة الثانية — Feistel Round 2", "\U0001f504 Round 2 — Feistel Round 2"), font=("Segoe UI", 13, "bold"), text_color="#0ea5e9").pack(anchor="w", padx=12, pady=(8, 0))
            self._sdes_math_row(round2, "SWAP", f"L2 = R1 = {L2}", ("L", L1), ("R", R1), "#64748b", swap=True)
            self._sdes_math_row(round2, "F", f"F(R1, K2) = {CryptoCore._sdes_f(R1, K2)}", ("EP", CryptoCore._sdes_permute(R1, CryptoCore.SDES_EP)), ("⊕K2", CryptoCore._sdes_xor(CryptoCore._sdes_permute(R1, CryptoCore.SDES_EP), K2)), "#38bdf8")
            self._sdes_math_row(round2, "OUT", "", ("R2", R2), ("L2", L2), "#0ea5e9")
            ctk.CTkLabel(round2, text=self._L(
                f"R2 = L1 ⊕ F(R1,K2) = {L1} ⊕ {CryptoCore._sdes_f(R1, K2)} = {R2}  |  pre-IP⁻¹ = {R2 + L2}",
                f"R2 = L1 ⊕ F(R1,K2) = {L1} ⊕ {CryptoCore._sdes_f(R1, K2)} = {R2}  |  pre-IP⁻¹ = {R2 + L2}"
            ), font=("Cascadia Code", 11, "bold"), text_color="#0ea5e9", anchor="w").pack(fill="x", padx=12, pady=(0, 8))

            result_row = ctk.CTkFrame(self.analysis_content, fg_color="transparent")
            result_row.pack(fill="x", padx=8, pady=6)
            self._analysis_tile(result_row, "IP⁻¹", "#64748b", size=12, width=44, height=44)
            self._analysis_arrow(result_row, "#0ea5e9")
            self._analysis_tile(result_row, f"{R2 + L2}", "#334155", size=12, width=112, height=44)
            self._analysis_arrow(result_row, "#0ea5e9")
            ctk.CTkLabel(result_row, text="→", font=("Segoe UI", 18, "bold"), text_color="#0ea5e9", width=26).pack(side="left", padx=2)
            self._analysis_tile(result_row, ct, "#0ea5e9", sub=operation, size=16, width=96, height=44)
            ctk.CTkLabel(result_row, text=self._L("الناتج النهائي (8 بت)", "Final output (8 bits)"), font=("Segoe UI", 10, "bold"), text_color="#7dd3fc", padx=10).pack(side="left")

        else:
            self._analysis_note(
                self._L(
                    f"أدخل 8 بت ثنائي ({len(pt)} بت الآن) لتشغيل الجولتين خطوة بخطوة — مثال: 10101101 بمفتاح 1010110011 → 00111100.",
                    f"Enter 8 binary bits (currently {len(pt)} bits) to run the two rounds step by step — e.g. 10101101 with key 1010110011 → 00111100."
                ), "#f59e0b", "\u26a0\ufe0f"
            )

    def _sdes_math_row(self, parent, label, expr, t1, t2, accent, swap=False):
        T = self._T
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(row, text=label, font=("Cascadia Code", 10, "bold"), text_color=accent, width=48, anchor="w").pack(side="left")
        if swap:
            ctk.CTkLabel(row, text=self._L("تبديل", "SWAP"), font=("Segoe UI", 11, "bold"), text_color="#fbbf24", width=70).pack(side="left", padx=2)
        t1_frame = ctk.CTkFrame(row, fg_color=T["BG_INPUT"], corner_radius=6)
        t1_frame.pack(side="left", padx=2)
        ctk.CTkLabel(t1_frame, text=self._L(t1[0], t1[0]), font=("Cascadia Code", 10, "bold"), text_color="#7dd3fc").pack(side="left", padx=(8, 2), pady=2)
        ctk.CTkLabel(t1_frame, text=t1[1], font=("Cascadia Code", 12, "bold"), text_color="#ffffff").pack(side="left", padx=(0, 8), pady=2)
        if t2:
            t2_frame = ctk.CTkFrame(row, fg_color=T["BG_INPUT"], corner_radius=6)
            t2_frame.pack(side="left", padx=2)
            ctk.CTkLabel(t2_frame, text=t2[0], font=("Cascadia Code", 10, "bold"), text_color="#7dd3fc").pack(side="left", padx=(8, 2), pady=2)
            ctk.CTkLabel(t2_frame, text=t2[1], font=("Cascadia Code", 12, "bold"), text_color="#ffffff").pack(side="left", padx=(0, 8), pady=2)
        if expr:
            ctk.CTkLabel(row, text=expr, font=("Cascadia Code", 10, "bold"), text_color=accent).pack(side="left", padx=6, pady=2)

    def _analyze_sdes_keys(self):
        key = self.key1.get().strip().replace(' ', '')
        try:
            K1, K2 = CryptoCore.sdes_keygen(key)
        except Exception:
            return
        self._analysis_note(
            self._L(
                f"توليد المفاتيح: K ← P10 → C|D ← إزاحات ← K1={K1} ، K2={K2}",
                f"Key schedule: K ← P10 → C|D ← shifts ← K1={K1}, K2={K2}"
            ), "#0ea5e9", "\U0001f511"
        )

    def _perm_str(self, perm):
        return ','.join(str(x) for x in perm)

    def _analyze_des(self, input_text, output_text, operation):
        key = self.key1.get().strip().replace(' ', '')
        pt = input_text.strip().replace(' ', '')
        try:
            keys = CryptoCore.des_keygen(key)
        except Exception:
            self._analysis_hero(
                self._L("\U0001f512 خوارزمية DES", "\U0001f512 DES Algorithm"),
                self._L("أدخل مفتاحًا صالحًا من 64 بت لرؤية التحليل", "Enter a valid 64-bit key to see the analysis"),
                "#f59e0b", "\U0001f512"
            )
            return

        color = "#f59e0b"
        self._analysis_hero(
            self._L("\U0001f512 DES — معيار تشفير البيانات", "\U0001f512 DES — Data Encryption Standard"),
            self._L(
                f"نص ثنائي: {pt or '………'} — المفتاح: {key[:15]}… — 16 جولة Feistel — {'تشفير' if operation == 'encrypt' else 'فك تشفير'}",
                f"Binary text: {pt or '………'} — Key: {key[:15]}… — 16 Feistel rounds — {'Encrypt' if operation == 'encrypt' else 'Decrypt'}"
            ),
            color, "\U0001f512"
        )
        self._analysis_chips([
            ("K\u2080", key[:8], "#fcd34d", "\U0001d45d"),
            ("K\u2081", keys[0], "#f59e0b", "K1"),
            ("K\u2081\u2086", keys[-1], "#f59e0b", "K16"),
            ("Effective", "56 bit", "#fb923c", "56"),
            ("Rounds", "16", "#fcd34d", "16"),
        ])

        self._analysis_note(
            self._L(
                "DES تشفّر كتلة 64 بت بمفتاح 64 بت (56 فعال بعد حذف كل 8 بت من أصل بت واحد إلى Parity bits) عبر 16 جولة Feistel. نفس الدالة تستخدم لفك التشفير مع عكس ترتيب المفاتيح K16→K1.",
                "DES encrypts a 64-bit block with a 64-bit key (56 effective after removing parity bits) through 16 Feistel rounds. Decryption reuses the same function with the subkey order reversed K16→K1."
            ), color, "\U0001f512"
        )

        if pt and len(pt) == 64 and all(c in '01' for c in pt):
            use_keys = keys
            if operation == "decrypt":
                use_keys = keys[::-1]
            block0 = CryptoCore._des_permute(pt, CryptoCore.DES_IP)
            L = block0[:32]
            R = block0[32:]
            rounds = []
            for i, k in enumerate(use_keys, 1):
                fk = CryptoCore._des_f(R, k)
                L, R = R, CryptoCore._des_xor(L, fk)
                rounds.append((i, L, R, fk))
            ct = CryptoCore._des_permute(R + L, CryptoCore.DES_FP)

            # جدول الجولات
            tbl = ctk.CTkFrame(self.analysis_content, fg_color="#13111f", corner_radius=12, border_width=1, border_color="#f59e0b")
            tbl.pack(fill="x", pady=4, padx=6)
            ctk.CTkLabel(tbl, text=self._L(
                "\U0001f4ca ملخص الــ 16 جولة (L / R بعد كل جولة)",
                "\U0001f4ca All 16 rounds summary (L / R after each round)"
            ), font=("Segoe UI", 13, "bold"), text_color="#fcd34d").pack(anchor="w", padx=12, pady=(8, 2))
            for i, lv, rv, fk in rounds:
                row = ctk.CTkFrame(tbl, fg_color="transparent")
                row.pack(fill="x", padx=12, pady=1)
                ctk.CTkLabel(row, text=f"R{i}", font=("Cascadia Code", 10, "bold"), text_color="#f59e0b", width=34, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=lv, font=("Cascadia Code", 9), text_color="#ffffff", width=250, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=rv, font=("Cascadia Code", 9), text_color="#ffffff", width=250, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=self._L(f"K{i} ⊕", f"K{i} ⊕"), font=("Cascadia Code", 9, "bold"), text_color="#fbbf24", width=40, anchor="w").pack(side="left")
            ctk.CTkLabel(tbl, text=self._L(
                f"قبل FP: R16|L16 = {R + L}",
                f"Pre-FP: R16|L16 = {R + L}"
            ), font=("Cascadia Code", 10, "bold"), text_color="#fcd34d", anchor="w").pack(fill="x", padx=12, pady=(4, 8))

            # تفاصيل الجولة الأولى
            detail = ctk.CTkFrame(self.analysis_content, fg_color="#13111f", corner_radius=12, border_width=1, border_color="#f59e0b")
            detail.pack(fill="x", pady=4, padx=6)
            ctk.CTkLabel(detail, text=self._L(
                f"\U0001f9ee تفاصيل الجولة الأولى (K\u2081 = {keys[0]})",
                f"\U0001f9ee Round 1 detail (K\u2081 = {keys[0]})"
            ), font=("Segoe UI", 13, "bold"), text_color="#fcd34d").pack(anchor="w", padx=12, pady=(8, 2))
            self._des_math_row(detail, "IP", f"{pt} → {block0}", ("L0", block0[:32]), ("R0", block0[32:]), "#f59e0b")
            self._des_math_row(detail, "E", fix_bidi(f"R0 → 48 بت"), ("E(R0)", CryptoCore._des_permute(block0[32:], CryptoCore.DES_E)), None, "#fbbf24")
            expanded = CryptoCore._des_permute(block0[32:], CryptoCore.DES_E)
            xored = CryptoCore._des_xor(expanded, keys[0])
            self._des_math_row(detail, "⊕", "", ("E(R0)⊕K1", xored), None, "#fb923c")
            self._des_math_row(detail, "S", "8 S-Boxes", ("boxes", "6×8 → 4×8"), None, "#fcd34d")
            self._des_math_row(detail, "P", "", ("F(R0,K1)", rounds[0][3]), None, "#f59e0b")
            ctk.CTkLabel(detail, text=self._L(
                f"R1 = L0 ⊕ F(R0,K1) = {block0[:32]} ⊕ {rounds[0][3]} = {rounds[0][2]}",
                f"R1 = L0 ⊕ F(R0,K1) = {block0[:32]} ⊕ {rounds[0][3]} = {rounds[0][2]}"
            ), font=("Cascadia Code", 10, "bold"), text_color="#fcd34d", anchor="w").pack(fill="x", padx=12, pady=(0, 8))

            # النتيجة النهائية
            res = ctk.CTkFrame(self.analysis_content, fg_color="transparent")
            res.pack(fill="x", padx=8, pady=6)
            self._analysis_tile(res, "FP", "#64748b", size=12, width=44, height=44)
            self._analysis_arrow(res, "#f59e0b")
            self._analysis_tile(res, f"{R + L}", "#334155", size=10, width=330, height=44)
            self._analysis_arrow(res, "#f59e0b")
            self._analysis_tile(res, ct, "#f59e0b", sub=operation, size=13, width=330, height=44)
            ctk.CTkLabel(res, text=self._L("الناتج النهائي (64 بت)", "Final output (64 bits)"), font=("Segoe UI", 10, "bold"), text_color="#fcd34d", padx=10).pack(side="left")

        else:
            self._analysis_note(
                self._L(
                    f"أدخل 64 بت ثنائي ({len(pt)} بت الآن) لتشغيل الجولات الـ16 — مثال (بلوك): {pt or '0000000100100011010001010110011110001001101010111100110111101111'} بمفتاح …1110001 → 85E813540F0AB405.",
                    f"Enter 64 binary bits (currently {len(pt)} bits) to run all 16 rounds — e.g. {pt or '0000000100100011010001010110011110001001101010111100110111101111'} with key …1110001 → 85E813540F0AB405."
                ), "#fbbf24", "\u26a0\ufe0f"
            )

    def _des_math_row(self, parent, label, expr, t1, t2, accent):
        T = self._T
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(row, text=label, font=("Cascadia Code", 10, "bold"), text_color=accent, width=34, anchor="w").pack(side="left")
        if t1:
            f1 = ctk.CTkFrame(row, fg_color=T["BG_INPUT"], corner_radius=6)
            f1.pack(side="left", padx=2)
            ctk.CTkLabel(f1, text=t1[0], font=("Cascadia Code", 9, "bold"), text_color="#fcd34d").pack(side="left", padx=(8, 2), pady=2)
            ctk.CTkLabel(f1, text=t1[1], font=("Cascadia Code", 10, "bold"), text_color="#ffffff").pack(side="left", padx=(0, 8), pady=2)
        if t2:
            f2 = ctk.CTkFrame(row, fg_color=T["BG_INPUT"], corner_radius=6)
            f2.pack(side="left", padx=2)
            ctk.CTkLabel(f2, text=t2[0], font=("Cascadia Code", 9, "bold"), text_color="#fcd34d").pack(side="left", padx=(8, 2), pady=2)
            ctk.CTkLabel(f2, text=t2[1], font=("Cascadia Code", 10, "bold"), text_color="#ffffff").pack(side="left", padx=(0, 8), pady=2)
        if expr:
            ctk.CTkLabel(row, text=expr, font=("Cascadia Code", 10, "bold"), text_color=accent).pack(side="left", padx=6, pady=2)

    def _playfair_prepare(self, text):
        text = text.upper().replace("J", "I").replace(" ", "")
        prepared = ""
        i = 0
        while i < len(text):
            prepared += text[i]
            if i + 1 < len(text):
                if text[i] == text[i + 1]:
                    prepared += "X"
                else:
                    prepared += text[i + 1]
                    i += 1
            else:
                prepared += "X"
            i += 1
        if len(prepared) % 2:
            prepared += "X"
        return prepared

    def update_keys(self):
        T = self._T
        # إزالة مراجع الحقول القديمة قبل إعادة بناء حقول الخوارزمية الجديدة.
        # وجود مرجع Tkinter قديم يجعل hasattr ينجح رغم أن العنصر دُمّر فعليًا.
        for index in range(1, 5):
            setattr(self, f"key{index}", None)
        for widget in self.key_frame.winfo_children():
            widget.destroy()

        t = TRANSLATIONS[self.lang]

        entry_style = {
            "font": ("Segoe UI", 14),
            "fg_color": T["BG_INPUT"],
            "border_width": 2,
            "border_color": T["BORDER_COLOR"],
            "corner_radius": 8
        }

        label_style = {
            "font": ("Segoe UI", 14, "bold"),
            "text_color": T["TEXT_LIGHT"]
        }

        if self.current_cipher == "Caesar":
            ctk.CTkLabel(self.key_frame, text=t["key"] + ":", **label_style).pack(side="left", padx=10)
            self.key1 = ctk.CTkEntry(self.key_frame, width=100, **entry_style)
            self.key1.insert(0, "3")
            self.key1.pack(side="left", padx=5)
            ctk.CTkLabel(self.key_frame, text="(1-25)", font=("Segoe UI", 11), text_color=T["TEXT_MUTED"]).pack(side="left", padx=5)

        elif self.current_cipher == "Affine":
            ctk.CTkLabel(self.key_frame, text=t["key_m"] + ":", **label_style).pack(side="left", padx=10)
            self.key1 = ctk.CTkEntry(self.key_frame, width=80, **entry_style)
            self.key1.insert(0, "7")
            self.key1.pack(side="left", padx=5)

            ctk.CTkLabel(self.key_frame, text=t["key_k"] + ":", **label_style).pack(side="left", padx=10)
            self.key2 = ctk.CTkEntry(self.key_frame, width=80, **entry_style)
            self.key2.insert(0, "10")
            self.key2.pack(side="left", padx=5)

        elif self.current_cipher == "Hill":
            ctk.CTkLabel(self.key_frame, text=t["key"] + ":", **label_style).pack(side="left", padx=10)
            self.key1 = ctk.CTkEntry(self.key_frame, width=200, placeholder_text="HILL \u0644\u0627 3,2,5,7", **entry_style)
            self.key1.insert(0, "HILL")
            self.key1.pack(side="left", padx=5)
            ctk.CTkLabel(self.key_frame, text="(4 \u062d\u0631\u0648\u0641 \u0623\u0648 4 \u0623\u0631\u0642\u0627\u0645)", font=("Segoe UI", 11), text_color=T["TEXT_MUTED"]).pack(side="left", padx=5)

        elif self.current_cipher == "DiffieHellman":
            ctk.CTkLabel(self.key_frame, text=t["key_p"] + ":", **label_style).pack(side="left", padx=(5, 2))
            self.key1 = ctk.CTkEntry(self.key_frame, width=50, **entry_style)
            self.key1.insert(0, "23")
            self.key1.pack(side="left", padx=2)

            ctk.CTkLabel(self.key_frame, text=t["key_g"] + ":", **label_style).pack(side="left", padx=(5, 2))
            self.key2 = ctk.CTkEntry(self.key_frame, width=50, **entry_style)
            self.key2.insert(0, "5")
            self.key2.pack(side="left", padx=2)

            ctk.CTkLabel(self.key_frame, text=t["key_a"] + ":", **label_style).pack(side="left", padx=(5, 2))
            self.key3 = ctk.CTkEntry(self.key_frame, width=50, **entry_style)
            self.key3.insert(0, "6")
            self.key3.pack(side="left", padx=2)

            ctk.CTkLabel(self.key_frame, text=t["key_b"] + ":", **label_style).pack(side="left", padx=(5, 2))
            self.key4 = ctk.CTkEntry(self.key_frame, width=50, **entry_style)
            self.key4.insert(0, "15")
            self.key4.pack(side="left", padx=2)

        elif self.current_cipher == "RSA":
            ctk.CTkLabel(self.key_frame, text=t["key_p"] + ":", **label_style).pack(side="left", padx=(10, 2))
            self.key1 = ctk.CTkEntry(self.key_frame, width=60, **entry_style)
            self.key1.insert(0, "23")
            self.key1.pack(side="left", padx=2)

            ctk.CTkLabel(self.key_frame, text=t["key_q"] + ":", **label_style).pack(side="left", padx=(10, 2))
            self.key2 = ctk.CTkEntry(self.key_frame, width=60, **entry_style)
            self.key2.insert(0, "113")
            self.key2.pack(side="left", padx=2)

            ctk.CTkLabel(self.key_frame, text=t["key_e"] + ":", **label_style).pack(side="left", padx=(10, 2))
            self.key3 = ctk.CTkEntry(self.key_frame, width=60, **entry_style)
            self.key3.insert(0, "207")
            self.key3.pack(side="left", padx=2)

        elif self.current_cipher == "SDES":
            ctk.CTkLabel(self.key_frame, text=t.get("key_binary_key", "Key (10-bit)") + ":", **label_style).pack(side="left", padx=10)
            self.key1 = ctk.CTkEntry(self.key_frame, width=160, placeholder_text="1010110011", **entry_style)
            self.key1.insert(0, "1010110011")
            self.key1.pack(side="left", padx=5)
            ctk.CTkLabel(self.key_frame, text=self._fb("(10 \u0628\u062a \u062b\u0646\u0627\u0626\u064a)"), font=("Segoe UI", 11), text_color=T["TEXT_MUTED"]).pack(side="left", padx=5)

        elif self.current_cipher == "DES":
            ctk.CTkLabel(self.key_frame, text=t.get("key_des_key", "Key (64-bit)") + ":", **label_style).pack(side="left", padx=10)
            self.key1 = ctk.CTkEntry(self.key_frame, width=300, placeholder_text="0001001100110100010101110111100110011011101111001101111111110001", **entry_style)
            self.key1.insert(0, "0001001100110100010101110111100110011011101111001101111111110001")
            self.key1.pack(side="left", padx=5)
            ctk.CTkLabel(self.key_frame, text=self._fb("(64 \u0628\u062a \u062b\u0646\u0627\u0626\u064a / 56 \u0641\u0639\u0627\u0644)"), font=("Segoe UI", 11), text_color=T["TEXT_MUTED"]).pack(side="left", padx=5)

        else:
            ctk.CTkLabel(self.key_frame, text=t["key"] + ":", **label_style).pack(side="left", padx=10)
            self.key1 = ctk.CTkEntry(self.key_frame, width=250, **entry_style)
            self.key1.insert(0, "KEY")
            self.key1.pack(side="left", padx=5)

    def setup_code_tab(self):
        if getattr(self, '_code_built', False):
            self._update_code_labels()
            return
        T = self._T

        for widget in self.tab_code.winfo_children():
            widget.destroy()

        self.tab_code.grid_columnconfigure(0, weight=1)
        self.tab_code.grid_columnconfigure(1, weight=1)
        self.tab_code.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(self.tab_code, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(15, 7), pady=15)
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        code_header = ctk.CTkFrame(left_frame, fg_color=T["BG_CARD"], corner_radius=AppSizes.CARD_RADIUS)
        code_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        code_header_content = ctk.CTkFrame(code_header, fg_color="transparent")
        code_header_content.pack(fill="x", padx=15, pady=12)

        dots = ctk.CTkFrame(code_header_content, fg_color="transparent")
        dots.pack(side="left")
        ctk.CTkLabel(dots, text="\u25cf", font=("Segoe UI", 8), text_color="#ef4444").pack(side="left", padx=2)
        ctk.CTkLabel(dots, text="\u25cf", font=("Segoe UI", 8), text_color="#f59e0b").pack(side="left", padx=2)
        ctk.CTkLabel(dots, text="\u25cf", font=("Segoe UI", 8), text_color="#10b981").pack(side="left", padx=2)

        self.code_title_label = ctk.CTkLabel(
            code_header_content,
            text="\U0001f4dd " + TRANSLATIONS[self.lang]["code_full"],
            font=("Segoe UI", 14, "bold"),
            text_color=T["TEXT_WHITE"]
        )
        self.code_title_label.pack(side="left", padx=15)

        self.copy_code_btn = ctk.CTkButton(
            code_header_content,
            text=self._L("\U0001f4cb \u0646\u0633\u062e \u0627\u0644\u0643\u0648\u062f", "\U0001f4cb Copy Code"),
            width=100,
            height=28,
            font=("Segoe UI", 11, "bold"),
            fg_color=T["BG_INPUT"],
            hover_color=T["PRIMARY"],
            text_color=T["TEXT_LIGHT"],
            corner_radius=6,
            command=self.copy_code
        )
        self.copy_code_btn.pack(side="right", padx=(10, 0))

        ctk.CTkLabel(
            code_header_content,
            text="Python",
            font=("Cascadia Code", 12),
            text_color=T["PRIMARY_LIGHT"]
        ).pack(side="right")

        code_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        code_frame.grid(row=1, column=0, sticky="nsew")
        code_frame.grid_rowconfigure(0, weight=1)
        code_frame.grid_columnconfigure(1, weight=1)

        self.line_numbers = ctk.CTkTextbox(
            code_frame,
            font=("Cascadia Code", 12),
            fg_color=T.get("BG_LINENUM", "#0c0c12"),
            text_color="#5a5a6a",
            border_width=0,
            corner_radius=AppSizes.CARD_RADIUS,
            activate_scrollbars=False,
            state="disabled",
            width=55
        )
        self.line_numbers.grid(row=0, column=0, sticky="ns")

        self.code_display = ctk.CTkTextbox(
            code_frame,
            font=("Cascadia Code", 12),
            fg_color=T.get("BG_CODE", "#111119"),
            text_color="#e2e8f0",
            border_width=2,
            border_color=T["BORDER_COLOR"],
            corner_radius=AppSizes.CARD_RADIUS,
            wrap="none"
        )
        self.code_display.grid(row=0, column=1, sticky="nsew")

        right_frame = ctk.CTkFrame(self.tab_code, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(7, 15), pady=15)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        expl_header = ctk.CTkFrame(right_frame, fg_color=T["BG_CARD"], corner_radius=AppSizes.CARD_RADIUS)
        expl_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        expl_header_content = ctk.CTkFrame(expl_header, fg_color="transparent")
        expl_header_content.pack(fill="x", padx=15, pady=12)

        self.expl_title_label = ctk.CTkLabel(
            expl_header_content,
            text="\U0001f4d6 " + TRANSLATIONS[self.lang]["explanation"],
            font=("Segoe UI", 14, "bold"),
            text_color=T["TEXT_WHITE"]
        )
        self.expl_title_label.pack(side="left")

        self.line_count_label = ctk.CTkLabel(
            expl_header_content,
            text="0 lines",
            font=("Cascadia Code", 12),
            text_color=T["TEXT_MUTED"]
        )
        self.line_count_label.pack(side="right")

        self.expl_display = ctk.CTkScrollableFrame(
            right_frame,
            fg_color=T["BG_INPUT"],
            corner_radius=AppSizes.CARD_RADIUS,
            border_width=2,
            border_color=T["BORDER_COLOR"]
        )
        self.expl_display.grid(row=1, column=0, sticky="nsew")

        self.update_code_content()

    def _highlight_code(self, code_text):
        try:
            textbox = self.code_display._textbox
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")

            lines = code_text.split('\n')
            num_lines = len(lines)
            width = len(str(num_lines)) if num_lines > 0 else 1

            code_line_starts = [0]
            for ln in lines[:-1]:
                code_line_starts.append(code_line_starts[-1] + len(ln) + 1)

            numbered_parts = []
            line_offsets = []
            pos = 0
            for i, line in enumerate(lines):
                prefix = f"{i+1:>{width}} │ "
                line_offsets.append(pos + len(prefix))
                numbered_parts.append(prefix + line)
                pos += len(prefix) + len(line) + 1

            numbered_text = '\n'.join(numbered_parts)
            textbox.insert("1.0", numbered_text)

            import re

            for tag_name in ["keyword", "builtin", "funcdef", "string", "docstring", "number", "comment", "operator", "decorator"]:
                try:
                    textbox.tag_delete(tag_name)
                except Exception:
                    pass

            textbox.tag_configure("keyword", foreground="#c084fc")
            textbox.tag_configure("builtin", foreground="#22d3ee")
            textbox.tag_configure("funcdef", foreground="#fbbf24")
            textbox.tag_configure("docstring", foreground="#86efac")
            textbox.tag_configure("string", foreground="#34d399")
            textbox.tag_configure("number", foreground="#fb923c")
            textbox.tag_configure("comment", foreground="#4a5568")
            textbox.tag_configure("operator", foreground="#f472b6")
            textbox.tag_configure("decorator", foreground="#e879f9")

            patterns = [
                ("comment", r'#[^\n]*'),
                ("docstring", r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''),
                ("string", r'"[^"]*"|\'[^\']*\''),
                ("keyword", r'\b(def|class|return|if|elif|else|for|while|import|from|try|except|raise|None|True|False|in|not|and|or|with|as|self|range|len|set|append|math|gcd)\b'),
                ("builtin", r'\b(ord|chr|int|str|print|type|isinstance|replace|upper|lower|isalpha|isdigit|split|join|format|mod_inverse|caesar_encrypt|caesar_decrypt|affine_encrypt|affine_decrypt|vigenere_encrypt|vigenere_decrypt|playfair_encrypt|playfair_decrypt|playfair_matrix|hill_encrypt|hill_decrypt|hill_matrix)\b'),
                ("funcdef", r'(?<=def\s)\w+'),
                ("decorator", r'@\w+'),
                ("number", r'\b\d+\b'),
                ("operator", r'[+\-*/%=<>!&|^~]+'),
            ]

            # بحث أسرع عن رقم السطر لأي إزاحة (بدل slice + count لكل تطابق → كان ثقيلاً)
            cs = code_line_starts
            def line_of(pos):
                return bisect.bisect_right(cs, pos) - 1

            for tag_name, pattern in patterns:
                for match in re.finditer(pattern, code_text):
                    start_in_code = match.start()
                    end_in_code = match.end()

                    start_line = line_of(start_in_code)
                    end_line = line_of(end_in_code)

                    start_in_numbered = line_offsets[start_line] + (start_in_code - cs[start_line])
                    end_in_numbered = line_offsets[end_line] + (end_in_code - cs[end_line])

                    textbox.tag_add(tag_name, f"1.0+{start_in_numbered}c", f"1.0+{end_in_numbered}c")

            textbox.configure(state="disabled")

            linenum_text = '\n'.join(f"{i+1:>{width}}" for i in range(num_lines))
            ln_box = self.line_numbers._textbox
            ln_box.configure(state="normal")
            ln_box.delete("1.0", "end")
            ln_box.insert("1.0", linenum_text)
            ln_box.configure(state="disabled")
        except Exception as e:
            try:
                textbox = self.code_display._textbox
                textbox.delete("1.0", "end")
                textbox.insert("1.0", code_text)
                textbox.configure(state="disabled")
            except Exception:
                pass

    def update_code_content(self):
        try:
            if not hasattr(self, 'code_display') or not hasattr(self, 'expl_display'):
                return

            full_code = CryptoCore.get_full_code(self.current_cipher)

            self._highlight_code(full_code)

            explanations = CryptoCore.get_explanation(self.current_cipher, self.lang)

            for widget in self.expl_display.winfo_children():
                widget.destroy()

            line_index = 0
            T = self._T
            for code_snippet, expl_text in explanations:
                if not code_snippet.strip() and not expl_text.strip():
                    continue

                line_index += 1

                card = ctk.CTkFrame(
                    self.expl_display,
                    fg_color=T["BG_CARD"],
                    corner_radius=10,
                    border_width=1,
                    border_color=T["BORDER_COLOR"]
                )
                card.pack(fill="x", pady=5, padx=5)

                def _hover_in(e, c=card, T=T):
                    c.configure(fg_color=T["BG_CARD_HOVER"], border_color=T["PRIMARY"])

                def _hover_out(e, c=card, T=T):
                    c.configure(fg_color=T["BG_CARD"], border_color=T["BORDER_COLOR"])

                card.bind("<Enter>", _hover_in)
                card.bind("<Leave>", _hover_out)

                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(fill="x", padx=15, pady=10)

                if code_snippet.strip():
                    index_label = ctk.CTkLabel(
                        content,
                        text=f"{line_index:02d}",
                        font=("Cascadia Code", 12, "bold"),
                        text_color=T["PRIMARY"],
                        width=30
                    )
                    index_label.pack(side="left", padx=(0, 10))

                    code_f = ctk.CTkFrame(content, fg_color=T["BG_INPUT"], corner_radius=6)
                    code_f.pack(fill="x", pady=(0, 8))
                    color = T["PRIMARY_LIGHT"] if "def " in code_snippet else T["ACCENT"] if "\U0001f539" in code_snippet else "#34d399"
                    ctk.CTkLabel(code_f, text=code_snippet, font=("Cascadia Code", 12, "bold" if "def " in code_snippet else "normal"), text_color=color, anchor="w", justify="left").pack(fill="x", padx=10, pady=8)

                if expl_text.strip():
                    is_ar = any("\u0600" <= c <= "\u06FF" for c in expl_text)
                    display_text = fix_bidi(expl_text) if is_ar else expl_text
                    ctk.CTkLabel(content, text=display_text, font=("Segoe UI", 13), text_color=T["TEXT_LIGHT"], anchor="w", justify="right" if is_ar else "left", wraplength=400).pack(fill="x")

            # Execution output example card
            examples = {
                "Caesar": {
                    "AR": ("\u25b6\ufe0f \u0645\u062e\u0631\u062c\u0627\u062a \u062a\u0634\u063a\u064a\u0644 \u062a\u062c\u0631\u064a\u0628\u064a\u0629 (Run Output)", "caesar_encrypt('HELLO WORLD', key=3)  \u2794  'KHOOR ZRUOG'\ncaesar_decrypt('KHOOR ZRUOG', key=3)  \u2794  'HELLO WORLD'"),
                    "EN": ("\u25b6\ufe0f Execution Output Example", "caesar_encrypt('HELLO WORLD', key=3)  \u2794  'KHOOR ZRUOG'\ncaesar_decrypt('KHOOR ZRUOG', key=3)  \u2794  'HELLO WORLD'")
                },
                "Affine": {
                    "AR": ("\u25b6\ufe0f \u0645\u062e\u0631\u062c\u0627\u062a \u062a\u0634\u063a\u064a\u0644 \u062a\u062c\u0631\u064a\u0628\u064a\u0629 (Run Output)", "affine_encrypt('HELLO', m=7, k=10)   \u2794  'ZEBBO'\naffine_decrypt('ZEBBO', m=7, k=10)   \u2794  'HELLO'"),
                    "EN": ("\u25b6\ufe0f Execution Output Example", "affine_encrypt('HELLO', m=7, k=10)   \u2794  'ZEBBO'\naffine_decrypt('ZEBBO', m=7, k=10)   \u2794  'HELLO'")
                },
                "Vigenere": {
                    "AR": ("\u25b6\ufe0f \u0645\u062e\u0631\u062c\u0627\u062a \u062a\u0634\u063a\u064a\u0644 \u062a\u062c\u0631\u064a\u0628\u064a\u0629 (Run Output)", "vigenere_encrypt('ATTACKATDAWN', key='LEMON')  \u2794  'LXFOPVEFRNHR'\nvigenere_decrypt('LXFOPVEFRNHR', key='LEMON')  \u2794  'ATTACKATDAWN'"),
                    "EN": ("\u25b6\ufe0f Execution Output Example", "vigenere_encrypt('ATTACKATDAWN', key='LEMON')  \u2794  'LXFOPVEFRNHR'\nvigenere_decrypt('LXFOPVEFRNHR', key='LEMON')  \u2794  'ATTACKATDAWN'")
                },
                "Playfair": {
                    "AR": ("\u25b6\ufe0f \u0645\u062e\u0631\u062c\u0627\u062a \u062a\u0634\u063a\u064a\u0644 \u062a\u062c\u0631\u064a\u0628\u064a\u0629 (Run Output)", "playfair_encrypt('INSTRUMENT', key='MONARCHY') \u2794 'GATLMZCLRQTX'\nplayfair_decrypt('GATLMZCLRQTX', key='MONARCHY') \u2794 'INSTRUMENT'"),
                    "EN": ("\u25b6\ufe0f Execution Output Example", "playfair_encrypt('INSTRUMENT', key='MONARCHY') \u2794 'GATLMZCLRQTX'\nplayfair_decrypt('GATLMZCLRQTX', key='MONARCHY') \u2794 'INSTRUMENT'")
                },
                "Hill": {
                    "AR": ("\u25b6\ufe0f \u0645\u062e\u0631\u062c\u0627\u062a \u062a\u0634\u063a\u064a\u0644 \u062a\u062c\u0631\u064a\u0628\u064a\u0629 (Run Output)", "hill_encrypt('HI', key='HILL')  \u2794  'JJ'  (Matrix: [[7,8],[11,11]])\nhill_decrypt('JJ', key='HILL')  \u2794  'HI'"),
                    "EN": ("\u25b6\ufe0f Execution Output Example", "hill_encrypt('HI', key='HILL')  \u2794  'JJ'  (Matrix: [[7,8],[11,11]])\nhill_decrypt('JJ', key='HILL')  \u2794  'HI'")
                },
                "DiffieHellman": {
                    "AR": ("\u25b6\ufe0f \u0645\u062e\u0631\u062c\u0627\u062a \u062a\u0634\u063a\u064a\u0644 \u062a\u062c\u0631\u064a\u0628\u064a\u0629 (Run Output)", "Public: p=23, g=5 | KAIDO (a=6) \u2794 A=8 | ALEX (b=15) \u2794 B=19\nShared Secret: s_kaido = 19^6 mod 23 = 2 | s_alex = 8^15 mod 23 = 2"),
                    "EN": ("\u25b6\ufe0f Execution Output Example", "Public: p=23, g=5 | KAIDO (a=6) \u2794 A=8 | ALEX (b=15) \u2794 B=19\nShared Secret: s_kaido = 19^6 mod 23 = 2 | s_alex = 8^15 mod 23 = 2")
                },
                "RSA": {
                    "AR": ("\u25b6\ufe0f \u0645\u062e\u0631\u062c\u0627\u062a \u062a\u0634\u063a\u064a\u0644 \u062a\u062c\u0631\u064a\u0628\u064a\u0629 (Run Output)", "Keys: p=61, q=53, e=17 \u2794 n=3233, \u03c6(n)=3120, d=2753\nrsa_encrypt('HI', 61, 53, 17)  \u2794  [3000, 1486]\nrsa_decrypt([3000, 1486], 61, 53, 17)  \u2794  'HI'"),
                    "EN": ("\u25b6\ufe0f Execution Output Example", "Keys: p=61, q=53, e=17 \u2794 n=3233, \u03c6(n)=3120, d=2753\nrsa_encrypt('HI', 61, 53, 17)  \u2794  [3000, 1486]\nrsa_decrypt([3000, 1486], 61, 53, 17)  \u2794  'HI'")
                },
                "SDES": {
                    "AR": ("\u25b6\ufe0f \u0645\u062e\u0631\u062c\u0627\u062a \u062a\u0634\u063a\u064a\u0644 \u062a\u062c\u0631\u064a\u0628\u064a\u0629 (Run Output)", "sdes_encrypt('10101101', key='1010110011')  \u2794  '00111100'\nsdes_decrypt('00111100', key='1010110011')  \u2794  '10101101'"),
                    "EN": ("\u25b6\ufe0f Execution Output Example", "sdes_encrypt('10101101', key='1010110011')  \u2794  '00111100'\nsdes_decrypt('00111100', key='1010110011')  \u2794  '10101101'")
                },
                "DES": {
                    "AR": ("\u25b6\ufe0f \u0645\u062e\u0631\u062c\u0627\u062a \u062a\u0634\u063a\u064a\u0644 \u062a\u062c\u0631\u064a\u0628\u064a\u0629 (Run Output)", "des_encrypt('0000000100100011010001010110011110001001101010111100110111101111', key='0001001100110100010101110111100110011011101111001101111111110001')\n  \u2794  '1000010111101000000100110101010000001111000010101011010000000101'  (85E813540F0AB405)"),
                    "EN": ("\u25b6\ufe0f Execution Output Example", "des_encrypt('0000000100100011010001010110011110001001101010111100110111101111', key='0001001100110100010101110111100110011011101111001101111111110001')\n  \u2794  '1000010111101000000100110101010000001111000010101011010000000101'  (85E813540F0AB405)")
                }
            }
            if self.current_cipher in examples:
                ex_title, ex_body = examples[self.current_cipher].get(self.lang, examples[self.current_cipher]["EN"])
                is_title_ar = any("\u0600" <= c <= "\u06FF" for c in ex_title)
                ex_card = ctk.CTkFrame(
                    self.expl_display,
                    fg_color=T["BG_CARD"],
                    corner_radius=10,
                    border_width=1,
                    border_color="#10b981"
                )
                ex_card.pack(fill="x", pady=(12, 6), padx=5)
                ctk.CTkLabel(
                    ex_card,
                    text=fix_bidi(ex_title) if is_title_ar else ex_title,
                    font=("Segoe UI", 12, "bold"),
                    text_color="#34d399",
                    anchor="w"
                ).pack(fill="x", padx=14, pady=(10, 4))
                ctk.CTkLabel(
                    ex_card,
                    text=ex_body,
                    font=("Cascadia Code", 11),
                    text_color=T["TEXT_WHITE"],
                    anchor="w",
                    justify="left"
                ).pack(fill="x", padx=14, pady=(0, 12))

            if hasattr(self, 'line_count_label'):
                self.line_count_label.configure(text=f"{line_index} lines")

        except Exception as e:
            if hasattr(self, 'code_display'):
                try:
                    self.code_display.configure(state="normal")
                    self.code_display.delete("1.0", "end")
                    self.code_display.insert("1.0", f"\u274c Error: {fix_bidi(str(e))}")
                    self.code_display.configure(state="disabled")
                except Exception:
                    pass

    def setup_status_bar(self):
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.update_char_count()

    def change_theme(self, new_theme):
        self._apply_theme(new_theme)

    def change_language(self, new_lang):
        self.lang = new_lang
        self.title(TRANSLATIONS[self.lang]["title"])

        tab_labels = TRANSLATIONS[self.lang]
        if hasattr(self, '_tab_btn_crypto'):
            self._tab_btn_crypto.configure(text="\U0001f510  " + tab_labels["tab_crypto"])
        if hasattr(self, '_tab_btn_code'):
            self._tab_btn_code.configure(text="\U0001f4dd  " + tab_labels["tab_code"])

        self.author.configure(text=TRANSLATIONS[self.lang]["author"])

        if hasattr(self, 'cipher_info_label'):
            self.cipher_info_label.configure(
                text=TRANSLATIONS[self.lang][f"desc_{self.current_cipher.lower()}"],
                justify="right" if self.lang == "AR" else "left"
            )

        self._update_crypto_labels()
        self.update_keys()
        self._update_code_labels()
        self.status_bar.set_status(TRANSLATIONS[self.lang]["status_ready"])

    def change_cipher(self, new_cipher):
        self.current_cipher = new_cipher
        self._analysis_ready = False
        # ألغِ أي بناء تحليل مؤجل أو تجزئة عجلات قديمة حتى لا تُبني نتيجة خاطئة أو تختفي الواجهات
        self._cancel_deferred_analysis()
        if getattr(self, "_analysis_build_after", None):
            try: self.after_cancel(self._analysis_build_after)
            except: pass
            self._analysis_build_after = None
        # أغلق صفحة التحليل إن كانت مفتوحة وأزل أي محتوى قديم ونظّف صفحة التحليل بعنصر نائب خفيف
        try:
            self._close_analysis_page()
            for w in self.analysis_content.winfo_children():
                w.destroy()
            # إخفاء زر التحليل عند تغيير الخوارزمية (لا يوجد تحليل جاهز بعد)
            try:
                self._analysis_bar.pack_forget()
            except Exception:
                pass
            try:
                self.analysis_page_title.configure(
                    text=self._L("\U0001f50d  تحليل التشفير — خطوة بخطوة", "\U0001f50d  Encryption Analysis — Step by Step")
                )
            except Exception:
                pass
            # show a light placeholder inside the (hidden) analysis page
            # so that when the user opens it they see guidance instead of a blank area
            ph = ctk.CTkLabel(
                self.analysis_content,
                text=self._L(
                    "تم تغيير الخوارزمية — أدخل النص واضغط تشفير ثم افتح التحليل لرؤية الشرح الجديد ✨",
                    "Cipher changed — enter text, run Encrypt, then open Analysis for the new explanation ✨"
                ),
                font=("Segoe UI", 11),
                text_color=self._T["TEXT_MUTED"],
                wraplength=1600,
                justify="center"
            )
            ph.pack(pady=14, padx=20)
        except Exception:
            pass

        if hasattr(self, 'cipher_info_label'):
            t = TRANSLATIONS[self.lang]
            self.cipher_info_label.configure(
                text=t[f"desc_{self.current_cipher.lower()}"],
                justify="right" if self.lang == "AR" else "left"
            )

        self._update_crypto_labels()
        self.update_keys()
        self._update_code_labels()

    def _update_crypto_labels(self):
        T = self._T
        t = TRANSLATIONS[self.lang]
        c = self.current_cipher
        if hasattr(self, 'cipher_title_label'):
            title_text = t[c.lower()]
            self.cipher_title_label.configure(text=f"\U0001f510 {fix_bidi(title_text) if self.lang == 'AR' else title_text}")
        if hasattr(self, 'cipher_desc_label'):
            desc_text = t[f"desc_{c.lower()}"]
            self.cipher_desc_label.configure(text=fix_bidi(desc_text) if self.lang == 'AR' else desc_text)
        if hasattr(self, 'security_notice_label'):
            self.security_notice_label.configure(
                text=self._L(
                    "⚠ تعليمي فقط — لا تستخدم هذه الخوارزميات لحماية بيانات حقيقية",
                    "⚠ Educational only — do not use these algorithms to protect real data"
                )
            )
        if hasattr(self, 'encrypt_btn'):
            self.encrypt_btn.configure(text="\U0001f512 " + t["encrypt"])
        if hasattr(self, 'decrypt_btn'):
            self.decrypt_btn.configure(text="\U0001f513 " + t["decrypt"])
        if hasattr(self, 'analysis_btn'):
            self.analysis_btn.configure(text="\U0001f50d " + t["analysis"])
        if hasattr(self, 'copy_btn'):
            self.copy_btn.configure(text="\U0001f4cb " + t["copy"])
        if hasattr(self, 'clear_btn'):
            self.clear_btn.configure(text="\U0001f5d1\ufe0f " + t["clear"])

    def _update_code_labels(self):
        t = TRANSLATIONS[self.lang]
        if hasattr(self, 'code_title_label'):
            self.code_title_label.configure(text="\U0001f4dd " + t["code_full"])
        if hasattr(self, 'expl_title_label'):
            self.expl_title_label.configure(text="\U0001f4d6 " + t["explanation"])
        if hasattr(self, 'copy_code_btn'):
            self.copy_code_btn.configure(text=self._L("\U0001f4cb \u0646\u0633\u062e \u0627\u0644\u0643\u0648\u062f", "\U0001f4cb Copy Code"))
        self.update_code_content()

    def _run_crypto_operation(self, operation):
        """ينفذ عملية التشفير أو فك التشفير عبر مسار موحد."""
        text = self.input_box.get("1.0", "end-1c")
        if self.current_cipher != "DiffieHellman" and not text.strip():
            message = "الرجاء إدخال النص!" if self.lang == "AR" else "Please enter text!"
            self.status_bar.set_status("⚠️ " + message, "#f59e0b")
            return

        translations = TRANSLATIONS[self.lang]
        status_key = "status_encrypting" if operation == "encrypt" else "status_decrypting"
        method_suffix = "encrypt" if operation == "encrypt" else "decrypt"

        try:
            self.status_bar.set_status(translations[status_key], "#f59e0b")
            self.update()
            result = self._dispatch_crypto(text, method_suffix)

            self.output_box.delete("1.0", "end")
            self.output_box.insert("1.0", result)
            self.status_bar.set_status("✅ " + translations["status_ready"], "#10b981")

            self.operations_count += 1
            if hasattr(self, "ops_label"):
                self.ops_label.configure(text=f"{self.operations_count} {translations['operations']}")
            self._add_to_history(self.current_cipher, text, result, operation)
            self._schedule_analysis(text, result, operation)
        except Exception as error:
            self.output_box.delete("1.0", "end")
            self.output_box.insert("1.0", f"❌ {fix_bidi(str(error))}")
            self.status_bar.set_status("❌ " + translations["status_error"], "#ef4444")

    def _dispatch_crypto(self, text, method_suffix):
        """يمرر قيم الواجهة إلى خدمة التشفير المستقلة."""
        key_fields = [getattr(self, f"key{index}", None) for index in range(1, 5)]
        keys = [field.get() if field is not None else "" for field in key_fields]
        return CryptoOperationService.execute(
            cipher=self.current_cipher,
            text=text,
            keys=keys,
            operation=method_suffix,
            lang=self.lang,
        )

    def run_encrypt(self):
        self._run_crypto_operation("encrypt")

    def run_decrypt(self):
        self._run_crypto_operation("decrypt")

    def copy_result(self):
        result = self.output_box.get("1.0", "end-1c")
        if result.strip():
            pyperclip.copy(result)
            self.status_bar.set_status("\u2705 " + TRANSLATIONS[self.lang]["status_copied"], "#10b981")

    def copy_code(self):
        code_text = CryptoCore.get_full_code(self.current_cipher)
        if code_text.strip():
            pyperclip.copy(code_text)
            self.status_bar.set_status("\u2705 " + self._L("\u062a\u0645 \u0646\u0633\u062e \u0627\u0644\u0643\u0648\u062f \u0627\u0644\u0628\u0631\u0645\u062c\u064a\u060a \u0628\u0646\u062c\u0627\u062d!", "Code copied to clipboard!"), "#10b981")

    def swap_texts(self):
        output_text = self.output_box.get("1.0", "end-1c")

        self.output_box.delete("1.0", "end")

        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", output_text)

        self.update_char_count()
        self.status_bar.set_status("\U0001f504 " + ("\u062a\u0645 \u0646\u0642\u0644 \u0627\u0644\u0646\u062a\u064a\u062c\u0629 \u0625\u0644\u0649 \u062e\u0627\u0646\u0629 \u0627\u0644\u0646\u0635!" if self.lang == "AR" else "Result moved to input!"), "#06b6d4")

    def clear_texts(self):
        self.input_box.delete("1.0", "end")
        self.output_box.delete("1.0", "end")
        self.update_char_count()
        self.status_bar.set_status(TRANSLATIONS[self.lang]["status_ready"])

    def update_char_count(self, event=None):
        try:
            text = self.input_box.get("1.0", "end-1c")
            char_count = len(text)
            word_count = len(text.split()) if text.strip() else 0

            if hasattr(self, 'input_char_count'):
                self.input_char_count.configure(text=str(char_count))

            self.status_bar.set_count(char_count, word_count)
        except Exception:
            pass

    def _on_input(self, event=None):
        """Alias kept for backward compatibility — used by quick test and key bindings."""
        return self.update_char_count(event)

    def on_closing(self):
        self.destroy()

    # ─── الاختبار السريع ───
    def _quick_test(self):
        test_data = {
            "Caesar": {"text": "HELLO WORLD", "key": "3"},
            "Affine": {"text": "HELLO WORLD", "key": "7", "key2": "10"},
            "Vigenere": {"text": "HELLO WORLD", "key": "KEY"},
            "Playfair": {"text": "HELLO WORLD", "key": "SECRET"},
            "Hill": {"text": "HELLO WORLD", "key": "HILL"},
            "DiffieHellman": {"text": "Diffie-Hellman Key Exchange", "key": "23", "key2": "5", "key3": "6", "key4": "15"},
            "RSA": {"text": "mohammed", "key": "23", "key2": "113", "key3": "207"},
            "SDES": {"text": "10101101", "key": "1010110011"},
            "DES": {"text": "0000000100100011010001010110011110001001101010111100110111101111", "key": "0001001100110100010101110111100110011011101111001101111111110001"},
        }
        data = test_data.get(self.current_cipher, test_data["Caesar"])
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", data["text"])
        self.key1.delete(0, "end")
        self.key1.insert(0, data["key"])
        if getattr(self, 'key2', None) is not None and "key2" in data:
            self.key2.delete(0, "end")
            self.key2.insert(0, data["key2"])
        if getattr(self, 'key3', None) is not None and "key3" in data:
            self.key3.delete(0, "end")
            self.key3.insert(0, data["key3"])
        if getattr(self, 'key4', None) is not None and "key4" in data:
            self.key4.delete(0, "end")
            self.key4.insert(0, data["key4"])
        self.update_char_count()
        self.run_encrypt()
        self._add_to_history(self.current_cipher, data["text"], self.output_box.get("1.0", "end-1c"), "test")

    # ─── سجل العمليات ───
    def _add_to_history(self, cipher, input_text, output_text, op_type):
        import datetime
        now = datetime.datetime.now().strftime("%H:%M")
        # السجل للبيانات الوصفية فقط؛ لا يحتفظ بالنصوص أو المفاتيح أو النتائج.
        item = {"cipher": cipher, "time": now, "type": op_type}
        self.history_items.insert(0, item)
        if len(self.history_items) > 10:
            self.history_items.pop()
        self._refresh_history()

    def _refresh_history(self):
        T = self._T
        for w in self.history_list_frame.winfo_children():
            w.destroy()
        if not self.history_items:
            no_data = "لا توجد عمليات" if self.lang == "AR" else "No operations"
            ctk.CTkLabel(self.history_list_frame, text=no_data, font=("Segoe UI", 10), text_color=T["TEXT_MUTED"]).pack(pady=10)
            return
        for item in self.history_items:
            row = ctk.CTkFrame(self.history_list_frame, fg_color=T["BG_CARD"], corner_radius=6)
            row.pack(fill="x", pady=2, padx=2)
            icon = "\U0001f510" if item["type"] == "encrypt" else "\U0001f513" if item["type"] == "decrypt" else "\U0001f9ea"
            ctk.CTkLabel(row, text=f"{icon} {item['cipher']}", font=("Segoe UI", 9, "bold"), text_color=T["PRIMARY_LIGHT"]).pack(side="left", padx=5, pady=4)
            ctk.CTkLabel(row, text=item["time"], font=("Segoe UI", 8), text_color=T["TEXT_MUTED"]).pack(side="right", padx=5, pady=4)

    def _clear_history(self):
        self.history_items.clear()
        self._refresh_history()

    # ─── نصائح المساعدة ───
    def _show_help(self):
        tips = {
            "AR": [
                ("\U0001f4a1", "نصيحة سريعة", "اضغط زر 'اختبار سريع' لتجربة الخوارزمية فوراً"),
                ("\U0001f504", "تبديل النصوص", "استخدم زر 🔄 لتبديل النص بين حقل الإدخال والإخراج"),
                ("\U0001f3af", "اختيار المفتاح", "كل خوارزمية لها مفتاح مختلف - راجع الوصف أسفل اسم الخوارزمية"),
                ("\U0001f4dd", "شرح الكود", "انتقل لتبويب 'شرح الكود' لفهم كيف تعمل كل خوارزمية"),
                ("\U0001f3a8", "الثيمات", "غيّر المظهر من قسم الثيمات في الشريط الجانبي"),
                ("\U0001f4d6", "اللغة", "يمكنك التبديل بين العربية والإنجليزية من زر اللغة"),
            ],
            "EN": [
                ("\U0001f4a1", "Quick Tip", "Press 'Quick Test' to try the algorithm instantly"),
                ("\U0001f504", "Swap Texts", "Use 🔄 to swap text between input and output"),
                ("\U0001f3af", "Key Selection", "Each algorithm has a different key - check the description below"),
                ("\U0001f4dd", "Code Explanation", "Go to 'Code Explanation' tab to understand how each algorithm works"),
                ("\U0001f3a8", "Themes", "Change the appearance from the themes section in the sidebar"),
                ("\U0001f4d6", "Language", "Switch between Arabic and English from the language button"),
            ]
        }
        dialog = ctk.CTkToplevel(self)
        dialog.title("\u2753 " + (fix_bidi("مساعدة") if self.lang == "AR" else "Help"))
        dialog.geometry("450x400")
        dialog.configure(fg_color=self._T["BG_DARK"])
        dialog.transient(self)
        dialog.grab_set()

        title = ctk.CTkLabel(dialog, text="\u2753 " + (fix_bidi("نصائح مساعدة") if self.lang == "AR" else "Help Tips"), font=("Segoe UI", 20, "bold"), text_color=self._T["TEXT_WHITE"])
        title.pack(pady=20)

        for icon, heading, desc in tips[self.lang]:
            card = ctk.CTkFrame(dialog, fg_color=self._T["BG_CARD"], corner_radius=10)
            card.pack(fill="x", padx=20, pady=5)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=10)
            ctk.CTkLabel(inner, text=f"{icon} {heading}", font=("Segoe UI", 13, "bold"), text_color=self._T["PRIMARY_LIGHT"]).pack(anchor="w")
            ctk.CTkLabel(inner, text=desc, font=("Segoe UI", 11), text_color=self._T["TEXT_LIGHT"], wraplength=350, justify="right" if self.lang == "AR" else "left").pack(anchor="w", pady=(2, 0))

        close_btn = ctk.CTkButton(dialog, text="\u2716 " + (fix_bidi("إغلاق") if self.lang == "AR" else "Close"), command=dialog.destroy, fg_color=self._T["ERROR"], hover_color=self._T["ERROR_LIGHT"], corner_radius=8, height=35)
        close_btn.pack(pady=15)

if __name__ == "__main__":
    app = CryptoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    
