"""Verified TLS with an OS CA-bundle fallback for incomplete Python installs."""
import os
from pathlib import Path
import ssl


def tls_context():
    context=ssl.create_default_context()
    # Some macOS python.org installations have no default CA bundle until the
    # installer certificate step runs. Use the established OS bundle only when
    # Python has no roots and the user has not explicitly configured trust paths.
    if not context.get_ca_certs() and not os.getenv('SSL_CERT_FILE') and not os.getenv('SSL_CERT_DIR'):
        system_bundle=Path('/etc/ssl/cert.pem')
        if system_bundle.is_file():
            context.load_verify_locations(cafile=str(system_bundle))
    return context
