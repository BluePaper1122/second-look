# Design decisions and review standards

This records implementation choices, their practical justifications, and their limits. A philosophical framework does not certify software correctness.

The user requested that development itself follow their essay: https://criticalphilosophy.medium.com/a-humanistic-hypothesis-of-artificial-intelligence-design-and-training-4d682cf75bed. The framework is applied to how decisions are made and checked: explicit purpose, consistent rules, preserved human agency, serious consideration of alternatives, domain context, and verification. It does not require philosophical language in the interface, simulated debates, or additional agents.

## Current decisions

| Choice | Purpose and justification | Boundary / reconsideration condition |
|---|---|---|
| One 96-well plate and one numerical channel | A clear supported domain permits exact position validation and intelligible calculations. | Broaden only after defining and checking multi-plate/batch and measurement-channel behavior. |
| Deterministic arithmetic, constrained model output | Numerical facts must remain inspectable and independent of a language model's fluency. | A future model analysis must use approved tools and evidence references; never accept unsupported quantities. |
| Bounded two-stage model review | A useful model must help choose an investigation and then respond to the measured evidence, rather than merely restating a report. | Only read-only tools and researcher-selected materials are allowed. Unknown references and partial completion are rejected. Scripted-response success does not establish live model quality. |
| No automatic biological hit ranking | Measurements alone do not identify activity or causation. | Require assay-specific definitions, relevant ground truth, and independent review before adding ranking. |
| No preselected follow-up samples | Alphabetical order and convenience are not scientific reasons to spend wells on a sample. | Researchers choose IDs; future selection suggestions need explicit objectives and reversible approval. |
| Explicit measured control identities in follow-up | Generic control names hide a real experimental choice. | The user selects materials present in the input. Missing control information blocks this design step, not report inspection. |
| Withhold pooled Z-prime for mixed control IDs | Distinct materials may differ for reasons unrelated to assay precision. | A future interface can support explicitly selected control pairs without silently pooling them. |
| Descriptive within-ID, within-position comparisons | They make a narrower, defensible claim than an unadjusted causal position conclusion. | Sparse or unbalanced data remain limited; never imply normalization proves the underlying biology. |
| Four wells per material: two edge and two interior | The question is whether position could contribute; crossing sample identity with position directly addresses that question and gives minimal within-zone replication. | It is a specific design template, not an optimal design or sufficient biological replication. |
| Default well budget 24 and randomization seed 11 | The budget accommodates four sample IDs plus two control materials in this template; a fixed seed makes allocation reproducible. | Both are visible and editable. The numerical seed has no biological significance. |
| Z-prime reference 0.5 is labeled exploratory | The reference helps interpretation without replacing an assay's own criteria. | Never turn the reference into a universal acceptance decision. |
| Human review before layout export | The researcher knows handling constraints, materials, and experimental context the app does not possess. | A checkbox records a review step; it does not establish expertise or prove scientific validity. |
| Local processing; explicit optional model call | Avoid sending measurements to an external provider as a side effect of inspection. | Public hosting or broader data transfer requires an explicit product design and clear user notice. |
| Model/network failures preserve local work | A service outage does not invalidate deterministic measurements or justify losing a researcher's input. | Errors must identify a recovery path and never masquerade as successful inference. |
| Bounded calls, response sizes, and request duration | Resource limits prevent an unresponsive interface and uncontrolled provider work. | Current limits are operational defaults, not scientific assumptions; monitor and adjust for documented usage. |
| Report fingerprint and analysis version | A handoff must identify which measurements and calculation version it refers to. | A fingerprint is an identifier, not a security signature, proof of truth, or identity verification. |
| Explicit portable review files | Researchers can resume work and share context without adding an account or silent data storage. | Files contain measurements and notes; the user chooses where to save them. Reopening recalculates findings and resets approval rather than trusting saved conclusions. |
| External-data compatibility kept distinct from validation | Real readings exercise ingestion and abstention but cannot establish artifact detection accuracy without relevant ground truth. | Preserve source bytes, attribution, license and transformation rules. A calibration gradient is intentional, not proof of an artifact; do not infer assay controls from signal magnitude. |
| Verified OS trust fallback | The local Python installation had no default CA roots, blocking legitimate HTTPS. | Load the established OS CA bundle only when no roots and no explicit user trust paths are configured. Keep certificate and hostname verification required. |
| Shared business routes, separate production transport | Local and hosted modes must calculate and validate the same data. A WSGI contract allows a maintained server to handle public HTTP instead of exposing a development server. | Actual Waitress serving was checked locally; managed TLS, container build and public judge access still require deployment verification. |
| Explicit call allowance and request caps | Limit the work that a public demo can trigger while retaining local analysis after model capacity is exhausted. | Counts are operational defaults, not scientific rules or monetary billing protection. Process restart and replication reset the allowance; provider-side spending controls remain necessary. |
| Hidden local credential setup | The account owner can supply required access without revealing a key in chat, source control, or command-line arguments. | Storage is explicitly plaintext with user-only permissions; no hidden-entry fallback to echo, no automatic provider calls, and no local secret file loaded by production serving. |
| Restrained, optional Pip | Personality is a preference, not a source of scientific authority. | The user can hide it; reports retain professional language. |

