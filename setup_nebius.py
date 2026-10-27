"""Interactive local credential entry. No secrets in command-line arguments or logs."""
import getpass
import os
from pathlib import Path
import shlex
import tempfile
import warnings

ROOT=Path(__file__).resolve().parent


def main():
    print('Configure local Nebius access. Enter the key here, not in chat or GitHub.')
    print('It will be stored as plaintext in .env.local, readable only by your user. This file is excluded from Git and container builds.')
    target=ROOT/'.env.local'
    if target.exists() and input('Replace the existing local configuration? [y/N] ').strip().lower()!='y':
        print('No configuration was changed.')
        return 1
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error',getpass.GetPassWarning)
            key=getpass.getpass('Nebius Token Factory API key (hidden): ').strip()
        model=input('Available NVIDIA model ID from your Nebius catalog: ').strip()
    except getpass.GetPassWarning:
        print('Hidden key entry is not available here. Run this helper in an interactive terminal; nothing was saved.')
        return 1
    except (EOFError,KeyboardInterrupt):
        print('\nSetup cancelled. No configuration was saved.')
        return 1
    if not key or not key.isascii() or not key.isprintable() or len(key)>4096 or any(ord(c)<33 for c in key) or not model.isascii() or len(model)>200 or not model.lower().startswith('nvidia/') or any(ord(c)<33 for c in model):
        print('A nonempty key and a valid NVIDIA model ID are required. Nothing was saved.')
        return 1
    content='# Local credentials. Never commit or share this file.\n'+'NEBIUS_API_KEY='+shlex.quote(key)+'\n'+'NEBIUS_MODEL='+shlex.quote(model)+'\n'
    if len(content.encode('utf-8'))>8192:
        print('The configuration exceeds the supported size. Nothing was saved.')
        return 1
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',prefix='.env.local.',dir=ROOT,delete=False) as out:
            temporary=Path(out.name)
            os.fchmod(out.fileno(),0o600)
            out.write(content)
            out.flush();os.fsync(out.fileno())
        os.replace(temporary,target)
    except OSError:
        if temporary is not None:
            try:temporary.unlink(missing_ok=True)
            except OSError:pass
        print('The local configuration could not be saved. Check folder permissions; no key was printed.')
        return 1
    print('Saved locally. Configuration is not yet verified. Run python3 verify_nebius.py --live-review to test synthetic data only.')
    return 0

if __name__=='__main__':raise SystemExit(main())
