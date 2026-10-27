"""Explicit local-only credential loading; process environment takes precedence."""
import os
from pathlib import Path
import shlex
import stat

ROOT=Path(__file__).resolve().parent
ALLOWED={'NEBIUS_API_KEY','NEBIUS_MODEL'}


def load_local_configuration(path=None):
    path=Path(path) if path else ROOT/'.env.local'
    try:fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    except FileNotFoundError:return False
    try:
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size>8192:
            raise ValueError('The local configuration must be a regular file smaller than 8 KB.')
        if info.st_mode & 0o077:
            raise ValueError('The local configuration is accessible to other users. Set its permissions to 600 before loading it.')
        if hasattr(os,'getuid') and info.st_uid!=os.getuid():
            raise ValueError('The local configuration must belong to the user running the application.')
        with os.fdopen(fd,encoding='utf-8') as source:
            fd=None
            text=source.read(8193)
    finally:
        if fd is not None:os.close(fd)
    values={}
    for line in text.splitlines():
        line=line.strip()
        if not line or line.startswith('#'):continue
        key,sep,value=line.partition('=')
        if not sep or key not in ALLOWED or key in values:
            raise ValueError('The local configuration has unsupported or repeated fields. Run the setup helper again.')
        try:parts=shlex.split(value,posix=True)
        except ValueError:raise ValueError('The local configuration has an unreadable value. Run the setup helper again.') from None
        if len(parts)!=1 or not parts[0] or any(ord(c)<32 for c in parts[0]):
            raise ValueError('The local configuration contains an empty or unsupported value.')
        values[key]=parts[0]
    if set(values)!=ALLOWED or not values['NEBIUS_MODEL'].lower().startswith('nvidia/'):
        raise ValueError('Configure both the Nebius key and an available NVIDIA model ID.')
    for key,value in values.items():os.environ.setdefault(key,value)
    return True
