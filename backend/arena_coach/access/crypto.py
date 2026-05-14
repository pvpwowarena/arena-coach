"""Fernet-шифрование игровых ников / реалмов в whitelist'е.

Ключ: ARENA_COACH_FERNET_KEY (обязателен при запуске).
Ротация: ARENA_COACH_FERNET_PREV_KEY (опционально — для дешифровки старых записей).
MultiFernet пробует ключи по очереди: сначала новый (для encrypt), затем старый (для decrypt).
"""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken, MultiFernet


def _build_fernet() -> MultiFernet:
    """Собрать MultiFernet из текущего + предыдущего ключей (если есть)."""
    # Импортируем здесь чтобы избежать circular-импорта при module load
    from arena_coach.shared.settings import settings

    key = settings.arena_coach_fernet_key
    if not key:
        raise RuntimeError(
            "ARENA_COACH_FERNET_KEY не задан. "
            "Сгенерируй: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )

    keys: list[Fernet] = [Fernet(key.encode())]
    if settings.arena_coach_fernet_prev_key:
        keys.append(Fernet(settings.arena_coach_fernet_prev_key.encode()))

    return MultiFernet(keys)


def encrypt_field(value: str) -> bytes:
    """Зашифровать строку (character или realm). Возвращает Fernet-токен (bytes)."""
    return _build_fernet().encrypt(value.encode("utf-8"))


def decrypt_field(token: bytes) -> str:
    """Расшифровать Fernet-токен. Бросает InvalidToken при неверном ключе."""
    try:
        return _build_fernet().decrypt(token).decode("utf-8")
    except InvalidToken as exc:
        raise InvalidToken(
            "Не удалось расшифровать поле. Проверь ARENA_COACH_FERNET_KEY / ARENA_COACH_FERNET_PREV_KEY."
        ) from exc


__all__ = ["decrypt_field", "encrypt_field"]
