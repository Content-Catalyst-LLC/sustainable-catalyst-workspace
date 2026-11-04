"""PB05 isolated test: secret-free TLS-bytes TCP forwarder."""
import os
import select
import socket
import socketserver

UPSTREAM_HOST = "pb05-app"
UPSTREAM_PORT = 8443
LISTEN_PORT = 8443


class StreamForwarder(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            with socket.create_connection((UPSTREAM_HOST, UPSTREAM_PORT), timeout=5) as upstream:
                self.request.settimeout(None)
                upstream.settimeout(None)
                sockets = (self.request, upstream)
                while True:
                    ready, _, _ = select.select(sockets, [], [], 120)
                    if not ready:
                        break
                    for inbound in ready:
                        data = inbound.recv(65536)
                        if not data:
                            return
                        outgoing = upstream if inbound is self.request else self.request
                        outgoing.sendall(data)
        except (OSError, TimeoutError):
            return


class LimitedForwardServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 32


def serve():
    if os.environ.get("PB05_PROXY_ENABLED") != "ISOLATED_TEST_ONLY":
        raise RuntimeError("PB05 TCP proxy may only run in isolated staging")
    with LimitedForwardServer(("0.0.0.0", LISTEN_PORT), StreamForwarder) as server:
        print("PB05_PROXY_TCP_READY=YES", flush=True)
        server.serve_forever(poll_interval=0.3)


if __name__ == "__main__":
    serve()
