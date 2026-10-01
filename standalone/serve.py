#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse
import os

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

def main():
    parser = argparse.ArgumentParser(description="Serve Sustainable Catalyst Workspace standalone shell.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    os.chdir(root)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Workspace standalone v3.46.10.0: http://{args.host}:{args.port}")
    server.serve_forever()

if __name__ == "__main__":
    main()
