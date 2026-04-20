# 63 — Implementation Handoff Template

Use this template when the audit system hands a work field to a separate implementation AI.

## 1. Role
You are a senior implementation engineer working on World of Shadows.
You must implement the requested field.
You must not redesign the product.

## 2. Target work field
- Field name:
- Why this field is next:
- Current maturity:
- Required uplift:

## 3. Allowed ownership surfaces
- Repository/package paths:
- Files expected to change:
- Files that must remain untouched unless necessary:

## 4. Mandatory outcomes
- behavioral outcomes
- runtime outcomes
- validation outcomes
- documentation outcomes

## 5. Non-negotiable constraints
- preserve authoritative world-engine law
- preserve player/operator separation
- do not replace committed truth with generated text
- do not add stubs where real implementation is required
- do not overclaim completeness

## 6. Evidence requirements
- tests to add or improve
- commands to run
- what to report as passed / failed / not run

## 7. Deliverables
- changed files
- validation output
- short implementation note
- explicit list of unresolved follow-ups

## 8. Audit return rule
Your output will be re-audited against this handoff.
Deliver only what can survive that re-audit honestly.
