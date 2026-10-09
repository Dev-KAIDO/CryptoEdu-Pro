"""Application service for cryptographic operations.

This module intentionally has no GUI dependencies.  The desktop UI supplies
raw field values, while this service owns operation selection and key parsing.
"""

from .algorithms import CryptoCore


class CryptoOperationService:
    """واجهة مستقلة لتنفيذ التشفير وفك التشفير من أي واجهة استخدام."""

    MAX_TEXT_LENGTH = 100_000
    MAX_RSA_TEXT_LENGTH = 1_000
    MAX_PRIME = 1_000_000

    SUPPORTED_CIPHERS = frozenset(
        {
            "Caesar",
            "Affine",
            "Vigenere",
            "Playfair",
            "Hill",
            "DiffieHellman",
            "RSA",
            "SDES",
            "DES",
        }
    )
    SUPPORTED_OPERATIONS = frozenset({"encrypt", "decrypt"})

    @classmethod
    def execute(cls, cipher, text, keys, operation, lang="AR"):
        """تنفذ العملية باستخدام قيم مفاتيح خام قادمة من الواجهة.

        Parameters
        ----------
        cipher: str
            اسم الخوارزمية كما يظهر في التطبيق.
        text: str
            النص الأصلي أو النص المشفر.
        keys: sequence[str]
            قيم حقول المفاتيح بالترتيب الظاهر في الواجهة.
        operation: str
            ``encrypt`` أو ``decrypt``.
        lang: str
            لغة رسائل أخطاء خوارزميات DH وRSA.
        """
        if cipher not in cls.SUPPORTED_CIPHERS:
            raise ValueError(f"Cipher not implemented: {cipher}")
        if operation not in cls.SUPPORTED_OPERATIONS:
            raise ValueError(f"Operation not implemented: {operation}")
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        max_length = cls.MAX_RSA_TEXT_LENGTH if cipher == "RSA" else cls.MAX_TEXT_LENGTH
        if len(text) > max_length:
            raise ValueError(f"Text is too long; maximum is {max_length} characters")

        key_values = tuple(keys)
        method = getattr(CryptoCore, f"{cls._prefix(cipher)}_{operation}")

        if cipher == "Caesar":
            return method(text, cls._int_key(key_values, 0, "key"))
        if cipher in {"Vigenere", "Playfair", "Hill"}:
            return method(text, cls._key(key_values, 0, cipher))
        if cipher == "Affine":
            return method(
                text,
                cls._int_key(key_values, 0, "m"),
                cls._int_key(key_values, 1, "k"),
            )
        if cipher == "DiffieHellman":
            p = cls._bounded_int_key(key_values, 0, "p")
            return method(
                text,
                p,
                cls._int_key(key_values, 1, "g"),
                cls._int_key(key_values, 2, "a"),
                cls._int_key(key_values, 3, "b"),
                lang,
            )
        if cipher == "RSA":
            p = cls._bounded_int_key(key_values, 0, "p")
            q = cls._bounded_int_key(key_values, 1, "q")
            return method(
                text,
                p,
                q,
                cls._int_key(key_values, 2, "e"),
                lang,
            )

        # Binary block ciphers intentionally ignore surrounding spaces.
        return method(text.strip().replace(" ", ""), cls._key(key_values, 0, cipher))

    @staticmethod
    def _prefix(cipher):
        return {"DiffieHellman": "dh"}.get(cipher, cipher.lower())

    @staticmethod
    def _key(keys, index, name):
        try:
            value = keys[index]
        except IndexError:
            raise ValueError(f"Missing key: {name}") from None
        return str(value).strip()

    @classmethod
    def _int_key(cls, keys, index, name):
        value = cls._key(keys, index, name)
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Key {name} must be an integer") from None

    @classmethod
    def _bounded_int_key(cls, keys, index, name):
        value = cls._int_key(keys, index, name)
        if value > cls.MAX_PRIME:
            raise ValueError(f"Key {name} is too large for the educational mode (maximum {cls.MAX_PRIME})")
        return value
