# Review checkpoint — October 28, 2026

**Status:** runnable, publicly reviewable research prototype; approximately 85% submission-ready by development estimate. This checkpoint is incomplete. It is not a submitted entry, scientific validation, or verified live-AI demonstration.

## Try it

Open https://second-look-qz70.onrender.com/ and use the supplied synthetic examples. The Free Render instance may take about a minute to wake. Start with **Confounded sample layout**, inspect, select both candidates, and design with budget 24. Expect 16 allocated wells. Read compatibility limitations before attesting review.

For local use, run `python3 start.py` from the repository folder with Python 3.11+. No third-party packages are required for local analysis. Use `--port 8766` if the default port is occupied; `--no-browser` prints the address without opening it. Keep the terminal open. Control+C stops the app.

## Read in this order

1. [First run](first-run.md): operation and recovery.
2. [Review guide](review-guide.md): focused product checks and remaining gates.
3. [Design decisions](design-decisions.md) and [architecture](architecture.md): reasons, assumptions, alternatives and code boundaries.
4. [Submission draft](submission-draft.md) and [demo script](demo-script.md): factual material awaiting final verification and recording.
5. [Model evaluation protocol](model-evaluation.md): a comparison plan that has not been run.

## Verified evidence

- 103 Python tests passed, including recovery/error paths and export validation. Three additional Node tests cover note isolation, restoration/import replacement and invalid-update preservation.
- 140 held-out-seed synthetic integrity cases passed. These are development checks, not a blinded biological or model-performance benchmark.
- All 11 synthetic HTTPS checks passed on the public Render origin; no inference calls were made.
- Actual synthetic handoff and reviewed CSV files were saved through the browser and inspected. Source/layout metadata and 16 unique CSV wells were verified.
- Keyboard navigation and scoped 390/1280-pixel horizontal containment were checked. Full assistive-technology conformance remains unverified.
- A 48-measurement real calibration compatibility case preserves source data and abstains from invented assay-control roles. It is not biological validation.

## Still required

1. Owner configures Nebius securely; successful two-stage live NVIDIA review and its rendering/recovery must be verified. Do not put a key in chat, GitHub, or a recording.
2. Evaluate usefulness against the deterministic baseline and obtain relevant domain review. No model usefulness or assay-validity claim is currently supported.
3. Record and review the actual public video, finalize submission fields and eligibility checks, and reserve time for user approval. No entry will be submitted automatically.
4. Review hosting/provider usage controls and monitor judge access. The Free compute selection does not eliminate all workspace quotas or possible overages; no paid compute plan was selected.

## Source snapshot

The optional review ZIP is made from committed, tracked repository contents only. It excludes ignored local credentials and review files. It is a source checkpoint, not a deployed environment or a substitute for live verification. The GitHub repository remains the current source: https://github.com/BluePaper1122/second-look.
