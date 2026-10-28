# Second Look review guide

This is a reviewable research prototype. It is not yet ready for a final submission claim of successful live NVIDIA/Nebius use.

## Ten-minute product review

1. Open https://second-look-qz70.onrender.com/ (the Free instance may need time to wake), or run `python3 start.py` locally. Use the supplied examples on the public demo.
2. Load **Confounded sample layout**, then inspect the plate. Read the identity/position limitation and its supporting measurements. A position association does not prove an artifact.
3. Enter the well map with Tab. Use arrows and Home/End; Control+Home/End reaches the first/last well. Tab leaves the map.
4. Select both candidate samples, retain the two measured control materials, and design a follow-up with a 24-well budget. Expect 16 allocated wells: four per sample and four per control.
5. Export a handoff before checking review. Its draft well assignments should be omitted. After reviewing assay compatibility, export the CSV. Check source/layout IDs, seed, budget, and review status.
6. Change the budget or seed. The previous layout and approval should clear. Generate and review again.
7. Add a note and save a review file. Reopen it: measurements and settings return, but conclusions are recalculated and approval/model responses are not restored.
8. Load the labeled real calibration example. Expect 48 measurements, no invented controls, no Z-prime, and no follow-up allocation until control information exists.
9. Toggle Pip off if preferred. The scientific workflow should remain understandable.

## Evidence available

100 automated tests pass, including local HTTP export validation and stale-review rejection. The held-out evaluation contains 140 synthetic integrity cases; it is not a biological or live-model performance benchmark. Browser keyboard navigation was checked. Actual synthetic handoff and reviewed CSV files were saved through the explicit browser link and inspected; expected source metadata and 16 unique CSV wells were verified. Earlier download-event waits timed out; direct file-link saving succeeded. A prepared-file link remains available if automatic download does not start, and clears when plate/settings change. The link and clearing behavior were checked in the browser. Scoped width checks at 390 and 1280 pixels showed contained plate scrolling with no page-wide horizontal overflow. Full screen-reader and broader mobile verification remain pending.

## Release gates

- Account owner configures Nebius locally using [secure setup](secure-setup.md), then runs the synthetic-only live verifier. Never put a key in chat or GitHub.
- Verify the actual NVIDIA model responses, both inference stages, failure recovery, and usefulness against deterministic QC using the [model evaluation protocol](model-evaluation.md).
- Broaden browser/device coverage and complete assistive-technology checks. Basic browser downloads and scoped responsive containment already passed.
- Obtain domain review of scientific wording and design assumptions; do not claim biological validation.
- The Free Render public HTTPS demo passed synthetic serving/export checks. Configure live secrets securely, review provider and Render usage controls, and maintain judge access. Docker execution remains unverified.
- Record the factual under-three-minute demo using [recording script](demo-script.md) and [submission draft](submission-draft.md). Show live model use only after verification; do not substitute scripted responses without disclosure.
- User reviews project, eligibility, required assets, and final entry. The agent does not submit the hackathon entry.
