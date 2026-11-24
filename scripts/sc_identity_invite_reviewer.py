#!/usr/bin/env python3
"""SC-PUB-REVIEW-01: invite one reviewer to Sustainable Catalyst Identity (Keycloak admin REST API).

Creates an account without any password for one named person and has Sustainable Catalyst Identity e-mail them a
single-use, time-limited invitation link. Following it, the reviewer verifies the address, chooses their own
password and enrols a TOTP second factor; nobody else ever sees either. Workspace access is a separate,
audited operator step (``python -m app.session_operator enroll-new``), and approval roles are a third,
owner-only step in Outputs & Publishing -> Reviewers.

    python3 -I sc_identity_invite_reviewer.py --idp http://127.0.0.1:PORT --realm REALM \
        --admin-password-file FILE --email person@example.org --first-name Ada --last-name Lovelace

Prints the new account's subject (Keycloak user id), username and e-mail; never a password or token.
Refuses an address or username that already has an account.
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

ACTIONS = ["VERIFY_EMAIL", "UPDATE_PASSWORD", "CONFIGURE_TOTP"]


def http(method, url, body=None, token=None, form=None):
    headers = {"Accept": "application/json"}
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if form is not None:
        data, headers["Content-Type"] = urllib.parse.urlencode(form).encode(), "application/x-www-form-urlencoded"
    elif body is not None:
        data, headers["Content-Type"] = json.dumps(body).encode(), "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else None), resp.headers
    except urllib.error.HTTPError as exc:
        return exc.code, None, exc.headers


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sc_identity_invite_reviewer")
    p.add_argument("--idp", required=True, help="Keycloak base URL reachable from this host, e.g. http://127.0.0.1:18980")
    p.add_argument("--realm", required=True)
    p.add_argument("--admin-user", default="sc-identity-admin")
    p.add_argument("--admin-password-file", required=True)
    p.add_argument("--email", required=True)
    p.add_argument("--first-name", required=True)
    p.add_argument("--last-name", required=True)
    p.add_argument("--username", default="")
    p.add_argument("--lifespan-hours", type=int, default=72, choices=range(1, 169), metavar="1-168")
    p.add_argument("--client-id", default="sc-workspace")
    p.add_argument("--redirect-uri", default="", help="where the reviewer lands after accepting (a client redirect URI)")
    a = p.parse_args(argv)
    email = a.email.strip().lower()
    if email.count("@") != 1 or any(c.isspace() for c in email):
        print(json.dumps({"ok": False, "error": "invalid e-mail address"}))
        return 2
    username = (a.username or email).strip().lower()
    with open(a.admin_password_file) as fh:
        password = fh.read().strip()
    idp = a.idp.rstrip("/")
    code, tok, _ = http("POST", f"{idp}/realms/master/protocol/openid-connect/token", form={
        "grant_type": "password", "client_id": "admin-cli", "username": a.admin_user, "password": password})
    password = None
    if code != 200:
        print(json.dumps({"ok": False, "error": f"admin sign-in refused ({code})"}))
        return 1
    token = tok["access_token"]
    base = f"{idp}/admin/realms/{urllib.parse.quote(a.realm, safe='')}"
    for key, value in (("email", email), ("username", username)):
        code, found, _ = http("GET", f"{base}/users?exact=true&{key}={urllib.parse.quote(value)}", token=token)
        if code != 200 or found:
            print(json.dumps({"ok": False, "error": f"an account with that {key} already exists" if found else f"lookup failed ({code})"}))
            return 1
    code, _, headers = http("POST", f"{base}/users", {
        "username": username, "email": email, "firstName": a.first_name.strip(), "lastName": a.last_name.strip(),
        "enabled": True, "emailVerified": False, "requiredActions": ACTIONS}, token)
    if code != 201:
        print(json.dumps({"ok": False, "error": f"account not created ({code})"}))
        return 1
    subject = headers["Location"].rstrip("/").rsplit("/", 1)[-1]
    q = {"lifespan": str(a.lifespan_hours * 3600), "client_id": a.client_id}
    if a.redirect_uri:
        q["redirect_uri"] = a.redirect_uri
    code, _, _ = http("PUT", f"{base}/users/{subject}/execute-actions-email?" + urllib.parse.urlencode(q), ACTIONS, token)
    sent = code == 204
    print(json.dumps({"ok": sent, "subject": subject, "username": username, "email": email, "actions": ACTIONS,
                      "invitationEmailed": sent, "lifespanHours": a.lifespan_hours,
                      **({} if sent else {"error": f"invitation e-mail not sent ({code}); the account stays unusable"})}))
    return 0 if sent else 1


if __name__ == "__main__":
    sys.exit(main())
