import unittest

from ui.theme_manager import ThemeManager


class TestThemeManager(unittest.TestCase):
    def test_default_and_available_themes(self):
        manager = ThemeManager()
        self.assertEqual(manager.current_name, "Midnight")
        self.assertEqual(manager.names, ("Midnight", "Ocean", "Purple Haze", "Emerald"))
        self.assertEqual(manager.current["PRIMARY"], "#7c3aed")

    def test_select_returns_immutable_theme(self):
        manager = ThemeManager()
        selected = manager.select("Emerald")
        self.assertEqual(manager.current_name, "Emerald")
        self.assertEqual(selected["PRIMARY"], "#10b981")
        with self.assertRaises(TypeError):
            selected["PRIMARY"] = "#000000"

    def test_unknown_theme_is_rejected_without_changing_current(self):
        manager = ThemeManager("Ocean")
        with self.assertRaisesRegex(ValueError, "Unknown theme"):
            manager.select("Unknown")
        self.assertEqual(manager.current_name, "Ocean")


if __name__ == "__main__":
    unittest.main()
