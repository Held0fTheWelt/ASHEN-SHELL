# Closure and proof

This repository makes bounded claims.

## What is proven

The repository keeps profile D as default, preserves Candidate E as opt-in, retains the Candidate E closure report, and keeps the self-hosting comparison artifacts and example outputs that show a material difference between D and E.

The repository also keeps the review-first and honesty constraints visible in both code and documentation.

## What is intentionally not claimed

This repository does not claim that Candidate E should replace D as the default.

This repository does not claim autonomous closure authority without review.

This repository does not claim that every historical report remains canonical.

## Proof artifact locations

The main proof locations are:

- `docs/platform/READINESS_CLOSURE_CANDIDATE_E_CLOSURE_REPORT.md`
- `docs/platform/READINESS_CLOSURE_CANDIDATE_E_CLOSURE_REPORT.json`
- `docs/platform/self_hosting/candidate_e_self_hosting_manifest.json`
- `docs/platform/self_hosting/candidate_e_d_vs_e_comparison.json`
- `docs/platform/examples/candidate_e/`
- `fy_platform/tests/test_candidate_e_profile.py`
- `fy_platform/tests/test_candidate_e_release_bundle.py`
- `fy_platform/tests/test_candidate_e_closure_report.py`

Historical reports can remain as secondary evidence under `docs/platform/`, but they are no longer the main way to understand the MVP.
