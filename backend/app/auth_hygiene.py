"""Authenticated-response hygiene (SC-AUTH-01 F3, retained by SC-AUTH-02).

Every Workspace API response is marked no-store so browsers and proxies never
retain private project data. The SC-AUTH-01 WordPress bridge assertion path
that previously lived here is removed: WordPress is not an identity source.
"""
from __future__ import annotations

class AuthHygieneMiddleware:
    """Pure ASGI: marks API responses no-store."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        path = scope.get("path", "")
        if not (path.startswith("/v1/") or path == "/v1" or path.startswith("/internal/")):
            return await self.app(scope, receive, send)

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = [(k, v) for k, v in message.get("headers", []) if k.lower() not in (b"cache-control", b"pragma")]
                headers += [(b"cache-control", b"no-store, private"), (b"pragma", b"no-cache")]
                vary = [v for k, v in headers if k.lower() == b"vary"]
                if not any(b"cookie" in v.lower() for v in vary):
                    headers.append((b"vary", b"Cookie, Authorization"))
                message = dict(message, headers=headers)
            await send(message)

        return await self.app(scope, receive, send_wrapper)
