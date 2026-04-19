# Docify Documentation Policy

Docify is adopted as the package's code-adjacent documentation governance layer.

## Role

Docify does not prove runtime correctness.
It helps ensure that important code-adjacent explanations do not lag too far behind real changes.

## Required uses

After each accepted implementation wave, Docify should be used to review:

- changed Python boundaries,
- public runtime seams,
- contract-heavy modules,
- service entry points,
- validation and recovery surfaces,
- and any player-visible or operator-visible behavior that was modified.

## MVP value

The main value of Docify in this package is not prose volume.
It is disciplined boundary explanation.

That matters because World of Shadows depends on keeping distinctions clear between:

- truth and projection,
- runtime and admin,
- player route and operator route,
- committed output and internal diagnostics,
- normative policy and observed implementation.
