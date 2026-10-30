# Demo recording script — rehearsal draft

Target length: 2 minutes 40 seconds. This is a script, not evidence of a completed video. Record synthetic measurements only. Keep keys, account pages, private files, and terminal history outside the capture.

## Before recording

- Run the app and rehearse the review-guide steps.
- Keep the example label and limitations visible. Pip is optional; choose whichever presentation feels natural.
- Local credentials are configured and one synthetic verifier run succeeded, but a subsequent browser review failed format validation. The successful on-screen segment remains blocked until reliability is addressed and rendering is verified. Record the actual model identifier and both stages. Do not replace real inference with a scripted response and call it live.
- Verify the exported file actually downloads and opens. Endpoint tests alone do not establish that browser behavior.
- Use the verified public demo at https://second-look-qz70.onrender.com/ and repository https://github.com/BluePaper1122/second-look. Free-instance wake-up may delay first access. The synthetic handoff and reviewed CSV were saved and inspected through the browser; repeat the intended recording flow before capturing it.

## 0:00–0:20 · The problem

Show the input screen.

“Second Look helps a researcher decide what to repeat after a plate assay. When one sample is measured only near the edge and another only in the interior, their difference can reflect the sample, the position, or both. A larger response alone cannot resolve that question.”

## 0:20–0:55 · Inspect the evidence

Load **Confounded sample layout**, inspect, select one edge well and one interior well, and expand the sample-position finding.

“This example is synthetic. The map shows raw measurements, and each well exposes its exact value. The findings point to the measurements used in the calculation. Here the sample identities and position zones overlap. The app reports that limitation; it does not correct the values or declare an artifact.”

## 0:55–1:30 · Live investigation — successful rendering still pending

Only after live verification: select the relevant samples, choose **Investigate selected samples by position**, request the review, then show the returned computed evidence and next step.

“The optional Nemotron review runs through Nebius. The model requests bounded, read-only analyses on materials I selected. Code calculates the evidence; the model then chooses a supported next step. It cannot change the measurements or select new experimental samples.”

Use the actual screen to describe what this particular response did. Do not promise that every response uses every selected sample or finds a cause. If verification is still missing, state that clearly and omit a successful-live-use claim; the entry remains incomplete.

## 1:30–2:10 · Plan a concrete follow-up

Show both selected samples, the named negative and positive controls, budget 24 and seed 11. Generate, show **What changes in this repeat?**, inspect the observed/proposed counts and well lists, then explicitly review compatibility.

“For these two samples, this template uses 16 wells. Each sample and each control gets two edge wells and two interior wells. Eight budgeted wells remain unused. The seed makes the layout reproducible. This design checks a position explanation; it does not balance every biological factor or replace independent biological replication. The researcher must review assay compatibility before exporting.”

## 2:10–2:40 · Preserve context and state the limits

Export the reviewed CSV and show source/layout identifiers. Briefly show researcher notes and the real calibration example if time permits.

“The handoff preserves evidence and researcher notes, and omits unreviewed assignments. Exported layouts identify their source and settings. Our synthetic checks test integrity and allocation constraints. A real calibration case checks measurement preservation and missing-control handling. Neither establishes biological validity or live-model usefulness. The next step is assay-specific expert review and a measured comparison with local QC.”

## Final review

Watch the rendered recording and check that labels, values, model status, and limitations are legible. Check audio and runtime. Update the submission draft using verified final behavior, then let the user review the actual video and entry. This workflow does not submit the hackathon entry.
