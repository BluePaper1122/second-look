# Second Look — implementation status

Updated October 26, 2026 (America/Chicago).

## Working now

- Python standard-library local server and responsive browser interface.
- CSV column mapping, strict single-plate validation, missing-data handling.
- Raw plate heatmap, inspectable exact values, evidence-linked descriptive QC.
- Control separation (Z-prime), matched edge/interior contrast, design confounding and replication limitations.
- Budgeted, stratified randomized follow-up layouts with unique wells and balanced edge/interior technical replicates.
- Human review before layout export; professional handoff export; formula-safe CSV identifiers.
- Optional restrained Pip notes; revised descriptive, task-focused interface after user feedback.
- Nebius runtime integration with NVIDIA model selected by environment. Output gate accepts only known finding codes; explicit unavailable/error states.
- 12 unit tests pass; 140 held-out synthetic integrity cases pass. These do not establish scientific accuracy or model usefulness.
- Browser verified: example loading, plate inspection, follow-up allocation, human review gate.

## Required before submission

1. Verify live NVIDIA Nemotron with a real Nebius key and available model. Neither is configured in the current environment. Do not ask the user to paste keys into chat; use secure local environment configuration.
2. Expand model contribution beyond prioritization: approved analysis-tool requests and evidence-linked follow-up choices. Compare against fixed QC baseline using blinded, independently labeled scenarios; do not overstate the current integration.
3. Add control-only position contrasts and within-ID replicate variability summaries. Keep descriptive scope and disclose small sample sizes and layout assumptions.
4. Improve CSV header parsing, asynchronous request invalidation, export verification, responsive testing, and accessibility. Audit stale results after input changes or out-of-order requests.
5. Verify a permission-compatible real plate dataset and ground-truth limitations. Time-box discovery; retain explicit synthetic-only status if unavailable.
6. Add production hosting, TLS, rate/concurrency/cost limits, data notice, and judge-access persistence. Do not expose the development server publicly.
7. Prepare the sub-3-minute public demo video, factual Devpost draft, screenshots, setup instructions, and user review package by October 29.
8. Verify all source is published to https://github.com/BluePaper1122/second-look and keep it current. The GitHub connection can read metadata but initially rejected a content write with 403. Browser is authenticated and supports repository uploads. Prefer connector/CLI when write access becomes available. Do not claim a successful publication without checking the repository contents.

## Schedule and authorization

The user authorized implementation while away, GitHub publication, and continued work through the next few days. A six-hour chat continuation automation is active with instructions to stop after October 29 or completion of the review package. Do not submit the hackathon entry automatically. No subagents authorized. Local runs depend on the device and app being available; never imply work runs while the laptop is powered off.

## Run and verify

`python3 server.py`, then http://127.0.0.1:8765.
`python3 -m unittest discover -s tests -v`
`python3 evaluate.py`
`node --check static/app.js`

Keep this status accurate after each work session. Report meaningful milestones or actionable blockers, not repeated unchanged status.
