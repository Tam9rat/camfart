"""Tests for the auth service (no DB required)."""
import bcrypt
from app.services.auth import hash_password


def test_hash_password_is_valid_bcrypt() -> None:
    plain = "my-secret-password"
    hashed = hash_password(plain)
    assert hashed.startswith("$2b$")
    assert bcrypt.checkpw(plain.encode(), hashed.encode())


def test_hash_password_different_salts() -> None:
    h1 = hash_password("password")
    h2 = hash_password("password")
    assert h1 != h2  # bcrypt generates a new salt each time


def test_hash_password_wrong_password_fails() -> None:
    hashed = hash_password("correct")
    assert not bcrypt.checkpw(b"wrong", hashed.encode())
