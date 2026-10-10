# main.py
import customtkinter as ctk
import sys
import os
import re
import math
import bisect
import pyperclip
import queue
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.algorithms import CryptoCore
from core.service import CryptoOperationService
from ui.analysis_view import AnalysisViewMixin
from ui.key_fields import KeyFieldsMixin
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


class CryptoApp(AnalysisViewMixin, KeyFieldsMixin, ctk.CTk):
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
        self._crypto_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="crypto")
        self._crypto_job_id = 0
        self._crypto_busy = False
        self._closing = False
        self._crypto_results = queue.Queue()
        self.setup_sidebar()
        self.setup_main_content()
        self.setup_crypto_tab()
        self.setup_code_tab()
        self.setup_status_bar()
        self._build_analysis_page()
        self._crypto_built = True
        self._code_built = True
        self.after(50, self._poll_crypto_results)

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


    def _L(self, ar, en):
        return en if self.lang == "EN" else fix_bidi(ar)

    def _fb(self, text):
        """Fix bidirectional text for Arabic. Use for direct Arabic strings outside _L."""
        if self.lang == "AR":
            return fix_bidi(text)
        return text


















    # ---------- Caesar wheel (graphic) ----------




    # ---------- Vigenere strip (graphic) ----------

    # ---------- Playfair rectangle (graphic) ----------

    # ---------- Diffie-Hellman flow (graphic) ----------

    # ---------- RSA padlock (graphic) ----------

    # ---------- Affine mapping ring (graphic, method 2) ----------

    # ---------- Hill 2x2 matrix x vector (graphic, method 2) ----------

    # ---------- RSA power chain (graphic, method 2) ----------

    # ---------- Caesar ----------

    # ---------- Affine ----------

    # ---------- Vigenere ----------

    # ---------- Playfair ----------


    # ---------- Hill ----------

    # ---------- DiffieHellman ----------

    # ---------- RSA ----------









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
        if getattr(self, "_crypto_busy", False):
            self._crypto_job_id += 1
            self._crypto_busy = False
            self._set_crypto_controls_enabled(True)
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

        if self._crypto_busy:
            return

        keys = self.get_key_values()
        cipher = self.current_cipher
        lang = self.lang
        self._crypto_busy = True
        self._crypto_job_id += 1
        job_id = self._crypto_job_id
        self._set_crypto_controls_enabled(False)
        self.status_bar.set_status(translations[status_key], "#f59e0b")

        future = self._crypto_executor.submit(
            CryptoOperationService.execute,
            cipher,
            text,
            keys,
            method_suffix,
            lang,
        )
        future.add_done_callback(
            lambda completed: self._crypto_results.put((job_id, cipher, text, operation, completed))
            if not self._closing else None
        )

    def _poll_crypto_results(self):
        """يفرغ نتائج العمال داخل خيط Tkinter الرئيسي فقط."""
        if self._closing:
            return
        try:
            while True:
                item = self._crypto_results.get_nowait()
                self._finish_crypto_operation(*item)
        except queue.Empty:
            pass
        self.after(50, self._poll_crypto_results)

    def _finish_crypto_operation(self, job_id, cipher, text, operation, future):
        """يعيد نتيجة Worker إلى Tkinter فقط إذا كانت ما زالت أحدث عملية."""
        if self._closing or job_id != self._crypto_job_id:
            return
        translations = TRANSLATIONS[self.lang]
        self._crypto_busy = False
        self._set_crypto_controls_enabled(True)
        try:
            result = future.result()
            self.output_box.delete("1.0", "end")
            self.output_box.insert("1.0", result)
            self.status_bar.set_status("✅ " + translations["status_ready"], "#10b981")
            self.operations_count += 1
            if hasattr(self, "ops_label"):
                self.ops_label.configure(text=f"{self.operations_count} {translations['operations']}")
            self._add_to_history(cipher, text, result, operation)
            self._schedule_analysis(text, result, operation)
        except Exception as error:
            self.output_box.delete("1.0", "end")
            self.output_box.insert("1.0", f"❌ {fix_bidi(str(error))}")
            self.status_bar.set_status("❌ " + translations["status_error"], "#ef4444")

    def _set_crypto_controls_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        for button_name in ("encrypt_btn", "decrypt_btn"):
            button = getattr(self, button_name, None)
            if button is not None:
                button.configure(state=state)

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
        self._closing = True
        self._crypto_job_id += 1
        self._crypto_executor.shutdown(wait=False, cancel_futures=True)
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
    
