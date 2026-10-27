# Second Look

Review a 96-well assay plate and plan a follow-up that checks whether sample position could explain a result.

**Status:** local research prototype. Deterministic analysis and layout generation work. Live NVIDIA Nemotron calls are implemented but have not been verified with a real Nebius account. Synthetic examples are accompanied by a separately licensed, provenance-tracked real calibration compatibility case. No biological validity has been established. This is not a validated scientific or clinical product.

## Run locally

Requires Python 3.11 or newer. No third-party Python packages are required.

```sh
python3 server.py
```

Open http://127.0.0.1:8765. To use another port, set `PORT`. The server binds to loopback only and is not a production public host.

```sh
python3 -m unittest discover -s tests -v
python3 evaluate.py
```

## Workflow

1. Load a labeled synthetic example or upload one CSV (at most 1 MB and 96 rows).
2. Confirm the column mapping; inspect raw values and evidence-linked QC findings.
3. Optionally select a review objective and request a bounded Nemotron analysis workflow. Use the follow-up controls to select the samples, control materials, and budget it may inspect.
4. Select sample IDs and a well budget. Review the proposed layout before CSV export.
5. Add researcher notes and save a portable review file, or export a handoff note documenting observations and uncertainty.
6. Reopen a saved `.secondlook.json` file to recompute the report and restore notes, mappings, sample choices, controls, budget, and seed. Model responses and layout approval are not restored. Invalid files leave the current review intact.

Required fields: `plate_id,well,sample_id,value,control`. Well positions are A01–H12; control roles are `sample`, `negative`, or `positive`. Each well appears once. Use the same sample ID for repeated measurements of the same material; use distinct IDs for distinct controls. Technical replicates are not assumed to be independent biological replicates. Inspect one plate and one measurement channel at a time.

## What is calculated

- Counts of measured wells and control roles; missing positions remain unmeasured.
- Z-prime: `1 - 3*(sample_SD_positive + sample_SD_negative)/abs(mean_positive - mean_negative)`. Requires at least two wells of each control role. Equal control means make it undefined. Multiple control IDs within either role cause the pooled score to be withheld. The displayed 0.5 reference is exploratory and not a universal acceptance threshold.
- Whether each sample ID spans edge and interior positions. An edge is row A/H or column 1/12.
- An equal-weight mean of within-ID edge-minus-interior contrasts for IDs represented in both zones, including controls. No pooled position comparison is substituted when matching is impossible.
- Separate control-only, within-ID edge/interior comparisons, so candidate sample responses do not drive the control check.
- Per-ID means and sample standard deviations within each position zone, with referenced wells. A single well has no estimable SD; it is not displayed as zero. Small groups still give uncertain variability estimates.
- Sample IDs lacking within-plate replication.

These descriptive checks do not establish a causal artifact, biological activity, statistical significance, or assay validity. No measurements are corrected and no hits are ranked.

## Follow-up layout

Each selected sample receives two edge and two interior wells. Each of two control roles receives the same allocation. Required wells: `4 × selected samples + 8`. Layouts use deterministic seeded randomization within position strata, reject insufficient budgets, and enforce unique plate positions. At most 16 samples fit this design because a 96-well plate has 36 edge wells. Unused budget is reported. This checks an edge/interior hypothesis; it does not balance every row, column, batch, or biological factor. Confirm controls, sample compatibility, handling, and biological replication independently.

## Nebius / NVIDIA integration

The user chooses the sample IDs; none are preselected. Follow-up designs require a measured negative and positive control identity selected from the input. Generic control names are not substituted. The randomization seed is visible and editable.

## Failure handling and traceability

The API distinguishes malformed or oversized uploads, missing control selections, impossible budgets, unsupported inputs, provider authorization/credit issues, rate limits, timeouts, invalid model output, and unexpected failures. Errors include a recovery message, stable code, retryability, and a request reference. Responses never expose provider error bodies or credentials. Closed browser connections are handled; concurrent requests and model work are bounded. No provider request is automatically retried, to avoid hidden duplicate usage. Browser input and local results remain available after a model failure.

Reports include a version and content-derived identifier; layouts reference their source report. Suggested next actions link to reported findings and retain the scientist’s authority over assay acceptance. See [design decisions](docs/design-decisions.md). Public hosting remains unfinished.

## Local credentials and hosted serving

Use `python3 setup_nebius.py` for hidden local key entry; do not paste a key into chat or GitHub. The helper stores `.env.local` with user-only permissions. Local `server.py` and `verify_nebius.py` load it explicitly, while existing process environment variables take precedence. Production `serve.py` uses deployment environment secrets and does not load the local file. See [secure setup](docs/secure-setup.md).

