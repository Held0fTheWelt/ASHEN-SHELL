"""Entrypoint for running the integrated MVP API."""

from __future__ import annotations

import uvicorn

from .config import get_settings


def main() -> None:
    """Run the API server."""

    settings = get_settings()
    uvicorn.run("wos_mvp.app:app", host=settings.bind_host, port=settings.bind_port, reload=False)


if __name__ == "__main__":
    main()
