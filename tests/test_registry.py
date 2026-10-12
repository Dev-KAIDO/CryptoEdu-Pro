import unittest

from core.registry import REGISTRY, algorithm_names, get_algorithm, key_defaults
from core.service import CryptoOperationService


class TestAlgorithmRegistry(unittest.TestCase):
    def test_registry_order_and_service_support_match(self):
        self.assertEqual(set(algorithm_names()), set(CryptoOperationService.SUPPORTED_CIPHERS))
        self.assertEqual(algorithm_names(), tuple(REGISTRY))
        self.assertEqual(len(algorithm_names()), 9)

    def test_every_spec_has_implementation_and_defaults(self):
        for name, spec in REGISTRY.items():
            with self.subTest(cipher=name):
                self.assertTrue(spec.method_prefix)
                self.assertTrue(spec.key_fields)
                self.assertTrue(all(field.default is not None for field in spec.key_fields))
                self.assertEqual(len(key_defaults(name)), len(spec.key_fields))
                for operation in spec.operations:
                    self.assertTrue(hasattr(__import__("core.algorithms", fromlist=["CryptoCore"]).CryptoCore, f"{spec.method_prefix}_{operation}"))

    def test_unknown_algorithm_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Cipher not implemented"):
            get_algorithm("Unknown")

    def test_registry_defaults_execute_through_service(self):
        for name in ("Caesar", "Vigenere", "SDES", "DES", "RSA"):
            spec = get_algorithm(name)
            encrypted = CryptoOperationService.execute(name, spec.quick_text, key_defaults(name), "encrypt")
            self.assertTrue(encrypted, name)


if __name__ == "__main__":
    unittest.main()
