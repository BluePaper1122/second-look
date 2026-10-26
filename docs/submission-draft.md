# Submission draft — incomplete, for later review

## Project
Second Look: review a plate assay and plan what to repeat.

## Problem
A measured response can be difficult to interpret when sample identity and plate position overlap. Researchers need to see those limitations and choose a follow-up that can separate plausible explanations.

## Current implementation
A local application imports a 96-well plate, calculates descriptive QC, connects findings to their supporting measurements, and creates a budgeted follow-up that places selected samples and controls at both edge and interior positions. A human reviews the layout before export. Optional NVIDIA Nemotron review through Nebius prioritizes existing findings; successful live use still requires verification.

## What is different
The proposed contribution connects a specific evidence limitation to a constrained follow-up design and a concise researcher handoff. QC and plate normalization already exist. Do not claim novel statistical methods or global uniqueness.

## Evaluation so far
12 unit tests and 140 held-out synthetic integrity cases pass. These check arithmetic, validation, evidence references, and layout properties. They do not measure scientific validity, artifact-detection accuracy, or live model quality. No verified real assay dataset has been used yet.

## Before publishing this draft as a submission
Replace status with verified final behavior. Include actual live model ID, integration evidence, hosted demo URL, public repository URL, measured evaluation results, limitations, and a public YouTube video shorter than three minutes. Supply honest platform feedback. Confirm current hackathon rules and eligibility.

## Demo outline
- 0:00–0:20: State the sample-position confounding problem.
- 0:20–0:55: Inspect an explicitly labeled synthetic example and exact measurements.
- 0:55–1:30: Demonstrate verified live model use, or do not claim it works.
- 1:30–2:10: Generate a constrained follow-up and show its limitations and review gate.
- 2:10–2:40: Export a handoff and state evidence, evaluation scope, and remaining limitations.
