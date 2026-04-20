from wos_mvp.auth_profiles import RuntimeProfile, authority_defaults_allowed, internal_auth_is_valid


def test_prod_hardened_requires_internal_key():
    assert internal_auth_is_valid(RuntimeProfile.PROD_HARDENED, None) is False
    assert internal_auth_is_valid(RuntimeProfile.PROD_HARDENED, "secret") is True


def test_defaults_allowed_only_in_non_prod_profiles():
    assert authority_defaults_allowed(RuntimeProfile.LOCAL_DEV) is True
    assert authority_defaults_allowed(RuntimeProfile.TEST_INJECTED) is True
    assert authority_defaults_allowed(RuntimeProfile.PROD_HARDENED) is False
