from __future__ import annotations

from fy_platform.ai.adapter_cli_helper import build_command_envelope


def test_command_envelope_v4_contains_contract_and_compatibility_fields():
    env = build_command_envelope('contractify', 'inspect', {'ok': True, 'summary': 'ok'})
    assert env.schema_version == 'fy.command-envelope.v4'
    assert env.contract_version == '1.0'
    assert env.compatibility_mode == 'autark-outbound'