## Changes made following this review

- Removed alphabetical preselection of the first two samples.
- Made the randomization seed visible and editable, with its purpose stated.
- Required actual control identities for follow-up instead of implicitly inventing materials.
- Separated missing information, service unavailability, and unsupported conclusions.
- Added evidence-linked next actions, while keeping assay acceptance with the researcher.
- Removed a generic competing-explanations panel introduced during an overly literal interpretation of the essay. Without a specific hypothesis and adequate contextual data, it risked presenting boilerplate as scientific analysis.

## Review obligations for subsequent work

For each substantive change, record its user problem, scope, evidence, important alternative or tradeoff, failure behavior, and verification. Use consistent rules across equivalent inputs. Preserve reversibility and meaningful human choice. Treat disagreement and counterexamples as reasons to re-evaluate the design rather than explanations to suppress. Verify implementation with direct behavior checks; seek domain review for scientific validity. Do not equate a passing test suite, AI consensus, or a philosophical label with a finished product.

## Export review boundary

A handoff is another route by which a draft could become actionable. It therefore follows the same review boundary as the layout CSV: unreviewed assignments are omitted. The server recomputes allocations and compares source and layout identifiers before reviewed export. These identifiers detect ordinary stale-state mistakes; they are not signatures, authentication, or proof that an expert reviewed the experiment. Export metadata makes the proposal traceable without inventing that assurance. Sorting selected IDs before seeded allocation makes equivalent selections reproducible regardless of click order.

The plate map uses one Tab stop with arrow navigation so inspecting 96 wells does not require 96 Tab presses. Empty wells remain inspectable and are described as unmeasured, preserving the distinction between missing data and zero.

## Evaluation follows product constraints

Held-out allocation checks now enter through the same validation path as the UI. Calling the lower-level allocator with generic controls in a missing-control scenario previously missed an important boundary: allocation should be blocked when measured control identities are absent. The evaluation now checks that boundary explicitly and independently counts material/zone allocations and verifies roles, budget, unique positions, and selection-order invariance for feasible cases. This improves integrity coverage; it does not supply scientific ground truth or an independent biological benchmark.

## Export recovery when browsers block automatic downloads

After asynchronous server validation, browser policy may prevent an automatic download. A persistent, attached link now exposes the prepared file and its name so the researcher can initiate it directly. A short-lived detached link offered no visible recovery path. Only the most recent file URL remains active, and changes to plate or follow-up settings revoke it to avoid presenting stale output as current. Browser checks verified link creation and budget-change removal; actual downloaded-file inspection remains outstanding because the download-wait tooling timed out. Narrow and desktop containment were checked separately, without claiming full accessibility conformance.

## Preserve the review objective through final selection

A two-analysis plan could compute the requested position analysis, then cite only feasibility in its final selection. Valid references alone therefore did not guarantee even structural relevance to the user’s question. The final selection now must include at least one computed analysis of the required type, and the second-stage prompt names those required evidence IDs. Scripted counterexamples verify rejection of unrelated-only selections and acceptance when objective evidence is the second analysis. This is a structural constraint, not proof that the chosen recommendation is scientifically useful; live evaluation remains required.

## First-run and recovery clarity

The local launcher shares the existing server entry point, validates its explicit port, and prints the address and stop instructions. Opening a browser is optional; it does not install packages, silently choose another port, terminate a competing process, or call a model. The first-run guide separates a usable synthetic local workflow from account-dependent live inference. Handoff IDs are JSON-quoted so data containing line breaks remains data rather than becoming a report heading. A fresh model request clears the old response before making the call; retaining it after an unavailable retry would blur which attempt produced the visible evidence.

## Render demo configuration

The user chose Render. A native Python Free service uses the already tested Waitress transport rather than introducing another application framework. The exact public origin comes from Render’s server-provided RENDER_EXTERNAL_URL in the start command, preserving Host and Origin checks without trusting request forwarding headers. Auto-deploy is disabled to keep public review on an explicitly deployed revision. No model key is bundled. Free instances sleep and have quotas; their process restart resets application call counts, so these counts must never be described as billing caps. Public deployment still requires actual verification and account usage review.
