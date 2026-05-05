# ToDo

Date: 2026-05-05
Topic: Manual Add Dive Log automation flow

## Follow-ups

- Refine create-flow waits further where system picker transitions still depend on broad UI readiness.
- Consider exposing stable app-owned IDs for:
  - Mine-page log card container
  - photo source action sheet buttons such as `潛點`
- Consider tightening title matching if future QA titles become more visually truncated and ambiguous.
- Decide whether `execution/orchestrate_manual_add_log.py` should become the default entrypoint for this scenario.
- If Anti-Gravity is the preferred final commit UI, document the expected Summary and Description format in the repo workflow docs.