A separate WSGI gateway and hash-pinned Waitress launcher are available for a managed HTTPS environment. They share the local app’s business routes, enforce an exact configured origin/host, reject cross-origin requests and unsupported methods, and cap incoming work. Actual Waitress HTTP serving has been checked on loopback. No public host has been deployed, and the Docker image has not been built in this environment. See [deployment instructions](docs/deployment.md).

## Model configuration

Configure the server environment with `NEBIUS_API_KEY` and `NEBIUS_MODEL`. Use an NVIDIA Nemotron model currently available to your Token Factory account. Do not put credentials in files committed to GitHub or paste them into the browser.

The server contacts `https://api.tokenfactory.nebius.com/v1/chat/completions` only after the researcher requests a review. Each completed review uses two inference calls. A process-lifetime allowance defaults to 100 inference attempts (`SECOND_LOOK_MAX_MODEL_CALLS`); failures also consume this allowance. This is not a monetary cap and resets when the process restarts. Configure an account-level provider budget separately before public hosting. First, the model requests one or two whitelisted, read-only analyses appropriate to the chosen objective: selected control-pair separation, selected sample measurements by position, or follow-up feasibility. Deterministic code checks the scope and computes the evidence. Second, the model selects existing findings, computed evidence IDs, and an allowed next step. Unsupported tools, substituted materials, unselected samples, duplicated calls, unrelated analyses, and invented references are rejected. Numbers and scientific explanations come from deterministic code. The model cannot alter the data, choose new follow-up samples, approve a layout, or run code. Changing selections or objective clears the previous review.

This workflow has been tested with scripted model responses. Live NVIDIA/Nebius compatibility and model quality remain unverified. To perform an explicit synthetic-only check after configuration, run `python3 verify_nebius.py --live-review --output docs/live-verification.json`. Without `--live-review`, the command only reports configuration state and makes no provider call. It exits with code 2 until a live review is verified. Provider usage may be charged; no inference request is automatically retried.

Unavailable or unconfigured model access is explicitly reported. It is never represented as a successful live review. No fallback provider is used.

## Portable review files

Review files contain the original measurements and notes. Saving is explicit; there is no automatic local storage or server persistence. Keep them in an approved location. Files use a versioned schema and are validated before download and when reopened. Imported calculations, model answers, and approval flags are not trusted: results are recomputed from the original CSV and layout approval starts over. Changed analysis versions or report fingerprints are disclosed. UTF-8 decoding is strict; unreadable files are rejected without replacing current work.

## Privacy and deployment

Uploads remain in request memory; application access logging is disabled. The browser holds the current CSV until replaced or the tab is closed. Optional live review sends the computed summary (including sample IDs and referenced wells) to Nebius. Use only data you are authorized to share. Exports remain the user's responsibility. No private research datasets are bundled.

The standard-library server is intended for local development. Before public hosting, provision a managed TLS gateway, set the exact public origin and environment secrets, configure account-level spending limits, verify the hosted routes and live inference, and maintain judge access. Production serving and application-level request/model limits are implemented, but public hosting remains unverified. A public demo must use synthetic examples by default. Do not expose this development server directly to the internet.

## External instrument-data case

[FlopR calibration case](examples/flopr-calibration/README.md) contains 48 real fluorescence measurements from a pinned public source, preserved exactly with upstream GPL-3.0 licensing and a reproducible importer. It checks real-data ingestion and correct abstention when assay-control roles are absent. This is not a biological validation benchmark, and the intentionally varying concentrations must not be mistaken for an artifact.

Outbound HTTPS uses certificate and hostname verification. On incomplete Python installations with no loaded roots and no explicit trust configuration, the transport may load the established OS CA bundle at `/etc/ssl/cert.pem`; it never disables verification.

## Scientific basis and prior work

Plate-level QC and position effects are established topics; this project does not invent normalization or QC. The intended contribution is a small, inspectable workflow connecting evidence limitations with a constrained follow-up design and a researcher-readable handoff.

- Systematic error detection in experimental high-throughput screening: https://pmc.ncbi.nlm.nih.gov/articles/PMC3034671/
- Statistical Methods for Analysis of High-Throughput RNA Interference Screens: https://pmc.ncbi.nlm.nih.gov/articles/PMC2789971/
- Existing assay analysis and QC product: https://www.genedata.com/platform/screener
- Nebius integration example: https://dev.nebius.com/cookbook/first-agent-on-nebius
- Hackathon requirements: https://nebiusglobalaihackathon.devpost.com/rules

## License

Second Look code and generated synthetic examples: MIT; see LICENSE. External FlopR data in `examples/flopr-calibration/` retains its upstream GPL-3.0 license and attribution; see that directory’s README and license.
