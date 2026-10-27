# Configure Nebius locally

Live NVIDIA/Nebius verification is still required for the hackathon. A working local analysis report does not satisfy that requirement by itself.

1. In your [Nebius Token Factory account](https://tokenfactory.nebius.com/), create or select an API key and choose an NVIDIA Nemotron model currently available to that account. Credits and model access must be active. Do not send the key in this chat, email, or GitHub.
2. Open an interactive terminal in the project folder and run:

   ```sh
   python3 setup_nebius.py
   ```

   Enter the key at the hidden prompt and the exact model ID from your catalog. If hidden entry is unavailable, the helper stops rather than echoing the key.
3. The helper stores `.env.local` with user-only permissions. It is plaintext on your device, excluded from Git and container builds. Existing environment variables take precedence. The helper does not verify the key, make inference calls, or accept billing terms.
4. To verify using generated synthetic data only:

   ```sh
   python3 verify_nebius.py --live-review --output docs/live-verification.json
   ```

   A complete check makes two inference calls, which may consume credits. It never reads your uploaded assay files. A result is accepted only when the two stages and evidence checks succeed. Do not interpret successful inference as scientific validation.
5. Restart the local application with `python3 server.py`. For hosted deployment, put the key/model in the host's environment-secret settings instead; `serve.py` never reads `.env.local`.

If you prefer not to store the key in this folder, use secure process environment configuration instead. Do not put the key in a command-line argument, a screenshot, a review file, or a public repository. `.env.local` is never included in handoff/review exports. Account-level spending controls should be configured in Nebius before any public deployment; application call limits are not a monetary spending cap.

No key has been configured by the developer, and no successful live inference has been claimed. This guide is the remaining account-specific step the account owner must perform.
