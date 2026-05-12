"""Fernet-шифрование игровых ников / реалмов в whitelist'е.

Phase 2 skeleton. См. docs/phase-0-design.md §5.1 — ARENA_COACH_FERNET_KEY,
ротация через ARENA_COACH_FERNET_PREV_KEY.
"""

from __future__ import annotations


def encrypt_field(value: str) -> bytes:
    """TODO(Phase 2): cryptography.fernet.Fernet(key).encrypt(value.encode())."""
    raise NotImplementedError("Phase 2")


def decrypt_field(token: bytes) -> str:
    """TODO(Phase 2): MultiFernet([new_key, prev_key]).decrypt(token)."""
    raise NotImplementedError("Phase 2")
