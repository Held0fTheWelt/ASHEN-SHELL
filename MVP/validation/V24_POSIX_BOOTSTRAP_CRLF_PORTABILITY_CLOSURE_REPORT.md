# V24 POSIX Bootstrap CRLF Portability Closure

## Summary

This narrow pass closes the proven package-local POSIX portability defect in the shipped bootstrap path.

The root cause was CRLF packaging of the shipped shell scripts:

- `setup-test-environment.sh`
- `scripts/install-ai-stack-test-env.sh`

Under Bash, the shipped package failed immediately before any dependency installation or engine-suite validation could begin.

## Reproduced failure

Observed from the shipped package before normalization:

```text
./setup-test-environment.sh: line 9: $'\r': command not found
./setup-test-environment.sh: line 10: set: pipefail\r: invalid option name
```

## Change made

Normalized POSIX line endings from CRLF to LF in:

- `setup-test-environment.sh`
- `scripts/install-ai-stack-test-env.sh`

No other script logic was changed.
No Windows batch file was changed.

## Validation outcome

After LF normalization:

- `bash ./setup-test-environment.sh` advanced into real dependency installation and verification work instead of failing at shell parsing.
- `cd tests && python run_tests.py --suite engine --quick` advanced past preflight and began real pytest execution of the intact engine suite.
- The engine suite collected `882` tests in `world-engine/tests` and executed real tests, proving that this pass did not weaken the suite target into a smaller surrogate.

Observed execution excerpt after the fix:

```text
collecting ... collected 882 items

tests/runtime/test_input_interpreter.py::test_silence_and_dots_no_command PASSED
...
tests/test_api.py::test_internal_run_detail_and_terminate PASSED
...
```

## Closure judgment

Closed for this micro-wave as an honest bounded-progress closure:

- the package-local CRLF portability defect is fixed in the shipped POSIX bootstrap files,
- the proof path now advances materially further than before,
- and the next remaining closure question is no longer shell parsing, but full end-to-end completion of the engine quick run in the audit environment.
