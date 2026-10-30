# Submission draft — incomplete, for later review

## Project
Second Look: review a plate assay and plan what to repeat.

## Problem
A measured response can be difficult to interpret when sample identity and plate position overlap. Researchers need to see those limitations and choose a follow-up that can separate plausible explanations.

## Current implementation
The application at https://second-look-qz70.onrender.com/ imports a 96-well plate, calculates descriptive QC, connects findings to their supporting measurements, and creates a budgeted follow-up that places selected samples and controls at both edge and interior positions. An observed-versus-proposed table shows exactly which selected materials gain edge/interior coverage, with supporting wells and explicit limits. A human reviews the layout before export. The optional NVIDIA Nemotron workflow requests scoped read-only analyses and selects a next step using their computed evidence. It uses two inference calls with bounded schemas and evidence-reference validation. One real synthetic two-stage Nano review passed on Nebius. A subsequent local browser run returned invalid model output and was rejected. Reliable live rendering and model usefulness are not established; public model access is not enabled.

## What is different
The proposed contribution connects a specific evidence limitation to a constrained follow-up design and a concise researcher handoff. QC and plate normalization already exist. Do not claim novel statistical methods or global uniqueness.

## Evaluation so far
103 automated checks and 140 held-out synthetic integrity cases pass. These check arithmetic, validation, evidence references, and layout properties. They do not measure scientific validity, artifact-detection accuracy, or live model quality. A 48-well real instrument-calibration compatibility case now verifies exact measurement preservation and abstention when assay-control roles are absent. It is not a biological validation benchmark; real assay validity and model usefulness remain unverified.

## Serving evidence
A separate WSGI gateway and hash-pinned Waitress launcher have been verified locally through HTTP, including synthetic inspection, health/HEAD, security headers, and origin rejection. The Free Render demo is now reachable over managed HTTPS and passed all 12 synthetic transport/export checks. Free-instance sleep can delay first access; ongoing judge availability still needs monitoring. Local credentials were configured with explicit approval, and synthetic live verification produced one success and one rejected browser result. See live-verification.json; no public model key was activated.

## Before publishing this draft as a submission
Replace status with verified final behavior. Include actual live model ID, integration evidence, hosted demo URL, public repository URL (https://github.com/BluePaper1122/second-look), measured evaluation results, limitations, and a public YouTube video shorter than three minutes. Supply honest platform feedback. Confirm current hackathon rules and eligibility.

## Demo outline
- 0:00–0:20: State the sample-position confounding problem.
- 0:20–0:55: Inspect an explicitly labeled synthetic example and exact measurements.
- 0:55–1:30: Demonstrate verified live model use, or do not claim it works.
- 1:30–2:10: Generate a constrained follow-up and show its limitations and review gate.
- 2:10–2:40: Export a handoff and state evidence, evaluation scope, and remaining limitations.
