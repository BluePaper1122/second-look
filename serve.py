"""Production WSGI launcher. A managed gateway must terminate public HTTPS."""
import os
from gateway import create_app


def main():
    try:
        from waitress import serve
    except ImportError:
        raise SystemExit('Install the pinned production requirements before running serve.py.') from None
    try:
        app=create_app()
        port=int(os.getenv('PORT','8080'))
        if not 1<=port<=65535:raise ValueError('PORT must be between 1 and 65535.')
    except ValueError as e:raise SystemExit(str(e)) from None
    serve(app,host=os.getenv('SECOND_LOOK_BIND_HOST','127.0.0.1'),port=port,
          threads=8,connection_limit=64,channel_timeout=60,cleanup_interval=10,
          max_request_body_size=1_100_000,max_request_header_size=16384,
          inbuf_overflow=2_000_000,outbuf_overflow=4_000_000,
          clear_untrusted_proxy_headers=True,ident='SecondLook')

if __name__=='__main__':main()
