"""Interactive encryption-analysis UI for CryptoEdu Pro.

The mixin relies on the host application for shared state such as ``_T``,
``lang``, ``current_cipher`` and ``analysis_content``. Rendering and algorithm
walkthroughs live here so the main window remains focused on application flow.
"""

import bisect
import math
import re

import customtkinter as ctk

from core.algorithms import CryptoCore
from core.textutils import fix_bidi
from ui.styles import AppSizes


class AnalysisViewMixin:
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
