# FY Manifest and Bootstrap

This package includes a root `fy-manifest.yaml` so the FY suites can resolve the package as a project root.

## Why the manifest matters

Several FY tools are more reliable when they can discover the repository root from an explicit manifest instead of falling back to ad hoc ancestor traversal.

This is especially important when the package is moved, copied, or audited in archive form.

## Current v24 bootstrap decision

The manifest configures:

- the Despaghettify hub path,
- the Docify default roots,
- and the package identity as an integrated current-state bundle.

Contractify is intentionally kept conservative here.
The package does not fabricate missing canonical API anchors merely to satisfy tooling.
If a stronger OpenAPI anchor is created later, the manifest should be expanded rather than invented in advance.

## Practical note

For archive-form validation, prefer `python scripts/run_fy_governance_cycle.py` over calling the FY tools ad hoc. The wrapper uses explicit paths for Despaghettify setup validation and is the most reliable baseline entry point for this package.
