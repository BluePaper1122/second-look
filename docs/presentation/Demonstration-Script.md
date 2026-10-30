# Second Look: demonstration script

Target: about 2 minutes 45 seconds, including short pauses. Use the app for most of the recording. The PowerPoint supports the explanation and provides a closing screen. The appendix sits outside the timed pitch.

## Recording order

Use slides 1–2 for the opening, switch to the app for inspection, AI review, follow-up and export, then close on slide 6. Slides 3–5 are optional cutaways or rehearsal aids. A slideshow alone will not demonstrate the working software.

Rehearse the narration once aloud. Shorten pauses or remove the optional Pip line if the recording approaches three minutes. Keep all synthetic-data labels visible. Use your own speaking rhythm. Describe what is on the screen rather than memorizing sentences.

## 0:00–0:15: the reason for the project

**Show:** title, then the app.

“Before spending another plate, what would you need to check? Second Look helps a researcher inspect a plate assay and plan a repeat when sample identity and position overlap.”

## 0:15–0:40: the concrete problem

**Show:** load **Confounded sample layout**, inspect, open a measured well and the position finding.

“This example is synthetic. One candidate appears only at the edge. The other appears only in the interior. A difference between them cannot tell us whether the sample, its position, or both contributed. Here I can inspect the raw values and the wells behind each finding.”

## 0:40–1:15: what the AI actually does

**Show:** select the candidate samples and measured control identities. Choose **Investigate selected samples by position**. Use one of the two endings below, matching the actual recorded outcome.

“The optional AI review uses NVIDIA Nemotron Nano through Nebius. It requests limited analyses on materials I select. Code computes the results, and the model selects evidence references and a permitted next step. The researcher still decides what to repeat.”

**If a complete result actually renders:**

“Here are the analyses this run requested and the evidence it selected.”

Point to the actual returned analysis names and next step. Do not say it found a cause or improved a decision unless you have evidence.

**If the run fails, or successful rendering remains unverified:**

“One live two-stage test completed, but a later browser run returned invalid output. The app rejected it and kept the local findings. Reliable on-screen AI review remains unfinished.”

Show the real error state or the dated verification record. This honest fallback does not resolve the live-demo readiness gap. Never substitute a mocked success. Do not initiate extra inference beyond the approved cumulative test allowance. Wait time can be trimmed in editing with a visible “wait shortened” caption.

## 1:15–2:00: a repeat with a purpose

**Show:** both candidates selected, named negative and positive controls, budget **24**, seed **11**. Generate the follow-up and open **What changes in this repeat?**

“For these two candidates and two controls, the template allocates sixteen wells. Each material gets two edge and two interior wells. Eight budgeted wells remain unused. This table shows the missing position zone added for both candidates. I can inspect the exact proposed wells. The design checks coverage without predicting what the experiment will find.”

## 2:00–2:30: the human decision

**Show:** compatibility review, reviewed CSV export and source/layout identifiers. Briefly show researcher notes.

“Before export, the researcher checks compatibility. The handoff keeps notes and source identifiers with the proposal. The current checks cover calculation and layout integrity. They do not establish biological validity. The researcher keeps responsibility for deciding whether this repeat fits the assay.”

Optional, only if there is time: “Pip adds a small, optional nudge. The measurements stay the same.”

## 2:30–2:45: the close

**Show:** slide 6 with demo and repository addresses.

“The goal is to make the reason for a repeat easier to inspect. You can try the examples and follow each proposal back to the measurements. Next comes assay-specific researcher review and a measured test of whether the AI adds value.”

## Before upload

- Verify the final recording stays below three minutes and text is legible.
- Show actual app interactions, not only slides. Preserve the distinction between observed values and proposed wells.
- Keep credentials, billing pages, private files and private research data outside the capture.
- Verify the downloaded export opens. Do not click the review attestation without inspecting the proposal.
- Upload the finished video publicly to YouTube and check it while signed out. This script is not a completed recording or submission.
- Public model access is currently disabled. The existing Render demo demonstrates the deterministic workflow. Do not describe it as a publicly available live AI service.

## Authenticity and attribution

Use “I” for choices you can explain and the actions you demonstrate. Avoid invented lab experiences, user interviews, customers, savings, accuracy claims or a claim that you trained Nemotron. If asked about implementation, a truthful description is: “I developed the idea and design priorities, and used Codex to assist with implementation and checks.” Adjust that wording to your actual contribution and follow any organizer disclosure requirements. Rehearse explaining the code and limitations in your own words.

## What past winners influenced

These are presentation lessons inferred from organizer accounts, not proof of a winning formula. We did not reproduce or score their applications.

- NVIDIA's 2025 **Route Optimization Agent**, first place: a specific operational task, explicit constraints and a complete input-to-action workflow. Second Look borrows that narrative discipline by showing the actual layout and supporting measurements. [NVIDIA's winner review](https://developer.nvidia.com/blog/hackathon-winners-bring-agentic-ai-to-life-with-the-nvidia-nemo-agent-toolkit/)
- **Nomi**, AWS/NVIDIA grand-prize winner: a clearly identified human audience, seniors. Second Look centers the researcher's decision and preserves their authority. The organizer's short announcement does not establish which presentation techniques caused the award. [Official winners](https://nvidia-aws.devpost.com/updates/38660-and-the-winner-is)

Current rules require the working project, public code, description, track, platform feedback and public YouTube demonstration. Our proposed track is **Best Apps and Agents**. [Official rules](https://nebiusglobalaihackathon.devpost.com/rules)

Deadline: **October 30, 2026, 10:00 a.m. Pacific / noon Chicago**. Aim for final review and submission by 11:00 a.m. Chicago. The entrant performs final submission.
