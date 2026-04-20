# Current repository state

The repository is organized around a cleaned suite baseline.

## What is present

The active root contains the live suite directories, platform code, platform documentation, requirements files, and canonical MVP documentation.

The platform documentation under `docs/platform/` remains the evidence and product-documentation area for release, readiness, and self-hosting artifacts.

The canonical MVP explanation now lives under `docs/MVPs/fy-suites-readiness-and-closure/`.

## What was removed from the active structure

The repository no longer uses imported MVP mirror trees as its canonical documentation structure.

The repository no longer keeps generated import bundles, cache directories, Python bytecode caches, or stale scratch state as part of the final release surface.

The old duplicated MVP import layout under `docs/MVPs/imports/` and `mvpify/imports/` is intentionally not part of the final repository state.

## Strategy truth

The active strategy file keeps profile D as the default.

Candidate E remains explicitly opt-in and is not silently enabled.
