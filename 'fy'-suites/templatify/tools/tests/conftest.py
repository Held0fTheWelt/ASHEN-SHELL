from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture()
def fake_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "'fy'-suites").mkdir(parents=True, exist_ok=True)
    frontend = tmp_path / 'frontend' / 'templates'
    frontend.mkdir(parents=True, exist_ok=True)
    (frontend / 'base.html').write_text(
        '<html><head><title>{% block title %}World of Shadows{% endblock %}</title>{% block extra_head %}{% endblock %}</head>'
        '<body class="{% block body_class %}{% endblock %}">{% block site_header %}<nav>Default</nav>{% endblock %}'
        '{% block site_main %}{% block content %}{% endblock %}{% endblock %}{% block extra_scripts %}{% endblock %}</body></html>',
        encoding='utf-8',
    )
    (frontend / 'dashboard.html').write_text('{% extends "base.html" %}{% block content %}<h1>Dashboard</h1>{% endblock %}', encoding='utf-8')
    source = tmp_path / 'source-pack' / 'default'
    source.mkdir(parents=True, exist_ok=True)
    (source / 'shell.html').write_text(
        '<!doctype html><html><head><title>[[TITLE]]</title>[[EXTRA_HEAD]]</head><body class="[[BODY_CLASS]]">[[HEADER]]<main>[[CONTENT]]</main>[[EXTRA_SCRIPTS]]</body></html>',
        encoding='utf-8',
    )
    monkeypatch.setenv('WOS_TEMPLATIFY_REPO_ROOT', str(tmp_path))
    return tmp_path
