# Outgoing package manifest

| Field | Value |
|-------|-------|
| package_name | g9b_external_evaluator_outgoing_g9_level_a_fullsix_20260410 |
| source_audit_run_id | g9_level_a_fullsix_20260410 |
| assembly_timestamp_utc | 2026-04-09T01:18:38Z |

## PDF policy

The GoC script PDF is **included** under `optional_grounding/` for this handoff per maintainer directive (test/training context). This manifest does **not** assert licensing or production distribution rights.

## Optional witness files

**Excluded by default:** `run_metadata.json`, `pytest_g9_roadmap_bundle.txt` (see `documents/06_PACKAGING_AND_ASSEMBLY.md`). No `optional_witness/` directory in this package.

## Evaluator A and contamination exclusions (default blind package)

The following were **not** copied into this outgoing package (preserve blind scoring; no Evaluator A artifacts shipped by default):

- `g9_experience_score_matrix.json` (Evaluator A)
- `g9_experience_score_matrix_evaluator_b.json` (prior B / filled matrix)
- `g9b_raw_score_sheet.json`, `g9b_raw_score_sheet_evaluator_b.json`
- `g9b_score_delta_record.json`
- `g9b_evaluator_record.json`, `g9b_level_b_attempt_record.json`, `g9b_evaluator_b_declaration.json`
- Internal readiness / independence markdown notes under the evidence directory
- `run_metadata.json`, `pytest_g9_roadmap_bundle.txt` (technical witness)
- Reconciliation artifacts, validator outputs (`g9_threshold_validator_*`), audit markdown baselines not intended for external scoring

**Explicit:** No scores, deltas, or G9/G9B/G10 closure status were generated or modified by this assembly task.

## Included files (byte-identical copies; SHA-256 of delivered file)

