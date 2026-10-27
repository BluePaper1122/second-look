# Real calibration readings — compatibility case

This directory contains a **real instrument calibration dataset**, not synthetic observations and not a biological assay-validation benchmark.

## Source and attribution

Source: [UCL CSSB FlopR](https://github.com/ucl-cssb/flopr), commit `83d7b92c50a5e12ed692459e5d57d65d08c11665`, file `examples/plate_reader/tecan_spark/191219_calibration_membrane_parsed.csv`.

Project/publication authors: Alex J. H. Fedorec, Clare M. Robinson, Ke Yan Wen, and Chris P. Barnes. Background: [FlopR publication](https://doi.org/10.1021/acssynbio.0c00296), including its linked correction. No calibration or normalization algorithm from that work is reimplemented here.

The upstream repository is distributed under GPL-3.0. Its license is retained as `LICENSE.GPL-3.0`. The upstream observations and this reformatted data case retain those upstream terms; Second Look's MIT license does not replace them. `upstream_calibration.csv` preserves the exact pinned source bytes. Our independently written import/analysis code remains under the root license.

## Transformation

- Select only rows whose calibrant is fluorescein.
- Read the single `GFP 40` instrument channel without correction or normalization.
- Preserve finite numeric measurements; normalize well labels to zero-padded form.
- Identify material using the original calibrant, fluorophore, medium, and concentration fields. Concentration units are not inferred or converted.
- Label every imported row `sample`. The source calibration layout does not supply the biological assay-control roles required by Second Look. Neither the largest signal nor a blank is silently assigned as an assay positive or negative control.

`plate.csv` contains 48 measured wells and 12 material IDs. The other calibrant's 48 rows are excluded from this single-channel case, not replaced with zero. The source intentionally varies concentration across columns.

## What was checked

Source measurements match exactly after reformatting. The app calculates descriptive position comparisons for ten material IDs measured in both zones and identifies two IDs confined to one zone. It discloses absent assay controls and withholds Z-prime. Follow-up planning requires identified assay controls, so this case should not produce an executable biological follow-up.

These are compatibility and abstention checks. They do **not** show a causal edge effect, false-positive rate, biological validity, or live-model quality. The planned concentration gradient is not evidence of an experimental artifact. A domain-reviewed real biological assay benchmark is still required for stronger claims.

Reproduce with `python3 scripts/import_flopr_calibration.py`. The importer verifies both source files against pinned Git blob hashes before generating output. See `provenance.json` for exact source links, hashes, selection rules, omitted rows, and checks.
