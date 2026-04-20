from wos_mvp.payloads import make_player_reveal, make_operator_bundle, ordinary_player_payload_is_clean


def test_player_reveal_self_classifies():
    payload = make_player_reveal(transcript=[{"speaker": "gm", "text": "Opening"}], narration="Opening", turn_number=0).as_dict()
    assert payload["schema_version"] == "v21"
    assert payload["path_class"] == "authoritative_player"
    assert payload["audience"] == "player"
    assert payload["truth_status"] == "committed"
    assert payload["payload_class"] == "player_reveal"


def test_operator_bundle_is_not_player_clean():
    bundle = make_operator_bundle(trace_id="tr-1", diagnostics={"ok": True}).as_dict()
    assert ordinary_player_payload_is_clean(bundle) is True
    mixed = {"operator_bundle": bundle}
    assert ordinary_player_payload_is_clean(mixed) is False
