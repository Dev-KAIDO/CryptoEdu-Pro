"""Main encryption-tab construction for CryptoEdu Pro."""

import customtkinter as ctk

from ui.styles import AppSizes


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
