# world-engine SAD restructure evidence — 2026-06-23

## Summary

| Item | Before | After |
| --- | ---: | ---: |
| mechanism-catalog rows | 0 | 13 |
| evidence-matrix rows | 0 | 8 |
| UML decisions/ files | 0 | 5 |
| TRACEABILITY Decision column | no | yes |
| §9 duplicate `### D` headings | 22+ nested | 16 unique top-level only |
| D16 placement | before D7 | after D15 |
| Empty Status fields | 14 | 0 |

## Cleanup commands

```powershell
python scripts/sad_world_engine_section9_cleanup.py
python scripts/sad_fill_section9_status.py
python scripts/sad_section9_hygiene.py --check
```

## Notes

ADR sub-sections under D5/D10/D13/D14 are now `####` headings (detail lives in SAD; diagrams in UML `decisions/`).
