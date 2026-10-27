# Design decisions and review standards

This records implementation choices, their practical justifications, and their limits. A philosophical framework does not certify software correctness.

The user requested that development itself follow their essay: https://criticalphilosophy.medium.com/a-humanistic-hypothesis-of-artificial-intelligence-design-and-training-4d682cf75bed. The framework is applied to how decisions are made and checked: explicit purpose, consistent rules, preserved human agency, serious consideration of alternatives, domain context, and verification. It does not require philosophical language in the interface, simulated debates, or additional agents.

## Current decisions

| Choice | Purpose and justification | Boundary / reconsideration condition |
|---|---|---|
| One 96-well plate and one numerical channel | A clear supported domain permits exact position validation and intelligible calculations. | Broaden only after defining and checking multi-plate/batch and measurement-channel behavior. |
| Deterministic arithmetic, constrained model output | Numerical facts must remain inspectable and independent of a language model's fluency. | A future model analysis must use approved tools and evidence references; never accept unsupported quantities. |
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
