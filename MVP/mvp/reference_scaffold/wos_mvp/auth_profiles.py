from __future__ import annotations
from enum import Enum

class RuntimeProfile(str, Enum):
    LOCAL_DEV = "local_dev"
    TEST_INJECTED = "test_injected"
    PROD_HARDENED = "prod_hardened"


def internal_auth_is_valid(profile: RuntimeProfile, internal_key: str | None) -> bool:
    if profile in {RuntimeProfile.PROD_HARDENED}:
        return bool(internal_key)
    return True


def authority_defaults_allowed(profile: RuntimeProfile) -> bool:
    return profile in {RuntimeProfile.LOCAL_DEV, RuntimeProfile.TEST_INJECTED}
