"""Sidebar construction for CryptoEdu Pro."""

import customtkinter as ctk

from core.registry import algorithm_names
from ui.styles import AppSizes


class SidebarViewMixin:
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
            text=self.language_manager.current["author"],
            font=("Segoe UI", 16, "bold"),
            text_color=T["PRIMARY_LIGHT"]
        )
        self.author.pack(padx=12, pady=10)

        ctk.CTkFrame(self.sidebar, height=1, fg_color=T["BORDER_COLOR"]).pack(fill="x", padx=20, pady=10)

        lang_section = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        lang_section.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            lang_section,
            text="\U0001f310 " + self.language_manager.current["language"],
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
            values=list(self.THEME_NAMES),
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
            text="\u2699\ufe0f " + self.language_manager.current["select_cipher"],
            font=("Segoe UI", 11),
            text_color=T["TEXT_GRAY"]
        ).pack(anchor="w", pady=(0, 8))

        self.cipher_menu = ctk.CTkOptionMenu(
            cipher_section,
            values=list(algorithm_names()),
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
        # === 🔎 بحث سريع عن الشفرة ===
        self.cipher_search = ctk.CTkEntry(
            cipher_section,
            placeholder_text=self._L("🔎 اكتب للبحث عن شفرة…", "🔎 Type to search a cipher…"),
            font=("Segoe UI", 12),
            height=30
        )
        self.cipher_search.pack(fill="x", pady=(8, 2))
        self.cipher_search.bind("<KeyRelease>", self._filter_cipher_results)
        self.cipher_search_results = ctk.CTkFrame(cipher_section, fg_color="transparent")

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
            text=self.language_manager.current[f"desc_{self.current_cipher.lower()}"],
            font=("Segoe UI", 11),
            text_color=T["TEXT_LIGHT"],
            wraplength=220,
            justify="right" if self.language_manager.is_rtl else "left"
        )
        self.cipher_info_label.pack(padx=15, pady=15)

        stats_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        stats_frame.pack(pady=10, padx=20, fill="x")

        self.operations_card = ctk.CTkFrame(stats_frame, fg_color=T["BG_CARD"], corner_radius=8)
        self.operations_card.pack(fill="x", pady=5)

        ctk.CTkLabel(self.operations_card, text="\U0001f4ca", font=("Segoe UI", 14)).pack(side="left", padx=10, pady=8)
        ops_text = "عمليات" if self.language_manager.is_rtl else "operations"
        self.ops_label = ctk.CTkLabel(self.operations_card, text=f"0 {ops_text}", font=("Segoe UI", 11), text_color=T["TEXT_GRAY"])
        self.ops_label.pack(side="left", pady=8)

        # === زر الاختبار السريع ===
        test_btn = ctk.CTkButton(
            stats_frame,
            text="\U0001f9ea " + ("اختبار سريع" if self.language_manager.is_rtl else "Quick Test"),
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
        ctk.CTkLabel(history_header, text="\U0001f4cb " + ("السجل" if self.language_manager.is_rtl else "History"), font=("Segoe UI", 11, "bold"), text_color=T["TEXT_LIGHT"]).pack(side="left")
        self.history_clear_btn = ctk.CTkButton(history_header, text="\U0001f5d1\ufe0f", width=25, height=25, font=("Segoe UI", 10), fg_color="transparent", hover_color=T["ERROR"], command=self._clear_history)
        self.history_clear_btn.pack(side="right")

        self.history_list_frame = ctk.CTkScrollableFrame(self.history_frame, fg_color=T["BG_INPUT"], corner_radius=6, height=120)
        self.history_list_frame.pack(fill="x", padx=8, pady=(0, 8))

        self.history_items = []

        # === زر المساعدة ===
        help_btn = ctk.CTkButton(
            stats_frame,
            text="\u2753 " + ("مساعدة" if self.language_manager.is_rtl else "Help"),
            command=self._show_help,
            font=("Segoe UI", 12, "bold"),
            fg_color=T["ACCENT"],
            hover_color=T["WARNING_LIGHT"],
            corner_radius=8,
            height=35
        )
        help_btn.pack(fill="x", pady=5)
    # === 🔎 نتائج البحث عن الشفرات ===
    def _filter_cipher_results(self, event=None):
        try:
            query = self.cipher_search.get().strip().lower()
        except Exception:
            return
        frame = self.cipher_search_results
        for w in frame.winfo_children():
            w.destroy()
        if not query:
            frame.pack_forget()
            return
        matches = []
        for name in algorithm_names():
            if query in name.lower():
                matches.append(name)
                continue
            display = self.language_manager.current.get(name.lower())
            if display and query in str(display).lower():
                matches.append(name)
        if event is not None and getattr(event, "keysym", "") == "Return" and matches:
            self._select_searched_cipher(matches[0])
            return
        if not matches:
            frame.pack_forget()
            return
        T = self._T
        frame.pack(fill="x", pady=(2, 4))
        max_results = 7
        for name in matches[:max_results]:
            display = self.language_manager.current.get(name.lower(), name)
            ctk.CTkButton(
                frame,
                text="🔐 " + display,
                anchor="w",
                height=28,
                font=("Segoe UI", 11),
                fg_color=T["BG_CARD"],
                hover_color=T["BG_CARD_HOVER"],
                text_color=T["TEXT_LIGHT"],
                corner_radius=8,
                command=lambda n=name: self._select_searched_cipher(n),
            ).pack(fill="x", pady=1)
        if len(matches) > max_results:
            ctk.CTkLabel(
                frame,
                text=self._L(f"… و{len(matches) - max_results} نتيجة إضافية", f"… and {len(matches) - max_results} more"),
                font=("Segoe UI", 9),
                text_color=T["TEXT_MUTED"]
            ).pack()

    def _select_searched_cipher(self, name):
        try:
            self.cipher_search.delete(0, "end")
            self.cipher_search_results.pack_forget()
            for w in self.cipher_search_results.winfo_children():
                w.destroy()
        except Exception:
            pass
        if hasattr(self, "cipher_menu"):
            self.cipher_menu.set(name)
        self.change_cipher(name)
