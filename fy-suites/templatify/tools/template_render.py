from __future__ import annotations

def render_with_header(title: str, body: str) -> str:
    return f"# {title}\n\n{body.rstrip()}\n"
