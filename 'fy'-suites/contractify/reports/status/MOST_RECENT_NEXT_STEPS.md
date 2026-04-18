# contractify — Most-Recent-Next-Steps

This page uses simple language. It should help you understand the latest result and what to do next.

## Current status

- suite: `contractify`
- command: `inspect`
- ok: `true`
- latest_run_id: `contractify-7ba2a2aea211`
- latest_run_mode: `consolidate`
- latest_run_status: `ok`

## Plain summary

contractify is ready for inspection. Read the latest summary first and then only open detailed artifacts where you still need proof.

## Most-Recent-Next-Steps

- Read the summary first, then open the linked artifacts only where you still need detail.
- Use the strongest cross-suite signal as a second opinion before acting in isolation.

## Key signals

- finding_count: `0`
- doc_count: `0`
- track_count: `0`
- template_count: `0`
- drift_count: `0`
- local_spike_count: `0`
- evidence_confidence: ``
- signal_count: `5`

## Cross-suite signals

- `usabilify`: Usabilify evaluated UI and UX surfaces, connected available UI contracts, and highlighted the next usability steps in plain language.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.
- `testify`: Compared testify-e6fc1d6c0370 with testify-17653c3cfc42. Focus first on changed artifacts, review-state changes, and any target or mode differences.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.
- `templatify`: No summary available.
  - next: Validate the generated template previews before applying them to a target repo.
- `securify`: Securify found security follow-up work: no discoverable security documentation, secret-related ignore rules are missing. Start with the most direct exposure and the missing guidance surfaces.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.
- `documentify`: Documentify generated the current documentation tracks and status pages.
  - next: Read the newly generated documentation and decide which tracks should be exported outward.
  - next: Open the generated output directory and review the new files in simple language first.

## Governance

The suite is usable, but there are warnings you should look at soon.

- missing_optional:docs

## Warnings

- missing_optional:docs
