from __future__ import annotations

def render_standard_report(title: str, body: str) -> str:
    return f"# {title}\n\n{body.rstrip()}\n"
