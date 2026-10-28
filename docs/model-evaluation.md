# Live-model review protocol — not yet run

The 140 synthetic integrity cases and scripted model tests do not measure whether Nemotron helps a researcher. Run this separate comparison only after owner configuration and a successful synthetic live verifier. Do not claim scientific accuracy from the outcome.

## Question

Does the optional two-stage review direct attention to a useful computed analysis and a defensible next step beyond the deterministic findings already displayed?

## Freeze before running

Record the repository commit, analysis/agent versions, exact NVIDIA model ID, provider, date, and temperature. Keep all failures and provider latency; do not silently retry until a preferred response appears. Use the same generated plate and researcher-selected materials in both views. The baseline is the current deterministic report and workflow guidance, not an empty screen.

## Cases

Use the bundled synthetic scenarios with seeds 100–119. Treat these as development integrity scenarios, not a newly blinded test set: the software has already been evaluated on them. A separate person must supply and label genuinely held-out cases before any independent-performance claim.

Include sample-position confounding, matched samples with a position contrast, a biological-signal simulation without a position manipulation, mixed signal/position simulation, missing controls, and inconsistent measurements. Include controls, position, and feasibility objectives; missing selections must stop before provider calls. For each position case, explicitly name the samples the model may inspect. For feasibility, deliberately include one insufficient-budget case. Never infer that simulated ground truth establishes biological truth.

A complete run uses two calls per accepted review. Establish an owner-approved call/credit budget first. Account billing controls are separate from the process allowance, which resets on restart.

## Review form

Have a domain reviewer examine baseline and model-assisted versions in randomized order, without branding, and record:

| Item | Record |
|---|---|
| Case, seed, objective, selected materials | Exact inputs |
| Provider outcome | Complete / unavailable / timed out / schema rejected / evidence rejected |
| Structural grounding | Every named ID and referenced analysis exists; record any violation |
| Relevance | 0: unrelated; 1: partly addresses objective; 2: directly addresses objective |
| Scientific restraint | Any causal, validity, significance, correction, or biological-replication overclaim |
| Practical next step | 0: unusable; 1: understandable but generic; 2: specific and appropriate to available evidence |
| Added value over baseline | Worse / same / better, with a written reason |
| Researcher burden | Time to identify the relevant limitation and decide a next step |
| Latency and calls | Observed values, including failed attempts |

The current output constrains the model to existing findings, read-only computed analyses, and allowed actions. This can prevent several invalid structures while limiting how much value the model can add. Report that tradeoff honestly. Do not equate a supported evidence reference with a scientifically useful choice.

## Report

Publish denominators, failures, criteria, and reviewer disagreements. Keep structural acceptance, subjective usefulness, and scientific validity separate. A small convenience sample supports a limited pilot report, not a general accuracy claim. If the assisted view does not help, state that result and retain the useful deterministic workflow.
