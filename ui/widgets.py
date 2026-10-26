# ui/widgets.py
"""Widgets المشتركة للواجهة — لا يُستخدم منها حاليًا سوى StatusBar."""
import customtkinter as ctk

from .styles import AppColors, AppFonts


class StatusBar(ctk.CTkFrame):
    """شريط الحالة السفلي المحسّن"""
    def __init__(self, master, **kwargs):
        super().__init__(master, height=40, **kwargs)
        self.configure(fg_color=AppColors.BG_CARD, corner_radius=0)

        # الجانب الأيسر - الحالة
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(side="left", padx=15, pady=8)

        self.status_dot = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=("Segoe UI", 10),
            text_color=AppColors.SUCCESS
        )
        self.status_dot.pack(side="left", padx=(0, 5))

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="جاهز",
            font=AppFonts.SMALL,
            text_color=AppColors.TEXT_LIGHT
        )
        self.status_label.pack(side="left")

        # الجانب الأيمن - العدادات
        self.count_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.count_frame.pack(side="right", padx=15, pady=8)

        self.char_label = ctk.CTkLabel(
            self.count_frame,
            text="📝 0",
            font=AppFonts.SMALL,
            text_color=AppColors.TEXT_GRAY
        )
        self.char_label.pack(side="right", padx=10)

        self.word_label = ctk.CTkLabel(
            self.count_frame,
            text="📄 0",
            font=AppFonts.SMALL,
            text_color=AppColors.TEXT_GRAY
        )
        self.word_label.pack(side="right", padx=10)

    def set_status(self, text, color=None):
        """تحديث حالة الشريط"""
        status_color = color or AppColors.SUCCESS
        self.status_label.configure(text=text, text_color=AppColors.TEXT_LIGHT)
        self.status_dot.configure(text_color=status_color)

    def set_count(self, count, word_count=0):
        """تحديث العدادات"""
        self.char_label.configure(text=f"📝 {count}")
        self.word_label.configure(text=f"📄 {word_count}")
