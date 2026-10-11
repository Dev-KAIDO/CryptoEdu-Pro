import os
import time
import unittest


@unittest.skipUnless(os.environ.get("DISPLAY"), "UI smoke tests require a display (use xvfb-run on CI)")
class TestCryptoAppSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from main import CryptoApp

        cls.app = CryptoApp()

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "app", None) is not None:
            cls.app.on_closing()

    def pump_worker(self):
        deadline = time.monotonic() + 5
        while self.app._crypto_busy and time.monotonic() < deadline:
            self.app.update()
            time.sleep(0.005)
        self.assertFalse(self.app._crypto_busy, "crypto worker did not finish within five seconds")

    def test_navigation_and_language(self):
        for language in ("AR", "EN"):
            self.app.change_language(language)
            self.app.change_cipher("Caesar")
            self.app.change_theme("Midnight")
            self.assertTrue(self.app.sidebar.winfo_exists())
            self.assertTrue(self.app.input_box.winfo_exists())
            self.assertTrue(self.app.code_display.winfo_exists())

    def test_quick_test_and_code_view(self):
        self.app.change_cipher("Caesar")
        self.app._quick_test()
        self.pump_worker()
        self.assertTrue(self.app.output_box.get("1.0", "end-1c"))
        self.app.update_code_content()
        self.assertTrue(self.app.code_display.get("1.0", "end-1c"))


if __name__ == "__main__":
    unittest.main()
