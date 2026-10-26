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
- 35 automated checks pass, including real local HTTP recovery scenarios; 140 held-out synthetic integrity cases pass. These do not establish scientific accuracy or model usefulness.
- Browser verified: example loading, inspection, named-control allocation, insufficient-budget recovery, missing-model recovery that preserves the existing layout, and human review gate.
- Versioned report identifiers, source-linked layouts, evidence-linked next actions, explicit control selection, no preselected samples, editable documented seed.
- Structured recovery errors; request/body/time/concurrency limits; provider authorization, credit, rate limit, timeout, and invalid-output handling. No automatic inference retries.

## Development standard

The user wants a usable product with real failure handling, not only an MVP or test suite. Read docs/design-decisions.md before substantive changes. The user’s essay governs the builder’s decision process at a meta level: explicit purpose and assumptions, consistent principles, human agency, alternatives and counterexamples, domain context, and verification. Do not turn this instruction into philosophical branding or simulated consensus.

## Required before submission

1. Verify live NVIDIA Nemotron with a real Nebius key and available model. Neither is configured in the current environment. Do not ask the user to paste keys into chat; use secure local environment configuration.
2. Expand model contribution beyond prioritization: approved analysis-tool requests and evidence-linked follow-up choices. Compare against fixed QC baseline using blinded, independently labeled scenarios; do not overstate the current integration.
3. Completed: control-only within-ID position contrasts and within-zone replicate means/SD, displayed in an accessible table and included in handoff exports. Pooled Z-prime is withheld for mixed control identities. Four new tests independently check these behaviors; scientific validity still requires expert review.
4. CSV header parsing now handles quoted/escaped headers. Continue export verification, responsive testing, and accessibility. Controls are locked during requests to prevent input/output mismatches; changes to sample selections or budget clear previous layouts. Audit stale results after input changes or out-of-order requests.
5. Verify a permission-compatible real plate dataset and ground-truth limitations. Time-box discovery; retain explicit synthetic-only status if unavailable.
6. Add production hosting, TLS, rate/concurrency/cost limits, data notice, and judge-access persistence. Do not expose the development server publicly.
7. Prepare the sub-3-minute public demo video, factual Devpost draft, screenshots, setup instructions, and user review package by October 29.
8. Publication verified: all 20 source/document/example files were present on main at commit 7c86c6a. Keep https://github.com/BluePaper1122/second-look current. The GitHub connector rejected a content write with 403. Network-enabled gh authentication is verified and supports direct git publication; the earlier sandboxed invalid-sign-in result was caused by unavailable network access. Browser uploads initialized main. Local and remote histories have been merged without conflicts; prefer network-enabled git pushes now.

## Schedule and authorization

The user authorized implementation while away, GitHub publication, and continued work through the next few days. A six-hour chat continuation automation is active with instructions to stop after October 29 or completion of the review package. Do not submit the hackathon entry automatically. No subagents authorized. Local runs depend on the device and app being available; never imply work runs while the laptop is powered off.

## Run and verify

`python3 server.py`, then http://127.0.0.1:8765.
`python3 -m unittest discover -s tests -v`
`python3 evaluate.py`
`node --check static/app.js`

Keep this status accurate after each work session. Report meaningful milestones or actionable blockers, not repeated unchanged status.
