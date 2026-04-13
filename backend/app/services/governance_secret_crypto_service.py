"""Envelope encryption helpers for provider credentials."""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.governance.errors import governance_error


@dataclass(frozen=True)
class EncryptedSecretRecord:
    """Envelope encrypted secret payload for persistence."""

    encrypted_secret: bytes
    encrypted_dek: bytes
    secret_nonce: bytes
    dek_nonce: bytes
    secret_fingerprint: str
    dek_algorithm: str


def _load_kek() -> bytes:
    """Load KEK from `SECRETS_KEK` environment variable."""
    raw_value = (os.getenv("SECRETS_KEK") or "").strip()
    if not raw_value:
        raise governance_error(
            "bootstrap_secret_write_failed",
            "SECRETS_KEK is required for credential encryption.",
            500,
            {"env_var": "SECRETS_KEK"},
        )
    try:
        kek = base64.b64decode(raw_value)
    except Exception as exc:  # pragma: no cover - defensive
        raise governance_error(
            "bootstrap_secret_write_failed",
            "SECRETS_KEK is not valid base64.",
            500,
            {"error": str(exc)},
        ) from exc
    if len(kek) != 32:
        raise governance_error(
            "bootstrap_secret_write_failed",
            "SECRETS_KEK must decode to 32 bytes.",
            500,
            {"decoded_length": len(kek)},
        )
    return kek


def fingerprint_secret(secret_value: str) -> str:
    """Return stable SHA-256 fingerprint for secret metadata."""
    return f"sha256:{hashlib.sha256(secret_value.encode('utf-8')).hexdigest()}"


def encrypt_secret(secret_value: str) -> EncryptedSecretRecord:
    """Encrypt a provider secret using DEK/KEK envelope encryption."""
    if not secret_value.strip():
        raise governance_error(
            "provider_secret_rejected",
            "Secret value must not be empty.",
            400,
            {},
        )
    kek = _load_kek()
    dek = secrets.token_bytes(32)
    secret_nonce = secrets.token_bytes(12)
    dek_nonce = secrets.token_bytes(12)
    secret_cipher = AESGCM(dek)
    dek_cipher = AESGCM(kek)
    encrypted_secret = secret_cipher.encrypt(secret_nonce, secret_value.encode("utf-8"), None)
    encrypted_dek = dek_cipher.encrypt(dek_nonce, dek, None)
    return EncryptedSecretRecord(
        encrypted_secret=encrypted_secret,
        encrypted_dek=encrypted_dek,
        secret_nonce=secret_nonce,
        dek_nonce=dek_nonce,
        secret_fingerprint=fingerprint_secret(secret_value),
        dek_algorithm="AES-256-GCM",
    )


def decrypt_secret(*, encrypted_secret: bytes, encrypted_dek: bytes, secret_nonce: bytes, dek_nonce: bytes) -> str:
    """Decrypt secret for internal runtime use only."""
    kek = _load_kek()
    dek_cipher = AESGCM(kek)
    secret_cipher: AESGCM
    try:
        dek = dek_cipher.decrypt(dek_nonce, encrypted_dek, None)
        secret_cipher = AESGCM(dek)
        plaintext = secret_cipher.decrypt(secret_nonce, encrypted_secret, None)
    except Exception as exc:
        raise governance_error(
            "credential_encryption_failed",
            "Stored credential could not be decrypted.",
            500,
            {"error": str(exc)},
        ) from exc
    return plaintext.decode("utf-8")
