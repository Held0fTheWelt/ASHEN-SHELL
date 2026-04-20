from wos_mvp.player_surface import make_clean_player_surface, validate_player_surface_payload


def test_clean_player_surface_validates():
    payload = make_clean_player_surface(transcript=[{"speaker": "gm", "text": "Hello"}], gm_narration="Hello", turn_number=0)
    ok, errors = validate_player_surface_payload(payload)
    assert ok is True
    assert errors == []


def test_player_surface_rejects_operator_leak():
    payload = make_clean_player_surface(transcript=[], gm_narration="...", turn_number=1)
    payload["operator_bundle"] = {"trace_id": "tr-1"}
    ok, errors = validate_player_surface_payload(payload)
    assert ok is False
    assert "forbidden player keys present" in errors[0]
