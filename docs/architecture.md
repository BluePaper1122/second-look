# Implementation map and explainable boundaries

Use [design decisions](design-decisions.md) for the reasons and tradeoffs, [first run](first-run.md) for operation, and STATUS.md for evidence and unfinished work. This map connects those decisions to code; it does not certify correctness.

| Component | Responsibility | Boundary / failure behavior |
|---|---|---|
| `assay.py` | Parse one plate, compute descriptive QC, allocate the stated template | Strict roles/wells/numeric limits; no normalization, biological acceptance, or inferred controls |
| `workflow.py` | Link measured findings to deterministic next steps and report identity | Fingerprint is traceability, not authentication or scientific proof |
| `analysis_tools.py` | Calculate approved, read-only scoped analyses | Researcher-selected samples/controls only; no arbitrary code or experimental execution |
| `agent_review.py` | Bound the model’s two stages and validate evidence/objective linkage | Unsupported scopes, references, actions and incomplete responses are rejected |
| `server.py` | Shared business routes, local HTTP, bounded provider requests | Recoverable errors; no automatic inference retry; safe opaque error logs |
| `gateway.py`, `serve.py` | WSGI transport and maintained HTTP serving | Exact origin/Host, headers, body/rate/concurrency limits; managed TLS belongs to host |
| `local_config.py`, `setup_nebius.py` | Explicit, hidden local credential entry and restricted loading | No shell evaluation or echoed fallback; no secrets in exports; hosted process uses environment secrets |
| `review_file.py` | Validate portable sessions and reanalyze original data | Saved conclusions, model responses and approval are not trusted or restored |
| `exports.py` | Recompute reviewed proposals and create traceable handoffs | Reject stale settings; omit unreviewed assignments; quote IDs and separate user notes |
| `static/app.js` | Present measurements and maintain browser state | Settings invalidate proposals; async operations lock inputs; model failure preserves local results and clears old model output |
| `static/index.html`, `style.css` | Semantic controls, keyboard plate map, optional Pip | One Tab stop for wells; contained horizontal plate scrolling; no claim of full accessibility conformance |
| `start.py` | Explain startup and optionally open local browser | No installation, network inference, silent port fallback, or termination of another process |
| `render.yaml` | Reviewable native-Python Free demo settings | Manual deploy; no credentials; free quotas/sleep are operational limitations |
| `evaluate.py`, `tests/`, `scripts/smoke_http.py` | Check deterministic invariants, exception handling, transport and exports | Scripted and synthetic checks are separate from live usefulness and biological validation |

## Data lifecycle

The browser holds CSV text until it is replaced or the tab closes. Inspection sends it to the application server; the hosted server is on Render. The application intentionally uses request memory without a data store and suppresses routine application access logs. This does not control provider infrastructure retention. Optional model review separately sends a computed summary, including identifiers and supporting measurements, to Nebius. Export/save is an explicit user action; portable files include measurements and notes and need appropriate handling.

## Operational numbers

One plate, 96 positions, one channel and 1 MB CSV bound supported scope. The position-check template uses four technical wells per sample plus eight named control wells, with at most 16 samples because edge capacity is 36. Default budget 24 and seed 11 are editable conveniences. Two provider slots, ten calls/minute, 100 attempts/process, input limits and timeouts are operational guardrails, not scientific conclusions or billing caps. See deployment instructions for server limits and restart behavior.

## Review standard

A design choice should identify a user problem, a reason, an alternative/tradeoff, a failure boundary, and evidence. Changed assumptions require revisiting the choice. User agency and explanatory clarity guide development; neither philosophical consistency nor passing tests substitute for direct checks and domain review. Known gaps remain explicit in STATUS.md and the review guide.
