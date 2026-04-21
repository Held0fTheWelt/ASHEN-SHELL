# Release Notes — MVP v23 FY-Governed

## Summary

v23 is a governance-strengthening package release.

It does not claim that all runtime fields are now fully implemented.
It does claim that the package is better prepared for coherent continuation because the implementation path is now explicitly tied to the FY suites.

## Main changes

- moved from a mostly standalone MVP package to an integrated current-state repository package,
- retained the previous MVP as an explicit `mvp/` layer,
- added the FY suites as first-class package contents,
- added a root suite bootstrap manifest,
- added package-level validation artifacts,
- added package-level guidance for Contractify, Despaghettify, and Docify usage.

## Expected benefit

This package should make it easier to continue implementation without letting contracts, structure, and documentation drift apart as work proceeds.
