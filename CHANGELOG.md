# Changelog

يستخدم هذا الملف [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- إعداد `pyproject.toml` لفحص Ruff واكتشاف الاختبارات.
- اختبار UI Smoke قابل للتخطي تلقائيًا عند غياب بيئة رسومية.
- سير عمل GitHub Actions للفحص والاختبارات والبناء.
- أداة Benchmark في `tools/benchmark.py`.
- سجل خوارزميات مركزي في `core/registry.py` يعرّف العمليات وحقول المفاتيح وحدود الإدخال.
- اختبارات Registry للتحقق من تطابق التعريفات مع `CryptoCore` وطبقة الخدمة.

### Changed

- تنظيم سكربتات الإصلاح التاريخية داخل `tools/legacy/`.
- إزالة تعريفات واجهة fallback المكررة من `main.py`.
- ربط قائمة الخوارزميات وحقول المفاتيح وQuick Test بتعريفات Registry.

## [0.1.0] - 2026-10-11

### Added

- واجهة تعليمية ثنائية اللغة للتشفير الكلاسيكي والحديث.
- طبقة خدمة مستقلة وعمليات Worker وCache محدود.
- اختبارات رجوع والتحقق من المدخلات للخوارزميات وطبقة الخدمة.
- بناء PyInstaller عبر `CryptoEdu.spec`.
