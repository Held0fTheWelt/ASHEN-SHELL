# FY-Governed Implementation Protocol

This carried-forward FY-governed layer remains part of the v24 lean package and continues to provide a governed continuation protocol for implementation work.

The package now treats the `fy` suites as part of the implementation discipline:

- **Contractify** governs contract discovery, versioning, relation mapping, and drift finding.
- **Despaghettify** governs bounded structural workstreams, pre/post evidence, and anti-spaghetti execution discipline.
- **Docify** governs code-adjacent documentation hygiene and drift hints after implementation changes.

## Required order for meaningful continuation work

1. select the target work field,
2. identify the governing contracts and truth anchors,
3. map expected implementation and validation surfaces,
4. open a bounded structural workstream,
5. perform the implementation outside this governance layer,
6. run documentation and validation follow-up,
7. re-audit the result against both the prior contract map and the returned implementation.

## What this carried-forward layer changed compared to v22

v22 already documented the runtime target clearly.

That historical v23 layer adds an explicit anti-drift operating layer so that implementation work is less likely to:

- introduce silent contract divergence,
- modify the wrong repository surface,
- leave structural debt untracked,
- or let documentation and tests drift away from the new code.
