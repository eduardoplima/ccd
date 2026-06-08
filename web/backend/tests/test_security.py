from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from freezegun import freeze_time
from jose import jwt

from app.auth import security
from app.auth.security import (
    BCRYPT_MAX_BYTES,
    InvalidTokenError,
    PasswordTooLongError,
    decode_access_token,
    encode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.config import get_settings


def test_hash_password_round_trip() -> None:
    h = hash_password("senha-secreta")
    assert verify_password("senha-secreta", h)
    assert not verify_password("outra", h)


def test_hash_password_rejects_above_72_bytes() -> None:
    with pytest.raises(PasswordTooLongError):
        hash_password("a" * (BCRYPT_MAX_BYTES + 1))


def test_verify_password_safe_against_long_input() -> None:
    h = hash_password("a" * BCRYPT_MAX_BYTES)
    assert not verify_password("a" * (BCRYPT_MAX_BYTES + 1), h)


def test_encode_decode_access_token() -> None:
    token, expires_in = encode_access_token(subject="42", papel="admin")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["papel"] == "admin"
    assert payload["type"] == "access"
    assert expires_in > 0


def test_decode_rejects_refresh_type_token() -> None:
    settings = get_settings()
    bogus = jwt.encode(
        {"sub": "1", "type": "refresh"}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    with pytest.raises(InvalidTokenError):
        decode_access_token(bogus)


def test_decode_rejects_wrong_signature() -> None:
    settings = get_settings()
    foreign = jwt.encode(
        {"sub": "1", "type": "access"}, "outra-chave", algorithm=settings.jwt_algorithm
    )
    with pytest.raises(InvalidTokenError):
        decode_access_token(foreign)


def test_decode_rejects_expired_token() -> None:
    with freeze_time("2026-05-06T12:00:00Z"):
        token, _ = encode_access_token(subject="1", papel="user")
    with freeze_time("2026-05-06T13:00:01Z"):
        with pytest.raises(InvalidTokenError):
            decode_access_token(token)


def test_refresh_token_hash_is_deterministic_sha256() -> None:
    raw = generate_refresh_token()
    assert hash_refresh_token(raw) == hash_refresh_token(raw)
    assert len(hash_refresh_token(raw)) == 64
    assert raw != hash_refresh_token(raw)
