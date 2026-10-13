import unittest

from ui.language_manager import LanguageManager


class TestLanguageManager(unittest.TestCase):
    def test_default_language_and_translation_access(self):
        manager = LanguageManager()
        self.assertEqual(manager.current_code, "AR")
        self.assertEqual(manager.languages, ("EN", "AR"))
        self.assertTrue(manager.is_rtl)
        self.assertEqual(manager.justify, "right")
        self.assertEqual(manager.text("encrypt"), "تشفير")

    def test_select_english_changes_text_and_direction(self):
        manager = LanguageManager()
        manager.select("EN")
        self.assertFalse(manager.is_rtl)
        self.assertEqual(manager.justify, "left")
        self.assertEqual(manager.text("encrypt"), "Encrypt")
        self.assertEqual(manager.localize("تشفير", "Encrypt"), "Encrypt")

    def test_arabic_localization_uses_bidi_helper(self):
        manager = LanguageManager("AR")
        self.assertEqual(manager.localize("تشفير", "Encrypt"), manager.bidi("تشفير"))

    def test_unknown_language_is_rejected_without_changing_current(self):
        manager = LanguageManager("EN")
        with self.assertRaisesRegex(ValueError, "Unsupported language"):
            manager.select("FR")
        self.assertEqual(manager.current_code, "EN")


if __name__ == "__main__":
    unittest.main()
