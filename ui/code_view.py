"""Code-explanation tab UI for CryptoEdu Pro."""

import bisect
import re

import customtkinter as ctk

from core.algorithms import CryptoCore
from core.textutils import fix_bidi
from ui.styles import AppSizes
from ui.translations import TRANSLATIONS


class CodeViewMixin:
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
