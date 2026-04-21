import json
from pathlib import Path
from wos_mvp.incidents import load_story_session_or_incident


def test_missing_story_session_becomes_incident(tmp_path: Path):
    data, incident = load_story_session_or_incident(tmp_path / "missing.json")
    assert data is None
    assert incident is not None
    assert incident.incident_code == "SESSION_MISSING"


def test_corrupt_story_session_becomes_incident(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    data, incident = load_story_session_or_incident(p)
    assert data is None
    assert incident is not None
    assert incident.incident_code == "SESSION_CORRUPT"
