# ui/widgets.py
import customtkinter as ctk
from .styles import AppColors, AppFonts, AppSizes

class GradientFrame(ctk.CTkFrame):
    """إطار مع تدرج لوني"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=AppColors.BG_DARK)

class AnimatedButton(ctk.CTkButton):
    """زر مع تأثيرات حركية محسنة"""
    def __init__(self, master, color=None, **kwargs):
        super().__init__(master, **kwargs)
        btn_color = color or AppColors.PRIMARY
        self.configure(
            corner_radius=AppSizes.BUTTON_RADIUS,
            border_width=0,
            font=AppFonts.BUTTON,
            fg_color=btn_color,
            hover_color=self._lighten_color(btn_color),
            height=AppSizes.BUTTON_HEIGHT
        )
    
    def _lighten_color(self, color):
        """تفتيح اللون قليلاً"""
        color_map = {
            AppColors.PRIMARY: AppColors.PRIMARY_LIGHT,
            AppColors.ENCRYPT_COLOR: AppColors.SUCCESS_LIGHT,
            AppColors.DECRYPT_COLOR: AppColors.WARNING_LIGHT,
            AppColors.COPY_COLOR: AppColors.PURPLE,
            AppColors.CLEAR_COLOR: AppColors.ERROR_LIGHT,
            AppColors.SUCCESS: AppColors.SUCCESS_LIGHT,
            AppColors.ERROR: AppColors.ERROR_LIGHT,
            AppColors.WARNING: AppColors.WARNING_LIGHT,
        }
        return color_map.get(color, AppColors.PRIMARY_LIGHT)

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

class CodeBlock(ctk.CTkFrame):
    """كتلة كود مع تلوين وترقيم"""
    def __init__(self, master, code_text, **kwargs):
        super().__init__(master, fg_color=AppColors.BG_INPUT, corner_radius=10, **kwargs)
        
        # شريط علوي
        header = ctk.CTkFrame(self, fg_color=AppColors.BG_CARD, corner_radius=10)
        header.pack(fill="x", padx=2, pady=(2, 0))
        
        # نقطة ملونة
        dots_frame = ctk.CTkFrame(header, fg_color="transparent")
        dots_frame.pack(side="left", padx=10, pady=8)
        
        ctk.CTkLabel(dots_frame, text="●", font=("Segoe UI", 8), text_color=AppColors.ERROR).pack(side="left", padx=2)
        ctk.CTkLabel(dots_frame, text="●", font=("Segoe UI", 8), text_color=AppColors.WARNING).pack(side="left", padx=2)
        ctk.CTkLabel(dots_frame, text="●", font=("Segoe UI", 8), text_color=AppColors.SUCCESS).pack(side="left", padx=2)
        
        # عنوان الكود
        ctk.CTkLabel(
            header,
            text="Python",
            font=AppFonts.SMALL,
            text_color=AppColors.TEXT_GRAY
        ).pack(side="right", padx=10)
        
        # محتوى الكود
        self.code_text = ctk.CTkTextbox(
            self,
            font=AppFonts.CODE,
            fg_color="transparent",
            text_color=AppColors.CODE_FUNCTION,
            wrap="word",
            activate_scrollbars=True
        )
        self.code_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.code_text.insert("1.0", code_text)
        self.code_text.configure(state="disabled")

class ExplanationCard(ctk.CTkFrame):
    """بطاقة شرح تفاعلية"""
    def __init__(self, master, code_line, explanation, index=0, **kwargs):
        super().__init__(
            master, 
            fg_color=AppColors.BG_CARD, 
            corner_radius=AppSizes.CARD_RADIUS,
            border_width=1,
            border_color=AppColors.BORDER_COLOR,
            **kwargs
        )
        
        # تأثير التمرير
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        
        # المحتوى
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)
        
        # رقم الخط
        if index > 0:
            index_label = ctk.CTkLabel(
                content,
                text=f"{index:02d}",
                font=AppFonts.CODE_BOLD,
                text_color=AppColors.PRIMARY,
                width=30
            )
            index_label.pack(side="left", padx=(0, 10))
        
        # الكود
        if code_line.strip():
            code_frame = ctk.CTkFrame(content, fg_color=AppColors.BG_INPUT, corner_radius=6)
            code_frame.pack(fill="x", pady=(0, 8))
            
            ctk.CTkLabel(
                code_frame,
                text=code_line,
                font=AppFonts.CODE,
                text_color=AppColors.CODE_FUNCTION,
                anchor="w",
                justify="left"
            ).pack(fill="x", padx=10, pady=8)
        
        # الشرح
        if explanation.strip():
            ctk.CTkLabel(
                content,
                text=explanation,
                font=AppFonts.BODY_AR,
                text_color=AppColors.TEXT_LIGHT,
                anchor="w",
                justify="right" if any("\u0600" <= c <= "\u06FF" for c in explanation) else "left",
                wraplength=400
            ).pack(fill="x", anchor="w")
    
    def _on_hover(self, event):
        """تأثير عند التمرير"""
        self.configure(fg_color=AppColors.BG_CARD_HOVER, border_color=AppColors.PRIMARY)
    
    def _on_leave(self, event):
        """إرجاع اللون الأصلي"""
        self.configure(fg_color=AppColors.BG_CARD, border_color=AppColors.BORDER_COLOR)

class InfoCard(ctk.CTkFrame):
    """بطاقة معلومات"""
    def __init__(self, master, title, value, icon="", color=None, **kwargs):
        super().__init__(
            master,
            fg_color=AppColors.BG_CARD,
            corner_radius=AppSizes.CARD_RADIUS,
            **kwargs
        )
        
        self.configure(width=150, height=80)
        self.grid_propagate(False)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=15, pady=10)
        
        # الأيقونة والعنوان
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x")
        
        if icon:
            ctk.CTkLabel(
                header,
                text=icon,
                font=("Segoe UI", 16),
                text_color=color or AppColors.PRIMARY
            ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=title,
            font=AppFonts.SMALL,
            text_color=AppColors.TEXT_GRAY
        ).pack(side="left", padx=5)
        
        # القيمة
        ctk.CTkLabel(
            content,
            text=str(value),
            font=AppFonts.STAT_NUMBER,
            text_color=color or AppColors.TEXT_WHITE
        ).pack(anchor="w", pady=(5, 0))

class TabButton(ctk.CTkButton):
    """زر تبويب مخصص"""
    def __init__(self, master, text, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color="transparent",
            hover_color=AppColors.BG_CARD_HOVER,
            font=AppFonts.BUTTON,
            text_color=AppColors.TEXT_GRAY,
            height=40,
            corner_radius=8,
            **kwargs
        )
        self.is_active = False
    
    def set_active(self, active):
        """تفعيل/تعطيل الزر"""
        self.is_active = active
        if active:
            self.configure(
                fg_color=AppColors.PRIMARY,
                text_color=AppColors.TEXT_WHITE
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=AppColors.TEXT_GRAY
            )
