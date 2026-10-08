import unittest

from core.algorithms import CryptoCore


class TestCryptoRoundTrips(unittest.TestCase):
    def test_caesar(self):
        encrypted = CryptoCore.caesar_encrypt("HELLO WORLD!", 3)
        self.assertEqual(encrypted, "KHOOR ZRUOG!")
        self.assertEqual(CryptoCore.caesar_decrypt(encrypted, 3), "HELLO WORLD!")

    def test_affine(self):
        encrypted = CryptoCore.affine_encrypt("HELLO", 7, 10)
        self.assertEqual(CryptoCore.affine_decrypt(encrypted, 7, 10), "HELLO")

    def test_vigenere(self):
        self.assertEqual(
            CryptoCore.vigenere_encrypt("ATTACKATDAWN", "LEMON"),
            "LXFOPVEFRNHR",
        )
        encrypted = CryptoCore.vigenere_encrypt("ATTACK AT DAWN", "LEMON")
        self.assertEqual(CryptoCore.vigenere_decrypt(encrypted, "LEMON"), "ATTACK AT DAWN")

    def test_playfair(self):
        encrypted = CryptoCore.playfair_encrypt("INSTRUMENT", "MONARCHY")
        self.assertEqual(encrypted, "GATLMZCLRQ")
        self.assertEqual(CryptoCore.playfair_decrypt(encrypted, "MONARCHY"), "INSTRUMENT")

    def test_hill(self):
        encrypted = CryptoCore.hill_encrypt("HI", "HILL")
        self.assertEqual(encrypted, "JJ")
        self.assertEqual(CryptoCore.hill_decrypt(encrypted, "HILL"), "HI")

    def test_diffie_hellman(self):
        self.assertEqual(CryptoCore.diffie_hellman_exchange(23, 5, 6, 15), "2")
        encrypted = CryptoCore.dh_encrypt("HELLO", 23, 5, 6, 15)
        self.assertEqual(CryptoCore.dh_decrypt(encrypted, 23, 5, 6, 15), "HELLO")

    def test_rsa(self):
        encrypted = CryptoCore.rsa_encrypt("HI", 61, 53, 17)
        self.assertEqual(encrypted, "3000,1486")
        self.assertEqual(CryptoCore.rsa_decrypt(encrypted, 61, 53, 17), "HI")

    def test_sdes_known_vector(self):
        encrypted = CryptoCore.sdes_encrypt("10101101", "1010110011")
        self.assertEqual(encrypted, "00111100")
        self.assertEqual(CryptoCore.sdes_decrypt(encrypted, "1010110011"), "10101101")

    def test_des_known_vector(self):
        plaintext = "0000000100100011010001010110011110001001101010111100110111101111"
        key = "0001001100110100010101110111100110011011101111001101111111110001"
        ciphertext = "1000010111101000000100110101010000001111000010101011010000000101"
        self.assertEqual(CryptoCore.des_encrypt(plaintext, key), ciphertext)
        self.assertEqual(CryptoCore.des_decrypt(ciphertext, key), plaintext)


class TestCryptoValidation(unittest.TestCase):
    def test_empty_vigenere_key_is_rejected(self):
        with self.assertRaises(ValueError):
            CryptoCore.vigenere_encrypt("ABC", "")

    def test_invalid_vigenere_key_is_rejected(self):
        with self.assertRaises(ValueError):
            CryptoCore.vigenere_encrypt("ABC", "123")

    def test_playfair_punctuation_is_rejected(self):
        with self.assertRaises(ValueError):
            CryptoCore.playfair_encrypt("A-B", "MONARCHY")

    def test_hill_invalid_key_is_rejected(self):
        with self.assertRaises(ValueError):
            CryptoCore.hill_encrypt("HI", "1,2")

    def test_hill_odd_ciphertext_is_rejected(self):
        with self.assertRaises(ValueError):
            CryptoCore.hill_decrypt("ABC", "HILL")

    def test_diffie_hellman_invalid_private_key_is_rejected(self):
        with self.assertRaises(ValueError):
            CryptoCore.diffie_hellman_exchange(23, 5, -1, 15)

    def test_rsa_invalid_parameters_are_rejected(self):
        with self.assertRaises(ValueError):
            CryptoCore.rsa_encrypt("A", 61, 61, 17)
        with self.assertRaises(ValueError):
            CryptoCore.rsa_encrypt("A", 61, 53, 1)

    def test_unsupported_alphabet_is_rejected(self):
        with self.assertRaises(ValueError):
            CryptoCore.caesar_encrypt("سلام", 3)


if __name__ == "__main__":
    unittest.main()
