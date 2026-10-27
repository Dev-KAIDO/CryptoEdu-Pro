"""Main encryption-tab construction for CryptoEdu Pro."""

import customtkinter as ctk

from ui.styles import AppSizes
from core.alphabet import ARABIC_INDEX, LATIN_INDEX, is_arabic_text, normalize_arabic


class CryptoViewMixin:
    def setup_crypto_tab(self):
        if getattr(self, '_crypto_built', False):
            self._update_crypto_labels()
            return
        T = self._T
        t = self.language_manager.current

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
        # === 📊 شريط إحصاءات الحروف — يتحدث مع كل ضغطة في النص ===
        self._stats_canvas = ctk.CTkCanvas(
            self._input_card,
            height=64,
            bg=T["BG_INPUT"],
            highlightthickness=0,
            bd=0
        )
        self._stats_canvas.pack(fill="x", padx=15, pady=(0, 12))
        self.input_box.bind("<KeyRelease>", self._update_text_stats, add="+")
        self.after(60, self._update_text_stats)

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

        self._btn_divider = ctk.CTkFrame(main_btn_frame, width=2, height=30, fg_color=T["BORDER_COLOR"])
        self._btn_divider.pack(side="left", padx=10)

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

        self._swap_arrow_label = ctk.CTkLabel(
            main_btn_frame,
            text="\u2194",
            font=("Segoe UI", 16),
            text_color=T["TEXT_GRAY"]
        )
        self._swap_arrow_label.pack(side="right", padx=5)
        # تصفيف الأزرار حسب اتجاه اللغة الحالي (RTL ⇒ التشفير أعلى اليمين)
        self._layout_main_buttons()

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
    # === 📊 إحصاءات تكرار الحروف (عربي 28 / إنجليزي 26 آليًا) ===
    def _layout_main_buttons(self):
        """يصفّ صف أزرار العمليات حسب الاتجاه: زر التشفير على الجهة الأولى للقراءة."""
        needed = ("encrypt_btn", "decrypt_btn", "analysis_btn", "copy_btn", "clear_btn", "swap_btn", "_btn_divider", "_swap_arrow_label")
        if not all(hasattr(self, a) for a in needed):
            return
        rtl = self.language_manager.is_rtl
        side = "right" if rtl else "left"
        other = "left" if rtl else "right"
        pad = (10, 0) if rtl else (0, 10)
        for widget, widget_pad in (
            (self.encrypt_btn, pad), (self.decrypt_btn, pad), (self.analysis_btn, pad),
            (self._btn_divider, (10, 10)), (self.copy_btn, pad), (self.clear_btn, (0, 0)),
        ):
            widget.pack_forget()
            widget.pack(side=side, padx=widget_pad)
        self.swap_btn.pack_forget()
        self.swap_btn.pack(side=other)
        self._swap_arrow_label.pack_forget()
        self._swap_arrow_label.pack(side=other, padx=5)

    def _update_text_stats(self, event=None):
        """يرسم أعمدة تكرار كل حروف النص المُدخل (تتسع لكل الأحرف حسب العرض)."""
        canvas = getattr(self, "_stats_canvas", None)
        if canvas is None:
            return
        try:
            if not canvas.winfo_exists():
                return
            try:
                text = self.input_box.get("1.0", "end-1c")
            except Exception:
                return
            canvas.delete("all")
            T = self._T
            h = 64
            w = max(int(canvas.winfo_width() or 0), int(canvas.winfo_reqwidth() or 0), 320)
            # حد رقيق يفصل شريط الإحصاءات عن مربع النص ويدمجه بصرياً في البطاقة
            canvas.create_rectangle(1, 1, max(w - 1, 2), h - 1, outline=T["BORDER_COLOR"])
            if is_arabic_text(text):
                counts = {}
                for ch in normalize_arabic(text):
                    if ch in ARABIC_INDEX:
                        counts[ch] = counts.get(ch, 0) + 1
                mode = self._L("عربي (28)", "Arabic (28)")
            else:
                counts = {}
                for ch in text.upper():
                    if ch in LATIN_INDEX:
                        counts[ch] = counts.get(ch, 0) + 1
                mode = self._L("إنجليزي (26)", "English (26)")
            total = sum(counts.values())
            title = f"📊 {total} {self._L('حرفًا', 'letters')} · {len(counts)} {self._L('مختلفًا', 'unique')} · {mode}"
            canvas.create_text(14, h // 2, text=title, font=("Segoe UI", 11, "bold"), fill=T["TEXT_LIGHT"], anchor="w")
            if not counts:
                canvas.create_text(
                    w - 16, h // 2,
                    text=self._L("ابدأ بكتابة النص لعرض الإحصاءات…", "Start typing to view stats…"),
                    font=("Segoe UI", 10),
                    fill=T["TEXT_MUTED"],
                    anchor="e"
                )
                return
            palette = ("#7c3aed", "#06b6d4", "#10b981", "#f59e0b", "#ec4899", "#22d3ee", "#a78bfa", "#34d399", "#fbbf24", "#f472b6")
            # كل الحروف المختلفة تُعرض (حتى 26/28 عمودًا) — التباعد ينكمش تلقائيًا حسب مساحة العرض
            by_rank = sorted(counts.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
            col_w = max(16, min(30, (w - 240) // len(by_rank)))
            max_cols = (w - 240) // col_w
            by_rank = by_rank[:max(1, max_cols)]
            max_count = by_rank[0][1]
            x = w - 18
            for i, (ch, cnt) in enumerate(by_rank):
                cx = x - col_w / 2
                bar_h = max(3, int(round(cnt / max_count * 20)))
                canvas.create_text(cx, 13, text=ch, font=("Segoe UI", 11 if col_w >= 24 else 10, "bold"), fill=T["TEXT_LIGHT"])
                canvas.create_text(cx, 27, text=str(cnt), font=("Segoe UI", 8 if col_w >= 24 else 7), fill=T["TEXT_MUTED"])
                canvas.create_rectangle(x - col_w + 3, h - 6 - bar_h, x - 3, h - 6, fill=palette[i % len(palette)], outline="")
                x -= col_w
        except Exception:
            pass
