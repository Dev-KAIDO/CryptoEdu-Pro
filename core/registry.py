"""Central algorithm metadata registry for CryptoEdu Pro.

Adding a new educational algorithm should start here.  The registry contains
only declarative metadata; implementations remain in :mod:`core.algorithms`.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal


FieldKind = Literal["text", "int"]


@dataclass(frozen=True)
class KeyFieldSpec:
    """Definition of one visible key input."""

    name: str
    label_key: str
    kind: FieldKind = "text"
    default: str = ""
    width: int = 100
    placeholder: str = ""
    note: str = ""
    bounded: bool = False


@dataclass(frozen=True)
class AlgorithmSpec:
    """Declarative contract shared by service and UI layers."""

    name: str
    method_prefix: str
    key_fields: tuple[KeyFieldSpec, ...]
    category: str
    text_limit: int = 100_000
    normalize_binary: bool = False
    pass_language: bool = False
    quick_text: str = "HELLO WORLD"

    @property
    def operations(self) -> tuple[str, str]:
        return ("encrypt", "decrypt")


_ALGORITHMS = (
    AlgorithmSpec(
        "Caesar", "caesar", (KeyFieldSpec("key", "key", "int", "3", 100, note="(1-25)"),), "classical"
    ),
    AlgorithmSpec(
        "Affine",
        "affine",
        (
            KeyFieldSpec("m", "key_m", "int", "7", 80),
            KeyFieldSpec("k", "key_k", "int", "10", 80),
        ),
        "classical",
    ),
    AlgorithmSpec(
        "Vigenere", "vigenere", (KeyFieldSpec("key", "key", default="KEY", width=180),), "classical"
    ),
    AlgorithmSpec(
        "Playfair", "playfair", (KeyFieldSpec("key", "key", default="SECRET", width=180),), "classical"
    ),
    AlgorithmSpec(
        "Hill",
        "hill",
        (KeyFieldSpec("key", "key", default="HILL", width=200, placeholder="HILL أو 3,2,5,7", note="(4 أحرف أو 4 أرقام)"),),
        "classical",
    ),
    AlgorithmSpec(
        "DiffieHellman",
        "dh",
        (
            KeyFieldSpec("p", "key_p", "int", "23", 50, bounded=True),
            KeyFieldSpec("g", "key_g", "int", "5", 50),
            KeyFieldSpec("a", "key_a", "int", "6", 50),
            KeyFieldSpec("b", "key_b", "int", "15", 50),
        ),
        "public_key",
        pass_language=True,
        quick_text="Diffie-Hellman Key Exchange",
    ),
    AlgorithmSpec(
        "RSA",
        "rsa",
        (
            KeyFieldSpec("p", "key_p", "int", "23", 60, bounded=True),
            KeyFieldSpec("q", "key_q", "int", "113", 60, bounded=True),
            KeyFieldSpec("e", "key_e", "int", "207", 60),
        ),
        "public_key",
        text_limit=1_000,
        pass_language=True,
        quick_text="mohammed",
    ),
    AlgorithmSpec(
        "SDES",
        "sdes",
        (KeyFieldSpec("key", "key_binary_key", default="1010110011", width=160, placeholder="1010110011", note="(10 بت ثنائي)"),),
        "block",
        normalize_binary=True,
        quick_text="10101101",
    ),
    AlgorithmSpec(
        "DES",
        "des",
        (
            KeyFieldSpec(
                "key",
                "key_des_key",
                default="0001001100110100010101110111100110011011101111001101111111110001",
                width=300,
                placeholder="0001001100110100010101110111100110011011101111001101111111110001",
                note="(64 بت ثنائي / 56 فعال)",
            ),
        ),
        "block",
        normalize_binary=True,
        quick_text="0000000100100011010001010110011110001001101010111100110111101111",
    ),
)

REGISTRY = MappingProxyType({spec.name: spec for spec in _ALGORITHMS})


def get_algorithm(name: str) -> AlgorithmSpec:
    """Return metadata for ``name`` or raise a clear error."""

    try:
        return REGISTRY[name]
    except KeyError:
        raise ValueError(f"Cipher not implemented: {name}") from None


def algorithm_names() -> tuple[str, ...]:
    """Return names in the stable UI order."""

    return tuple(REGISTRY)


def key_defaults(name: str) -> tuple[str, ...]:
    return tuple(field.default for field in get_algorithm(name).key_fields)
