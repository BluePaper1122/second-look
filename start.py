"""Friendly local entry point. No installation, model calls or private-file scan."""
import argparse
import sys


def main():
    parser=argparse.ArgumentParser(description='Start Second Look locally and open its plate-review page. Keep this terminal open while reviewing.')
    parser.add_argument('--port',type=int,help='Use another local port if 8765 is occupied (1–65535).')
    parser.add_argument('--no-browser',action='store_true',help='Print the address without opening a browser.')
    args=parser.parse_args()
    if sys.version_info < (3,11):
        parser.error('Second Look requires Python 3.11 or newer. Run it with a supported Python installation.')
    if args.port is not None and not 1 <= args.port <= 65535:
        parser.error('Choose a port from 1 to 65535, for example: python3 start.py --port 8766')
    from server import main as serve_local
    serve_local(open_browser=not args.no_browser,port_override=args.port)


if __name__=='__main__':main()
