"""Тесты Fernet round-trip и ротации ключа (Phase 2).

Проверяем:
- encrypt → decrypt возвращает исходную строку
- Кириллица и unicode корректно шифруются
- Ротация: зашифрованное старым ключом расшифровывается с MultiFernet(new+old)
- InvalidToken при неверном ключе
"""

from __future__ import annotations

import importlib

import pytest
from cryptography.fernet import Fernet, InvalidToken, MultiFernet


@pytest.fixture()
def fernet_key() -> str:
    return Fernet.generate_key().decode()


@pytest.fixture()
def prev_key() -> str:
    return Fernet.generate_key().decode()


def _make_crypto(
    key: str, prev_key: str | None = None
) -> tuple[
    type[bytes],
    type[str],
]:
    """Создать пару (encrypt, decrypt) с заданными ключами, минуя settings."""
    keys = [Fernet(key.encode())]
    if prev_key:
        keys.append(Fernet(prev_key.encode()))
    f = MultiFernet(keys)

    def encrypt(value: str) -> bytes:
        return f.encrypt(value.encode("utf-8"))

    def decrypt(token: bytes) -> str:
        return f.decrypt(token).decode("utf-8")

    return encrypt, decrypt  # type: ignore[return-value]


def test_roundtrip_ascii(fernet_key: str) -> None:
    enc, dec = _make_crypto(fernet_key)
    assert dec(enc("Stabby")) == "Stabby"


def test_roundtrip_unicode(fernet_key: str) -> None:
    enc, dec = _make_crypto(fernet_key)
    value = "Колдун-Ревенант"
    assert dec(enc(value)) == value


def test_roundtrip_special_chars(fernet_key: str) -> None:
    enc, dec = _make_crypto(fernet_key)
    assert dec(enc("Realm Of Shadows")) == "Realm Of Shadows"


def test_rotation_old_key_decryptable(fernet_key: str, prev_key: str) -> None:
    """Шифруем старым ключом → расшифровываем с MultiFernet(new+old)."""
    token = Fernet(prev_key.encode()).encrypt(b"Gorefiend")
    _, dec = _make_crypto(fernet_key, prev_key=prev_key)
    assert dec(token) == "Gorefiend"


def test_wrong_key_raises(fernet_key: str) -> None:
    wrong_key = Fernet.generate_key().decode()
    enc, _ = _make_crypto(fernet_key)
    _, dec_wrong = _make_crypto(wrong_key)
    token = enc("secret")
    with pytest.raises(InvalidToken):
        dec_wrong(token)


def test_encrypt_field_integration(
    monkeypatch: pytest.MonkeyPatch,
    fernet_key: str,
) -> None:
    """Интеграционный тест encrypt_field / decrypt_field через settings."""
    import arena_coach.shared.settings as _sm
    from arena_coach.shared.settings import Settings

    cfg = Settings(
        arena_coach_fernet_key=fernet_key,
        discord_bot_token="test",
        discord_guild_id=0,
    )
    monkeypatch.setattr(_sm, "settings", cfg)

    import arena_coach.access.crypto as _crypto

    importlib.reload(_crypto)

    token = _crypto.encrypt_field("TestChar")
    assert _crypto.decrypt_field(token) == "TestChar"
