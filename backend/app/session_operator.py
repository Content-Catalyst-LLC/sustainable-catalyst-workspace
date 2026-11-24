"""SC-AUTH-01 G1 — restricted operator session revocation.

Host-only by design: there is no HTTP route. An operator with shell access to
the Workspace container runs, for example:

    python -m app.session_operator revoke-user --user-key 42 --actor ops:name --reason "lost device"
    python -m app.session_operator revoke-session --session-id <32 hex> --user-key 42 --actor ops:name --reason "..."
    python -m app.session_operator purge-expired
    python -m app.session_operator link-identity --issuer <iss> --subject <sub> --user-key 42 \
        --method verified-existing-owner --evidence-sha256 <hex> --actor ops:name --reason "..."
    python -m app.session_operator enroll-new --issuer <iss> --subject <sub> --actor ops:name --reason "..."
    python -m app.session_operator suspend-identity --issuer <iss> --subject <sub> --actor ops:name --reason "..."
    python -m app.session_operator list-links

revoke-user ends every Workspace session and Sustainable Catalyst access
token issued to the user up to now. Identity links (SC-AUTH-02) map a Platform
Core subject to an existing Workspace user_key without rekeying any project;
ambiguous links are refused. Every action is audited. Output never contains
tokens.
"""
from __future__ import annotations

import argparse
import json
import sys

from .config import get_settings
from .db import session_scope
from .migrate_security import require_schema
from sqlalchemy import text

from .session_revocation import (
    link_identity, purge_expired, revoke_session_id, revoke_user_sessions, suspend_identity,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="app.session_operator")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("revoke-user", "revoke-session"):
        p = sub.add_parser(name)
        p.add_argument("--user-key", required=True)
        p.add_argument("--actor", required=True)
        p.add_argument("--reason", required=True)
        if name == "revoke-session":
            p.add_argument("--session-id", required=True)
    sub.add_parser("purge-expired")
    for name in ("link-identity", "enroll-new", "suspend-identity"):
        p = sub.add_parser(name)
        p.add_argument("--issuer", required=True)
        p.add_argument("--subject", required=True)
        p.add_argument("--actor", required=True)
        p.add_argument("--reason", required=True)
        if name == "link-identity":
            p.add_argument("--user-key", required=True)
            p.add_argument("--method", required=True, choices=("verified-existing-owner",))
            p.add_argument("--evidence-sha256", required=True)
    sub.add_parser("list-links")
    args = parser.parse_args(argv)

    settings = get_settings()
    if not settings.session_revocation_enforced:
        print(json.dumps({"ok": False, "error": "session revocation is not enforced in this deployment"}))
        return 2
    require_schema()
    with session_scope() as db:
        try:
            if args.command == "revoke-user":
                revoke_user_sessions(db, args.user_key, actor=args.actor, reason=args.reason)
                result = {"ok": True, "action": "revoke-user", "userKey": args.user_key}
            elif args.command == "revoke-session":
                revoke_session_id(db, args.session_id, user_key=args.user_key, actor=args.actor,
                                  reason=args.reason, ttl_seconds=settings.session_ttl_seconds)
                result = {"ok": True, "action": "revoke-session", "userKey": args.user_key}
            elif args.command == "link-identity":
                outcome = link_identity(db, issuer=args.issuer, subject=args.subject, user_key=args.user_key,
                                        method=args.method, actor=args.actor, reason=args.reason,
                                        evidence_sha256=args.evidence_sha256)
                result = {"ok": True, "action": "link-identity", "userKey": args.user_key, "outcome": outcome}
            elif args.command == "enroll-new":
                # New accounts get a fresh, namespaced key; never an existing one.
                user_key = "sci:" + args.subject
                outcome = link_identity(db, issuer=args.issuer, subject=args.subject, user_key=user_key,
                                        method="new-enrollment", actor=args.actor, reason=args.reason)
                result = {"ok": True, "action": "enroll-new", "userKey": user_key, "outcome": outcome}
            elif args.command == "suspend-identity":
                user_key = suspend_identity(db, issuer=args.issuer, subject=args.subject,
                                            actor=args.actor, reason=args.reason)
                result = {"ok": True, "action": "suspend-identity", "userKey": user_key}
            elif args.command == "list-links":
                rows = db.execute(text(
                    "SELECT issuer, subject, user_key, status, link_method, created_at "
                    "FROM workspace_identity_links ORDER BY created_at")).all()
                result = {"ok": True, "action": "list-links", "links": [
                    {"issuer": r.issuer, "subject": r.subject, "userKey": r.user_key, "status": r.status,
                     "method": r.link_method, "createdAt": str(r.created_at)} for r in rows]}
            else:
                result = {"ok": True, "action": "purge-expired", "deleted": purge_expired(db)}
            db.commit()
        except ValueError as exc:
            db.rollback()
            print(json.dumps({"ok": False, "error": str(exc)}))
            return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
