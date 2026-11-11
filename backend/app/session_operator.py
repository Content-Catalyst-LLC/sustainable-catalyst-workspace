"""SC-AUTH-01 G1 — restricted operator session revocation.

Host-only by design: there is no HTTP route. An operator with shell access to
the Workspace container runs, for example:

    python -m app.session_operator revoke-user --user-key 42 --actor ops:name --reason "lost device"
    python -m app.session_operator revoke-session --session-id <32 hex> --user-key 42 --actor ops:name --reason "..."
    python -m app.session_operator purge-expired

revoke-user ends every Workspace cookie session issued to the user up to now,
and every WordPress-bridge request from a WordPress session signed in up to
now. Every action is written to workspace_session_revocation_audit. Output
never contains tokens.
"""
from __future__ import annotations

import argparse
import json
import sys

from .config import get_settings
from .db import session_scope
from .migrate_security import require_schema
from .session_revocation import purge_expired, revoke_session_id, revoke_user_sessions


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
