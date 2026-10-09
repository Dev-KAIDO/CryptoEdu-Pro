import unittest

from core.service import CryptoOperationService


class TestCryptoOperationService(unittest.TestCase):
    def round_trip(self, cipher, plaintext, keys):
        encrypted = CryptoOperationService.execute(cipher, plaintext, keys, "encrypt")
        decrypted = CryptoOperationService.execute(cipher, encrypted, keys, "decrypt")
        return encrypted, decrypted

    def test_classical_ciphers(self):
        cases = [
            ("Caesar", "HELLO WORLD", ["3", "", "", ""]),
            ("Affine", "HELLO WORLD", ["7", "10", "", ""]),
            ("Vigenere", "ATTACK AT DAWN", ["LEMON", "", "", ""]),
            ("Playfair", "INSTRUMENT", ["MONARCHY", "", "", ""]),
            ("Hill", "HELP", ["HILL", "", "", ""]),
        ]
        for cipher, plaintext, keys in cases:
            with self.subTest(cipher=cipher):
                encrypted, decrypted = self.round_trip(cipher, plaintext, keys)
                self.assertTrue(encrypted)
                self.assertEqual(decrypted, plaintext.replace(" ", "") if cipher == "Playfair" else plaintext.upper())

    def test_public_key_and_binary_ciphers(self):
        cases = [
            ("DiffieHellman", "HELLO", ["23", "5", "6", "15"]),
            ("RSA", "HI", ["61", "53", "17", ""]),
            ("SDES", "10101101", ["1010110011", "", "", ""]),
            ("DES", "0000000100100011010001010110011110001001101010111100110111101111", ["0001001100110100010101110111100110011011101111001101111111110001", "", "", ""]),
        ]
        for cipher, plaintext, keys in cases:
            with self.subTest(cipher=cipher):
                encrypted, decrypted = self.round_trip(cipher, plaintext, keys)
                self.assertTrue(encrypted)
                self.assertEqual(decrypted, plaintext)

    def test_invalid_operation_and_cipher(self):
        with self.assertRaises(ValueError):
            CryptoOperationService.execute("Unknown", "ABC", [], "encrypt")
        with self.assertRaises(ValueError):
            CryptoOperationService.execute("Caesar", "ABC", ["3"], "compress")

    def test_key_parsing_error_is_clear(self):
        with self.assertRaisesRegex(ValueError, "Key m must be an integer"):
            CryptoOperationService.execute("Affine", "ABC", ["not-a-number", "10"], "encrypt")

    def test_text_size_limits_are_enforced(self):
        with self.assertRaisesRegex(ValueError, "maximum is 1000"):
            CryptoOperationService.execute("RSA", "A" * 1001, ["61", "53", "17"], "encrypt")
        with self.assertRaisesRegex(ValueError, "maximum is 100000"):
            CryptoOperationService.execute("Caesar", "A" * 100001, ["3"], "encrypt")

    def test_educational_prime_limit_is_enforced(self):
        with self.assertRaisesRegex(ValueError, "too large"):
            CryptoOperationService.execute("RSA", "A", ["1000003", "53", "17"], "encrypt")


if __name__ == "__main__":
    unittest.main()
