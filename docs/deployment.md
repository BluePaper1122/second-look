# Hosted serving

**Render demo:** https://second-look-qz70.onrender.com/ — deployed October 28, 2026 initially from commit fcfd5c6, then updated to df55880. Native Python with hash-pinned Waitress, Free compute ($0/month selected), manual deployments, and `/api/status` health check. All 11 synthetic HTTPS smoke checks passed through the public gateway, including reviewed export contents and stale/unreviewed rejection. See `render-smoke.json`. No model key was configured and no inference call was made. The hosted-data notice in df55880 was verified in the public browser; all 11 HTTP checks passed again. Later documentation-only commits do not change the running code.

Free compute sleeps after inactivity and can have a cold-start delay. Render also imposes workspace usage quotas; the $0 compute selection is not a guarantee against all account-level overages. No paid compute plan was selected and no payment details were added. Keep usage within the account’s included allowances; review billing controls before enabling public model use. Uploaded example data is synthetic; hosted inspection sends CSVs to the Render app server, not solely the visitor’s device. Application logic holds it in request memory without intentional database storage; infrastructure data handling remains subject to Render’s policies.

The native-Python settings are recorded in `render.yaml`; the service was created manually in the authorized Render account. The server-supplied `RENDER_EXTERNAL_URL` supplies the exact public origin. Automatic deployment is off. Verify each manually deployed source revision, and keep judge access available. Live NVIDIA/Nebius verification, model usefulness, Docker execution, load testing, and biological validity remain unverified.

## Run the production server locally

Install the exact dependency in an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-production.txt
```

Set `SECOND_LOOK_PUBLIC_ORIGIN` to `http://127.0.0.1:8088` and `PORT` to `8088` for local verification, then run `.venv/bin/python serve.py`. It binds to loopback by default. Production serving deliberately uses process environment secrets and does not load `.env.local`.

Verify with `python3 scripts/smoke_http.py --url http://127.0.0.1:8088`. This uses generated synthetic data and makes no inference calls. It checks layout allocation, receives/parses reviewed CSV content and metadata, rejects unreviewed/stale exports, and verifies unreviewed handoff omission in addition to serving/origin checks. It does not exercise browser file-saving policy. The recorded local result is in `production-smoke.json`.

## Deployment requirements

Use a host that runs a persistent Python/WSGI process or the provided container behind a managed HTTPS gateway. The user selected Render and authorized deployment there. No paid compute plan was selected. Budget approval is required before any paid upgrade.

Set these environment values on that host:

| Setting | Purpose |
|---|---|
| `SECOND_LOOK_PUBLIC_ORIGIN` | Exact canonical HTTPS origin, such as `https://second-look.example`. No path or trailing slash. The example hostname is a placeholder. |
| `PORT` | The internal port assigned by the host, default 8080. |
| `SECOND_LOOK_BIND_HOST` | Usually `0.0.0.0` inside a private container; default loopback outside the image. |
| `NEBIUS_API_KEY`, `NEBIUS_MODEL` | Environment secrets for an available NVIDIA model on Nebius. Never build these into the image. |
| `SECOND_LOOK_MAX_MODEL_CALLS` | Inference-attempt allowance per process lifetime, default 100. Failed attempts count. A complete review normally uses two calls. |
| `SECOND_LOOK_REQUESTS_PER_MINUTE` | Deployment-wide POST-request limit, default 120. Read-only pages remain available when this limit is reached. |

The gateway must preserve the original Host header. Forwarded headers are not trusted to change the application's origin or client identity. The health endpoint requires that same configured Host header. Its response reports configuration state, not proof of live inference.

Waitress uses eight application threads, at most 64 connections, a 1.1 MB body limit, a 16 KB header limit, and timeouts. Input/output overflow thresholds exceed this app's supported payload sizes so normal requests do not spill assay content into temporary files. The app has two simultaneous inference slots and ten inference attempts per minute. The call allowance resets on process restart and applies independently to each replica; it is not durable account-wide billing protection. Use one process for the hackathon demo and configure provider-side monetary controls separately.

## Container

A `Dockerfile` and `.dockerignore` are provided. The image runs as a numeric non-root user; local secrets, portable review files, Git history, and caches are excluded. The external FlopR data and its license remain together. Docker is not installed in the current development environment, so the image is a prepared configuration rather than a verified build.

Build/test the image in the selected host's environment, set the real HTTPS origin and environment secrets, and keep the internal port behind that host's TLS gateway. Do not expose the development `server.py` publicly.

## Before calling the demo submission-ready

- Verify the public HTTPS URL, expected Host handling, body limits, and synthetic workflow through the actual managed gateway.
- Perform the live synthetic-only NVIDIA/Nebius check and record the model ID and evidence checks.
- Test the real UI's model-result rendering; scripted-response tests do not establish live model quality.
- Keep the URL and free judge access available through the judging period. Confirm current hackathon dates before submission.
- Provide the public repository, accurate limitations, and a public video under three minutes.

These deployment controls do not make the tool clinically validated, compliant with any particular regulation, or suitable for unapproved private datasets. The default demo should use the included clearly labeled examples.

Sources: [Waitress arguments](https://docs.pylonsproject.org/projects/waitress/en/stable/arguments.html), [Waitress release](https://pypi.org/project/waitress/3.0.2/). The standard-library local server remains a development convenience; hosted traffic uses the WSGI gateway.
