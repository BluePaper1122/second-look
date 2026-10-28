# First run: about five minutes

1. Open a terminal in the `second-look` folder. You need Python 3.11 or newer; the local app needs no package installation.
2. Run `python3 start.py`. It opens the local app in your default browser. Keep the terminal open; Control+C stops the app. If the browser does not open, use the printed address.
3. Leave **Confounded sample layout** selected, click **Load selected example**, then **Inspect this plate**. This uses synthetic measurements and needs no key or account.
4. Read **Sample identity and position may be entangled**. Expand its supporting measurements. Select a well to see its exact value; an unmeasured position is not zero.
5. Select both candidate samples under follow-up design. Keep the measured control materials, budget 24, and seed 11. Click **Design follow-up**. The template should allocate 16 wells and leave eight unused.
6. Inspect the assignments and compatibility limitations. Only attest review if you have actually reviewed the proposal. Then export the CSV. A prepared-file link lets you retry if automatic saving is blocked.
7. Add any context to **Researcher notes**, then **Save review file** before closing the tab. The file includes original data and notes; store it appropriately. Reopening recalculates findings and resets approval. No account or silent server-side save is provided.

The optional model review is a separate step. It sends a computed QC summary, including sample IDs, to Nebius only when requested. Follow [secure setup](secure-setup.md) for live use. Local QC and planning work without it.

## If something goes wrong

| What you see | What to do |
|---|---|
| `python3` is not found, or Python is too old | Use an installed Python 3.11+ interpreter. The launcher does not install software for you. |
| Port is unavailable | Run `python3 start.py --port 8766`. It does not terminate another program. |
| Browser does not open | Copy the printed localhost address into your browser, or use `--no-browser` intentionally. |
| App becomes unreachable | Keep the tab open, restart the server, then retry. Browser input remains until replaced or the tab closes. |
| Missing controls | Check the original metadata. Do not invent roles based on signal size. Inspection remains available; allocation is blocked. |
| Too many samples for the budget | Reduce your selection or deliberately increase the well budget. The app does not choose samples for you. |
| Model is unavailable | Continue with deterministic findings. Check local setup separately; no automatic inference retries occur. |
| Export did not start | Use the named link in **Prepared export**. Verify the filename and contents before use. |

This is exploratory single-plate research software. The initial layout is a specific position-check template, not a biological replication or power calculation. A researcher responsible for the assay must decide whether it is appropriate.
