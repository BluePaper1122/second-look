# Second Look review guide

This is a reviewable research prototype. It is not yet ready for a final submission claim of successful live NVIDIA/Nebius use.

## Ten-minute product review

1. Run `python3 server.py` and open http://127.0.0.1:8765.
2. Load **Confounded sample layout**, then inspect the plate. Read the identity/position limitation and its supporting measurements. A position association does not prove an artifact.
3. Enter the well map with Tab. Use arrows and Home/End; Control+Home/End reaches the first/last well. Tab leaves the map.
4. Select both candidate samples, retain the two measured control materials, and design a follow-up with a 24-well budget. Expect 16 allocated wells: four per sample and four per control.
5. Export a handoff before checking review. Its draft well assignments should be omitted. After reviewing assay compatibility, export the CSV. Check source/layout IDs, seed, budget, and review status.
6. Change the budget or seed. The previous layout and approval should clear. Generate and review again.
7. Add a note and save a review file. Reopen it: measurements and settings return, but conclusions are recalculated and approval/model responses are not restored.
8. Load the labeled real calibration example. Expect 48 measurements, no invented controls, no Z-prime, and no follow-up allocation until control information exists.
9. Toggle Pip off if preferred. The scientific workflow should remain understandable.

## Evidence available

97 automated tests pass, including local HTTP export validation and stale-review rejection. The held-out evaluation contains 140 synthetic integrity cases; it is not a biological or live-model performance benchmark. Browser keyboard navigation was checked. Actual export-file download verification remains incomplete because the browser automation timed out; endpoint tests passed. Full screen-reader/mobile verification remains pending.

## Release gates

- Account owner configures Nebius locally using [secure setup](secure-setup.md), then runs the synthetic-only live verifier. Never put a key in chat or GitHub.
- Verify the actual NVIDIA model responses, both inference stages, failure recovery, and usefulness against deterministic QC.
- Complete browser download, responsive, and assistive-technology checks.
- Obtain domain review of scientific wording and design assumptions; do not claim biological validation.
- If a public demo is needed, provision an authorized host, TLS, secrets, provider spending controls, and judge access. Local Waitress serving has been tested; public hosting and Docker execution have not.
- Record the factual under-three-minute demo using [submission draft](submission-draft.md). Show live model use only after verification; do not substitute scripted responses without disclosure.
- User reviews project, eligibility, required assets, and final entry. The agent does not submit the hackathon entry.
