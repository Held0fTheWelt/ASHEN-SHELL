from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "architecture-assurance.yml"


def test_ci_renders_and_publishes_checksum_pinned_uml_previews() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    version = re.search(r'PLANTUML_VERSION:\s*"(?P<value>[^"]+)"', text)
    checksum = re.search(r'PLANTUML_SHA256:\s*"(?P<value>[0-9a-f]+)"', text)
    assert version is not None
    assert checksum is not None
    assert len(checksum.group("value")) == 64

    assert "actions/setup-java@v4" in text
    assert (
        "plantuml/releases/download/v${PLANTUML_VERSION}/"
        "plantuml-${PLANTUML_VERSION}.jar"
    ) in text
    assert "sha256sum --check --strict" in text
    assert "find UML -type f -name '*.puml'" in text
    assert "-failfast2 -tsvg" in text
    assert 'test "${source_count}" -eq "${preview_count}"' in text
    assert "SHA256SUMS" in text
    assert "RENDERER.txt" in text
    assert "name: better-tomorrow-uml-previews" in text
    assert (
        "reports/architecture/uml-previews/**/*.svg"
    ) in text
