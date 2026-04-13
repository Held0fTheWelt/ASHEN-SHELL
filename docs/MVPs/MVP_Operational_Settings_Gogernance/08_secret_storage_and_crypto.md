# 08 Secret Storage and Crypto

## Security requirement

Provider credentials and similar operational secrets must be:
- backend-held
- encrypted at rest
- write-only from the UI
- unavailable in raw form through normal read APIs
- auditable when changed
- rotatable

## Recommended model: envelope encryption

### Secret record flow
1. generate a per-secret DEK
2. encrypt the secret value with the DEK
3. encrypt the DEK with a KEK
4. store:
   - encrypted secret
   - encrypted DEK
   - metadata
5. store the KEK outside the database

## Recommended implementation defaults

These defaults should be treated as the MVP baseline unless a stricter platform-specific control exists.

- **DEK algorithm:** AES-256-GCM
- **KEK algorithm:** AES-256-GCM or external KMS-managed symmetric key equivalent
- **DEK size:** 32 bytes
- **Nonce size:** 12 bytes for AES-GCM
- **Fingerprint algorithm:** SHA-256 over a normalized secret payload or provider-specific canonical secret string
- **KEK environment variable name:** `SECRETS_KEK`
- **KEK format:** base64-encoded 256-bit key when deployment-secret mode is used

## Example implementation sketch

```python
from __future__ import annotations

import base64
import hashlib
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_dek() -> bytes:
    return secrets.token_bytes(32)


def encrypt_with_aes_gcm(key: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
    nonce = secrets.token_bytes(12)
    aes = AESGCM(key)
    ciphertext = aes.encrypt(nonce, plaintext, None)
    return nonce, ciphertext


def decrypt_with_aes_gcm(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    aes = AESGCM(key)
    return aes.decrypt(nonce, ciphertext, None)


def fingerprint_secret(secret_value: str) -> str:
    digest = hashlib.sha256(secret_value.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"
```

## KEK location options

### Preferred
external KMS / Vault

### Strong MVP option
deployment secret not stored in app DB

### Not acceptable
KEK stored in same DB row as the encrypted secret

## Storage modes

### `same_db_encrypted`
Use primary backend DB, but separate secret service and tables.

### `separate_secret_db_encrypted`
Store secret rows in a dedicated secret DB.
Recommended if operational complexity is acceptable.

### `external_secret_manager`
Use external secret manager and store references.

## Rotation policy

### DEK rotation
- generate a fresh DEK per write or re-encrypt operation
- old DEKs do not need to remain active after the secret is re-encrypted
- the secret record should update `rotated_at` and append an audit event

### KEK rotation
KEK rotation must be an explicit operator/deployment procedure.
Minimum supported process:
1. load current KEK and new KEK
2. decrypt each encrypted DEK with current KEK
3. re-encrypt each DEK with new KEK
4. update stored encrypted DEKs atomically per batch
5. verify decryptability using the new KEK before finalizing rotation
6. record a `kek_rotation_completed` audit event

### Rotation safety requirements
- credential rotation must not re-render the old raw secret
- the system must support post-rotation health checks
- rotation failure must leave the previous decryptable state intact
- concurrent rotations on the same provider credential must be blocked

## UI handling rules

- secret values may be submitted
- secret values must never be re-shown
- masked state may be shown
- credential configured status may be shown
- test connection may be shown
- rotation events may be shown

## API handling rules

- credential write endpoints are write-only
- GET endpoints return configuration metadata only
- logs must redact secrets
- error messages must not leak secrets
- audit trail must record rotation/change without exposing secret value

## Recovery and trust-anchor note

Bootstrap/trust-anchor configuration must make it obvious how secret storage is anchored and how recovery works.
If recovery requires deployment-level intervention, the system must say so clearly.

## Recovery minimums

- the operator must be told whether recovery requires access to `SECRETS_KEK`, an external KMS, or a secret DB connection
- the bootstrap recovery screen must show the storage mode in use
- production runbooks must include KEK loss and credential recovery steps
