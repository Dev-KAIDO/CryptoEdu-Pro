# ui/styles.py
"""ملف الثيمات والألوان الموحدة للتطبيق"""

class AppColors:
    """ألوان التطبيق الرئيسية"""
    # الألوان الأساسية - تصميم عصري
    PRIMARY = "#6366f1"           # نيلي
    PRIMARY_LIGHT = "#818cf8"     # نيلي فاتح
    PRIMARY_DARK = "#4338ca"      # نيلي داكن
    PRIMARY_DARKER = "#312e81"    # نيلي داكن جداً
    
    SECONDARY = "#06b6d4"         # سماوي
    SECONDARY_LIGHT = "#22d3ee"   # سماوي فاتح
    
    ACCENT = "#f59e0b"            # ذهبي
    ACCENT_LIGHT = "#fbbf24"      # ذهبي فاتح
    
    PURPLE = "#a855f7"            # بنفسجي
    PINK = "#ec4899"              # وردي
    
    # ألوان الخلفية
    BG_DARK = "#0f172a"           # خلفية داكنة
    BG_CARD = "#1e293b"           # خلفية البطاقات
    BG_CARD_HOVER = "#334155"     # خلفية البطاقات عند التمرير
    BG_INPUT = "#1e293b"          # خلفية حقول الإدخال
    BG_SIDEBAR = "#0f172a"        # خلفية الشريط الجانبي
    
    # ألوان النصوص
    TEXT_WHITE = "#ffffff"
    TEXT_LIGHT = "#e2e8f0"
    TEXT_GRAY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    
    # ألوان الحالة
    SUCCESS = "#10b981"           # أخضر
    SUCCESS_LIGHT = "#34d399"
    ERROR = "#ef4444"             # أحمر
    ERROR_LIGHT = "#f87171"
    WARNING = "#f59e0b"           # أصفر
    WARNING_LIGHT = "#fbbf24"
    INFO = "#3b82f6"              # أزرق
    
    # ألوان التشفير
    ENCRYPT_COLOR = "#10b981"     # أخضر للتشفير
    DECRYPT_COLOR = "#f59e0b"     # أصفر لفك التشفير
    COPY_COLOR = "#6366f1"        # نيلي للنسخ
    CLEAR_COLOR = "#ef4444"       # أحمر للمسح
    
    # ألوان الكود
    CODE_KEYWORD = "#c084fc"      # بنفسجي للكلمات المحجوزة
    CODE_FUNCTION = "#22d3ee"     # سماوي للدوال
    CODE_STRING = "#34d399"       # أخضر للنصوص
    CODE_COMMENT = "#64748b"      # رمادي للتعليقات
    CODE_NUMBER = "#fbbf24"       # ذهبي للأرقام
    CODE_OPERATOR = "#f472b6"     # وردي للعمليات
    
    # التدرجات
    GRADIENT_START = "#6366f1"
    GRADIENT_END = "#a855f7"
    
    # الحدود
    BORDER_COLOR = "#334155"
    BORDER_FOCUS = "#6366f1"
    
    # الظل
    SHADOW = "#000000"

class AppFonts:
    """إعدادات الخطوط"""
    # خطوط عربية وإنجليزية
    TITLE_AR = ("Segoe UI", 28, "bold")
    TITLE_EN = ("Segoe UI", 28, "bold")
    
    SUBTITLE_AR = ("Segoe UI", 16, "normal")
    SUBTITLE_EN = ("Segoe UI", 16, "normal")
    
    BODY_AR = ("Segoe UI", 13, "normal")
    BODY_EN = ("Segoe UI", 13, "normal")
    
    BUTTON = ("Segoe UI", 14, "bold")
    BUTTON_LARGE = ("Segoe UI", 16, "bold")
    
    CODE = ("Cascadia Code", 12, "normal")
    CODE_BOLD = ("Cascadia Code", 12, "bold")
    CODE_LARGE = ("Cascadia Code", 14, "normal")
    
    SMALL = ("Segoe UI", 11, "normal")
    SMALL_BOLD = ("Segoe UI", 11, "bold")
    
    MONO = ("Consolas", 12, "normal")
    
    # للعناوين الكبيرة
    HERO_TITLE = ("Segoe UI", 36, "bold")
    
    # للأرقام والإحصائيات
    STAT_NUMBER = ("Segoe UI", 24, "bold")
    STAT_LABEL = ("Segoe UI", 11, "normal")

class AppSizes:
    """الأحجام والمسافات"""
    SIDEBAR_WIDTH = 280
    BUTTON_HEIGHT = 45
    BUTTON_HEIGHT_SMALL = 35
    INPUT_HEIGHT = 150
    CARD_RADIUS = 12
    BUTTON_RADIUS = 10
    PADDING_SMALL = 8
    PADDING_MEDIUM = 16
    PADDING_LARGE = 24
    PADDING_XLARGE = 32

class AppAnimations:
    """التأثيثات الحركية"""
    HOVER_SCALE = 1.02
    CLICK_SCALE = 0.98
    TRANSITION_SPEED = 200
