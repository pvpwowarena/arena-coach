"""Тесты Fernet round-trip и ротации ключа.

Проверяем:
- encrypt → decrypt возвращает исходную строку
- Кирилица и unicode корректно шифруются
- Ротация: зашифрованное старым ключом расшифровывается с новым + старым
- InvalidToken при неверном ключе
"""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet, InvalidToken


@pytest.fixture()
def fernet_key() -> str:
    return Fernet.generate_key().decode()


@pytest.fixture()
def prev_key() -> str:
    return Fernet.generate_key().decode()


def _make_crypto(key: str, prev_key: str | None = None):
    """Создать пару (encrypt_field, decrypt_field) с заданными ключами."""
    from cryptography.fernet import MultiFernet

    keys = [Fernet(key.encode())]
    if prev_key:
        keys.append(Fernet(prev_key.encode()))
    f = MultiFernet(keys)

    def encrypt(value: str) -> bytes:
        return f.encrypt(value.encode("utf-8"))

    def decrypt(token: bytes) -> str:
        return f.decrypt(token).decode("utf-8")

    return encrypt, decrypt


def test_roundtrip_ascii(fernet_key: str) -> None:
    enc, dec = _make_crypto(fernet_key)
    assert dec(enc("Stabby")) == "Stabby"


def test_roundtrip_unicode(fernet_key: str) -> None:
    enc, dec = _make_crypto(fernet_key)
    value = "Колдун-Ревенант"
    assert dec(enc(value)) == value


def test_roundtrip_special_chars(fernet_key: str) -> None:
    enc, dec = _make_crypto(fernet_key)
    value = "Realm Of Shadows"
    assert dec(enc(value)) == value


def test_rotation_old_key_decryptable(fernet_key: str, prev_key: str) -> None:
    """Сообщение зашифрованное СТАРЫМ ключом расшифровывается с MultiFernet(new+old)."""
    # Шифруем только старым ключом
    old_fernet = Fernet(prev_key.encode())
    token = old_fernet.encrypt(b"Gorefiend")

    # Расшифровываем с new + old
    _, dec = _make_crypto(fernet_key, prev_key=prev_key)
    assert dec(token) == "Gorefiend"


def test_wrong_key_raises(fernet_key: str) -> None:
    """Неверный ключ должен бросать InvalidToken."""
    wrong_key = Fernet.generate_key().decode()
    enc, _ = _make_crypto(fernet_key)
    _, dec_wrong = _make_crypto(wrong_key)

    token = enc("secret")
    with pytest.raises(InvalidToken):
        dec_wrong(token)


def test_encrypt_field_integration(monkeypatch: pytest.MonkeyPatch, fernet_key: str) -> None:
    """Интеграционный тест: encrypt_field / decrypt_field через settings."""
    import arena_coach.shared.settings as _settings_module
    from arena_coach.shared.settings import Settings

    cfg = Settings(
        arena_coach_fernet_key=fernet_key,
        discord_bot_token="test",
        discord_guild_id=0,
    )
    monkeypatch.setattr(_settings_module, "settings", cfg)

    from arena_coach.access import crypto as _crypto

    # Reload чтобы _build_fernet() взял новые settings
    import importlib

    importlib.reload(_crypto)

    token = _crypto.encrypt_field("TestChar")
    result = _crypto.decrypt_field(token)
    assert result == "TestChar"
