# Evidence-based judging review — October 29, 2026

This is a builder self-review, not an unbiased panel, official score, representative competition survey, or winning-probability estimate. The [official gallery](https://nebiusglobalaihackathon.devpost.com/project-gallery) was not published when checked. Two independently discoverable public repositories below are a convenience sample; their claims were read, not independently reproduced. Missing evidence is marked unknown rather than assumed failure.

## Eligibility before scoring

The [official rules](https://nebiusglobalaihackathon.devpost.com/rules) require a functioning Nebius runtime integration with an NVIDIA open model. Our code implements two-stage inference, but no successful real call is verified. Treat this as a blocked baseline gate, regardless of the quality of local QC or hosting. A public YouTube demonstration shorter than three minutes and final user entry review are also outstanding. Submission closes October 30 at 10:00am Pacific / noon Chicago. Verify eligibility with the entrant; do not infer it from account access. Keep judge access free through the stated judging period ending December 15.

The four equally weighted criteria are technical implementation, design, potential impact and idea quality. The organizer’s [judging update](https://nebiusglobalaihackathon.devpost.com/updates/46204-here-s-how-judging-works) favors useful multi-step workflows over superficial wrappers.

## Anchors and provisional assessment

Use 1 for unsupported/incomplete evidence, 3 for a coherent demonstrated implementation, and 5 for convincing, independently verified excellence. These are internal anchors, not the organizers’ detailed scoring rubric. No overall rank or score is computed while baseline viability is blocked.

| Criterion | Current evidence | Internal provisional range | What would change it |
|---|---|---|---|
| Technical implementation | Deterministic QC, read-only tool chain, constrained model schemas, export/recovery checks, public HTTPS app; live provider path unverified | 1–2 / 5 | Successful live use, inspected results, and a measured comparison with local QC |
| Design | Working input → evidence → chosen follow-up → reviewed export → portable review flow; keyboard map; notes separated by report | 3–4 / 5 | Independent first-use observation, broader accessibility checks, final video |
| Potential impact | Specific position-confounding problem and concrete layout constraints; no user study, measured lab savings or biological validation | 2–3 / 5 | Domain feedback and a small, honest task-completion comparison |
| Idea quality | Connects evidence limitations to a reproducible repeat and inspectable before/after design coverage; underlying QC methods are established | 3 / 5 | Demonstrated model contribution and a researcher explaining why this workflow helps |

## Limited public comparisons

| Project | Primary public evidence reviewed | Lesson for Second Look | Unknowns |
|---|---|---|---|
| [Goldito](https://github.com/minsikpaul92/Goldito) | Repository presents pet-sitting workflows, judge demo access, a video link, human approval, and multiple model uses | A clear audience, frictionless judge entry and a complete demonstration matter as much as model plumbing. Human approval alone is not unique. | Live claims and impact estimates were not independently tested here; no numerical score assigned |
| [SafeRotate](https://github.com/smanika3/Nebius-x-NVIDIA-Hackathon) | Repository describes credential-consumer discovery, runtime evidence and gated rotation with a Nemotron role | Evidence-linked action is a broader pattern, not a uniqueness claim for our product. Explain the assay-specific contribution. | Reviewed repository listing showed documentation rather than an executed application; working status remains unknown |

## Changes prioritized from this review

1. **Eligibility and evidence first:** real NVIDIA/Nebius inference and final video have higher priority than another neural network. Nemotron already is the neural model. Training an assay predictor on bundled simulations would not establish usefulness on biological data.
2. **Make the follow-up’s purpose visible:** implement observed versus proposed edge/interior counts, with exact supporting wells for selected samples and controls. Count which samples gain both-zone coverage. For already crossed samples, say so rather than inventing a new gap. Never predict responses or claim causal identification, statistical power or biological replication.
3. **Show the human workflow:** preserve report-specific notes, researcher sample choice, explicit compatibility review and a traceable handoff. Document limitations where a decision is made.
4. **Demonstrate rather than decorate:** keep the interface descriptive and Pip optional. No invented impact statistics, unsupported global uniqueness, simulated live responses, or score inflation.

The before/after coverage display is a useful product explanation and differentiator within this limited comparison; it is not a claim of a novel statistical method. Final judging evidence must describe the actually deployed revision and observed behavior.

For a genuinely external usability check and a more consistent comparison procedure, use [independent review](independent-review.md). That procedure is prepared but has not been executed; no independent verdict is claimed.