| Relative source path (repo root) | Relative outgoing path (package root) | SHA-256 |
|----------------------------------|----------------------------------------|---------|
| `docs/g9_evaluator_b_external_package/README.md` | `README.md` | `d76bc692bd3ac85eee1173aa39b55bcced08f8f69415239ed327257fe9fa5718` |
| `docs/g9_evaluator_b_external_package/documents/01_EVALUATOR_B_HANDOUT.md` | `documents/01_EVALUATOR_B_HANDOUT.md` | `6d42e7c6b8678516e29a1741561ccae43a962a04c4895b504cfc292b408989d3` |
| `docs/g9_evaluator_b_external_package/documents/02_SCORING_INSTRUCTIONS_CRITERIA.md` | `documents/02_SCORING_INSTRUCTIONS_CRITERIA.md` | `6724fa03579cf9b215059c798bf56bfeb4e58ad28c9ecdb446d4508d25a51cb6` |
| `docs/g9_evaluator_b_external_package/documents/03_FROZEN_SOURCE_MANIFEST.md` | `documents/03_FROZEN_SOURCE_MANIFEST.md` | `c0bb4818f438d2ba68ec8cd80720809fd0525d97570226b93ee04cb73f786e88` |
| `docs/g9_evaluator_b_external_package/documents/04_BLINDNESS_CONTAMINATION_CHECKLIST.md` | `documents/04_BLINDNESS_CONTAMINATION_CHECKLIST.md` | `8ab2d327bf177a55ce3828af1f34f0a3d0ba05b1c456b5e041785d7aae891d0b` |
| `docs/g9_evaluator_b_external_package/documents/05_SUBMISSION_CHECKLIST.md` | `documents/05_SUBMISSION_CHECKLIST.md` | `b2ed3b7af0527f5d9c2649cb1936f294254bfe5234ecc357f353ffed6a80fecb` |
| `docs/g9_evaluator_b_external_package/documents/06_PACKAGING_AND_ASSEMBLY.md` | `documents/06_PACKAGING_AND_ASSEMBLY.md` | `1fe3e51b9c86841a4369f7e18785963e698f3cf44455bdb7b8c3583e57d7e3ff` |
| `docs/g9_evaluator_b_external_package/documents/07_FILENAME_AND_RETURN_LAYOUT.md` | `documents/07_FILENAME_AND_RETURN_LAYOUT.md` | `690846cc1ce37c1748b7f8c6417baaea46fb6cad1c78675b60e9b19f18b43187` |
| `docs/g9_evaluator_b_external_package/documents/INTERNAL_PACKAGE_OWNER_INSTRUCTIONS.md` | `documents/INTERNAL_PACKAGE_OWNER_INSTRUCTIONS.md` | `42eeb91ffeb00904161c0558c5d809f21f1d6b22ca0fb1704b34fdc72f4baa60` |
| `docs/g9_evaluator_b_external_package/templates/g9_experience_score_matrix_evaluator_b.json` | `templates/g9_experience_score_matrix_evaluator_b.json` | `8f4d150e8004e96c54979cd19fb9d638789c42b52bb57c370f8e68765ef5a9a3` |
| `docs/g9_evaluator_b_external_package/templates/g9b_evaluator_b_declaration.json` | `templates/g9b_evaluator_b_declaration.json` | `f22ce065a035e82c7e8d892f8d76827a2712a6becce3d4ee60ed130bfd780a8b` |
| `docs/g9_evaluator_b_external_package/templates/g9b_raw_score_sheet_evaluator_b.json` | `templates/g9b_raw_score_sheet_evaluator_b.json` | `082ab4f2289ff74a73d4ba5f50a21b9a67768777751025d683bc896046932f3c` |
| `tests/reports/evidence/g9_level_a_fullsix_20260410/scenario_goc_roadmap_s1_direct_provocation.json` | `frozen_scenarios/scenario_goc_roadmap_s1_direct_provocation.json` | `3ce561d99cfc5804d3c4fcbca3784da97249aeae6f4d4332312512876b11f2cb` |
| `tests/reports/evidence/g9_level_a_fullsix_20260410/scenario_goc_roadmap_s2_deflection_brevity.json` | `frozen_scenarios/scenario_goc_roadmap_s2_deflection_brevity.json` | `0bcb82ffb500417bc05e74cf1a623332bcd217705ce86c5f68001dfef1e7a1ec` |
| `tests/reports/evidence/g9_level_a_fullsix_20260410/scenario_goc_roadmap_s3_pressure_escalation.json` | `frozen_scenarios/scenario_goc_roadmap_s3_pressure_escalation.json` | `38b0916c19de54d66fea83e37c0ebcaff99b5f75aa880812c224f6223f294ad6` |
| `tests/reports/evidence/g9_level_a_fullsix_20260410/scenario_goc_roadmap_s4_misinterpretation_correction.json` | `frozen_scenarios/scenario_goc_roadmap_s4_misinterpretation_correction.json` | `d98b97d288cf3265ddb4534102d792a21d2682959c85def88da02427f2f81261` |
| `tests/reports/evidence/g9_level_a_fullsix_20260410/scenario_goc_roadmap_s5_primary_failure_fallback.json` | `frozen_scenarios/scenario_goc_roadmap_s5_primary_failure_fallback.json` | `0dd46ab60145812b53bd0fc5b8401f2578b2ca8d7327e457248be62f05e7aef6` |
| `tests/reports/evidence/g9_level_a_fullsix_20260410/scenario_goc_roadmap_s6_retrieval_heavy.json` | `frozen_scenarios/scenario_goc_roadmap_s6_retrieval_heavy.json` | `be32860176cf9af2d0881be06f44d3b8600c7b95eac3dc457526eaa65cd7d70b` |
| `resources/Script-God-Of-Carnage-Script-by-Yazmina-Reza.pdf` | `optional_grounding/Script-God-Of-Carnage-Script-by-Yazmina-Reza.pdf` | `3aa5bfaa37bdeea5f6fde2af003c30e4fedfb01ece86082d16792606e1726d2b` |
## Assembly-generated files

The SHA-256 for `PACKAGE_MANIFEST.md` is **SHA-256(prefix)** where *prefix* is the UTF-8 content from the start of this file through the end of the Included files table (exclusive of this section), so the hash is not circular.

| Relative source path | Relative outgoing path | SHA-256 |
|----------------------|------------------------|---------|
| _(generated during assembly)_ | `PACKAGE_MANIFEST.md` | `41012d60c33f10a50e6c85ba2d26892241952e4f9019698886782f282ab0c697` |
| _(generated during assembly)_ | `ASSEMBLY_NOTES.txt` | `7270bb87ed91f6b93a32fb6efa34b884058d98a4e112635d8c191561e3136f5b` |
