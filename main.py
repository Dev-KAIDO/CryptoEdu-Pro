# main.py
# pyrefly: ignore[missing-import]
import customtkinter as ctk
import sys
import os
import pyperclip

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.algorithms import CryptoCore
from core.app_state import AppState
from core.controller import CryptoController
from core.registry import get_algorithm, key_defaults
from ui.analysis_view import AnalysisViewMixin
from ui.key_fields import KeyFieldsMixin
from ui.code_view import CodeViewMixin
from ui.crypto_view import CryptoViewMixin
from ui.sidebar_view import SidebarViewMixin
from ui.language_manager import LanguageManager
from ui.theme_manager import ThemeManager
from core.textutils import fix_bidi

from ui.styles import AppSizes
from ui.widgets import StatusBar


class CryptoApp(SidebarViewMixin, AnalysisViewMixin, KeyFieldsMixin, CodeViewMixin, CryptoViewMixin, ctk.CTk):
    THEME_NAMES = ThemeManager().names

    @property
    def lang(self):
        return self.language_manager.current_code

    @lang.setter
    def lang(self, value):
        self.language_manager.select(value)
        self.app_state.lang = value

    @property
    def current_cipher(self):
        return self.app_state.current_cipher

    @current_cipher.setter
    def current_cipher(self, value):
        self.app_state.current_cipher = value

    @property
    def current_theme_name(self):
        return self.app_state.current_theme_name

    @current_theme_name.setter
    def current_theme_name(self, value):
        self.app_state.current_theme_name = value

    @property
    def operations_count(self):
        return self.app_state.operations_count

    @operations_count.setter
    def operations_count(self, value):
        self.app_state.operations_count = value

    @property
    def _crypto_busy(self):
        return self.app_state.crypto_busy

    @_crypto_busy.setter
    def _crypto_busy(self, value):
        self.app_state.crypto_busy = value

    @property
    def _crypto_job_id(self):
        return self.app_state.crypto_job_id

    @_crypto_job_id.setter
    def _crypto_job_id(self, value):
        self.app_state.crypto_job_id = value

    @property
    def _closing(self):
        return self.app_state.closing

    @_closing.setter
    def _closing(self, value):
        self.app_state.closing = value

    def __init__(self):
        super().__init__()

        self.app_state = AppState()
        self.controller = CryptoController(self.app_state)
        self.language_manager = LanguageManager(self.app_state.lang)
        self.theme_manager = ThemeManager(self.current_theme_name)
        self._T = self.theme_manager.current

        self.title(self.language_manager.current["title"])
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
        self._code_dirty = False
        self._code_highlight_after = None
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
        self.after(50, self._poll_crypto_results)

    def _apply_theme(self, theme_name=None):
        if theme_name:
            self.theme_manager.select(theme_name)
            self.current_theme_name = self.theme_manager.current_name
        self._T = self.theme_manager.current

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

        tab_labels = self.language_manager.current

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
        if tab_name == "code" and getattr(self, "_code_dirty", False):
            self._code_dirty = False
            self.after(10, self.update_code_content)
        self._current_tab = tab_name
        # ensure visible canvas is updated without blocking
        self.update_idletasks()



    def _L(self, ar, en):
        return self.language_manager.localize(ar, en)

    def _fb(self, text):
        """Fix bidirectional text for Arabic. Use for direct Arabic strings outside _L."""
        return self.language_manager.bidi(text)


















    def setup_status_bar(self):
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.update_char_count()

    def change_theme(self, new_theme):
        self._apply_theme(new_theme)

    def change_language(self, new_lang):
        self.lang = new_lang
        self.title(self.language_manager.current["title"])

        tab_labels = self.language_manager.current
        if hasattr(self, '_tab_btn_crypto'):
            self._tab_btn_crypto.configure(text="\U0001f510  " + tab_labels["tab_crypto"])
        if hasattr(self, '_tab_btn_code'):
            self._tab_btn_code.configure(text="\U0001f4dd  " + tab_labels["tab_code"])

        self.author.configure(text=self.language_manager.current["author"])

        if hasattr(self, 'cipher_info_label'):
            self.cipher_info_label.configure(
                text=self.language_manager.current[f"desc_{self.current_cipher.lower()}"],
                justify="right" if self.language_manager.is_rtl else "left"
            )

        self._update_crypto_labels()
        self.update_keys()
        self._update_code_labels()
        self.status_bar.set_status(self.language_manager.current["status_ready"])
        # إعادة تخطيط صف أزرار العمليات وشريط الإحصاءات ونصوص الشريط الجانبي للاتجاه الجديد
        try:
            self._layout_main_buttons()
        except Exception:
            pass
        try:
            self._refresh_sidebar_texts()
        except Exception:
            pass
        try:
            self.after(90, self._update_text_stats)
        except Exception:
            pass
        # زر العودة في صفحة التحليل: نصه ورسمة سهمه يتبعان اللغة الجديدة
        try:
            self.analysis_page_back.configure(
                text=("\u2192  " if self.language_manager.is_rtl else "\u2190  ")
                + self._L("العودة إلى التشفير", "Back to Encryption")
            )
        except Exception:
            pass

    def change_cipher(self, new_cipher):
        get_algorithm(new_cipher)
        if getattr(self, "_crypto_busy", False):
            self.controller.cancel_current()
            self._set_crypto_controls_enabled(True)
        self.current_cipher = new_cipher
        if hasattr(self, "cipher_menu") and hasattr(self, "_cipher_display"):
            wanted = self._cipher_display(new_cipher)
            if self.cipher_menu.get() != wanted:
                self.cipher_menu.set(wanted)
        self._analysis_ready = False
        # ألغِ أي بناء تحليل مؤجل أو تجزئة عجلات قديمة حتى لا تُبني نتيجة خاطئة أو تختفي الواجهات
        self._cancel_deferred_analysis()
        if getattr(self, "_analysis_build_after", None):
            try: self.after_cancel(self._analysis_build_after)
            except Exception: pass
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
            t = self.language_manager.current
            self.cipher_info_label.configure(
                text=t[f"desc_{self.current_cipher.lower()}"],
                justify="right" if self.language_manager.is_rtl else "left"
            )

        self._update_crypto_labels()
        self.update_keys()
        self._update_code_labels()

    def _update_crypto_labels(self):
        t = self.language_manager.current
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
        t = self.language_manager.current
        if hasattr(self, 'code_title_label'):
            self.code_title_label.configure(text="\U0001f4dd " + t["code_full"])
        if hasattr(self, 'expl_title_label'):
            self.expl_title_label.configure(text="\U0001f4d6 " + t["explanation"])
        if hasattr(self, 'copy_code_btn'):
            self.copy_code_btn.configure(text=self._L("\U0001f4cb \u0646\u0633\u062e \u0627\u0644\u0643\u0648\u062f", "\U0001f4cb Copy Code"))
        # الأداء: إعادة بناء الشيفرة (~1200 سطر مُلوَّن) كانت تتكلف 300-570ms في كل تغيير شفرة.
        # تُعاد الآن بعد idle إن كان التبويب ظاهرًا، وإلا تؤجَّل حتى عودة المستخدم لتبويب الشيفرة.
        if getattr(self, "_current_tab", None) == "code":
            self.after(10, self.update_code_content)
        else:
            self._code_dirty = True

    def _run_crypto_operation(self, operation):
        """ينفذ عملية التشفير أو فك التشفير عبر مسار موحد."""
        text = self.input_box.get("1.0", "end-1c")
        if self.current_cipher != "DiffieHellman" and not text.strip():
            message = "الرجاء إدخال النص!" if self.language_manager.is_rtl else "Please enter text!"
            self.status_bar.set_status("⚠️ " + message, "#f59e0b")
            return

        translations = self.language_manager.current
        status_key = "status_encrypting" if operation == "encrypt" else "status_decrypting"
        method_suffix = "encrypt" if operation == "encrypt" else "decrypt"

        if self._crypto_busy:
            return

        keys = self.get_key_values()
        cipher = self.current_cipher
        lang = self.lang
        self._set_crypto_controls_enabled(False)
        self.status_bar.set_status(translations[status_key], "#f59e0b")

        job_id = self.controller.submit(cipher, text, keys, method_suffix, lang)
        if job_id is None:
            self._set_crypto_controls_enabled(True)

    def _poll_crypto_results(self):
        """يفرغ نتائج العمال داخل خيط Tkinter الرئيسي فقط."""
        if self._closing:
            return
        for result in self.controller.poll_results():
            self._finish_crypto_operation(
                result.job_id,
                result.cipher,
                result.text,
                result.keys,
                result.operation,
                result.future,
            )
        self.after(50, self._poll_crypto_results)

    def _finish_crypto_operation(self, job_id, cipher, text, keys, operation, future):
        """يعيد نتيجة Worker إلى Tkinter فقط إذا كانت ما زالت أحدث عملية."""
        if not self.controller.is_current(job_id):
            return
        translations = self.language_manager.current
        self.controller.mark_finished(job_id)
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
            self._schedule_analysis(text, result, operation, keys)
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

    def run_encrypt(self):
        self._run_crypto_operation("encrypt")

    def run_decrypt(self):
        self._run_crypto_operation("decrypt")

    def copy_result(self):
        result = self.output_box.get("1.0", "end-1c")
        if result.strip():
            pyperclip.copy(result)
            self.status_bar.set_status("\u2705 " + self.language_manager.current["status_copied"], "#10b981")

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
        self.status_bar.set_status("\U0001f504 " + ("\u062a\u0645 \u0646\u0642\u0644 \u0627\u0644\u0646\u062a\u064a\u062c\u0629 \u0625\u0644\u0649 \u062e\u0627\u0646\u0629 \u0627\u0644\u0646\u0635!" if self.language_manager.is_rtl else "Result moved to input!"), "#06b6d4")

    def clear_texts(self):
        self.input_box.delete("1.0", "end")
        self.output_box.delete("1.0", "end")
        self.update_char_count()
        self.status_bar.set_status(self.language_manager.current["status_ready"])

    def update_char_count(self, event=None):
        try:
            text = self.input_box.get("1.0", "end-1c")
            char_count = len(text)
            word_count = len(text.split()) if text.strip() else 0

            if hasattr(self, 'input_char_count'):
                self.input_char_count.configure(text=str(char_count))

            self.status_bar.set_count(char_count, word_count)
            if hasattr(self, "_update_text_stats"):
                self._update_text_stats()
        except Exception:
            pass

    def _on_input(self, event=None):
        """Alias kept for backward compatibility — used by quick test and key bindings."""
        return self.update_char_count(event)

    def on_closing(self):
        self.controller.close()
        self.destroy()

    # ─── الاختبار السريع ───
    def _quick_test(self):
        spec = get_algorithm(self.current_cipher)
        data = {"text": spec.quick_text, "keys": key_defaults(self.current_cipher)}
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", data["text"])
        for index, value in enumerate(data["keys"], start=1):
            field = getattr(self, f"key{index}", None)
            if field is not None:
                field.delete(0, "end")
                field.insert(0, value)
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
            no_data = "لا توجد عمليات" if self.language_manager.is_rtl else "No operations"
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
        dialog.title("\u2753 " + (fix_bidi("مساعدة") if self.language_manager.is_rtl else "Help"))
        dialog.geometry("450x400")
        dialog.configure(fg_color=self._T["BG_DARK"])
        dialog.transient(self)
        dialog.grab_set()

        title = ctk.CTkLabel(dialog, text="\u2753 " + (fix_bidi("نصائح مساعدة") if self.language_manager.is_rtl else "Help Tips"), font=("Segoe UI", 20, "bold"), text_color=self._T["TEXT_WHITE"])
        title.pack(pady=20)

        for icon, heading, desc in tips[self.lang]:
            card = ctk.CTkFrame(dialog, fg_color=self._T["BG_CARD"], corner_radius=10)
            card.pack(fill="x", padx=20, pady=5)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=10)
            ctk.CTkLabel(inner, text=f"{icon} {heading}", font=("Segoe UI", 13, "bold"), text_color=self._T["PRIMARY_LIGHT"]).pack(anchor="w")
            ctk.CTkLabel(inner, text=desc, font=("Segoe UI", 11), text_color=self._T["TEXT_LIGHT"], wraplength=350, justify="right" if self.language_manager.is_rtl else "left").pack(anchor="w", pady=(2, 0))

        close_btn = ctk.CTkButton(dialog, text="\u2716 " + (fix_bidi("إغلاق") if self.language_manager.is_rtl else "Close"), command=dialog.destroy, fg_color=self._T["ERROR"], hover_color=self._T["ERROR_LIGHT"], corner_radius=8, height=35)
        close_btn.pack(pady=15)

if __name__ == "__main__":
    app = CryptoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    
