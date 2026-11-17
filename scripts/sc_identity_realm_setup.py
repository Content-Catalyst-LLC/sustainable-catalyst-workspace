#!/usr/bin/env python3
"""SC-PUB-REVIEW-01: configure a Sustainable Catalyst Identity realm (Keycloak admin REST API). Prints no secrets.

The production form of the SC-AUTH-02 staging realm (realm_setup.py + reset_flow_setup.py, accepted in staging):

* no self-registration; accounts exist only by invitation (sc_identity_invite_reviewer.py);
* password policy, brute-force protection, short token and session lifetimes;
* TOTP is a default required action, and the browser flow always asks for it (no password-only path);
* recovery by e-mail requires the enrolled TOTP before a new password and never resets the second factor;
* one confidential client for Workspace: authorization code + PKCE S256 only, exact redirect URIs,
  back-channel logout, and an ``amr`` claim so Workspace can verify the second factor;
* SMTP from an operator-supplied JSON file (host, port, from, fromDisplayName, user, password, starttls, ssl).

Idempotent: re-running converges the realm and client to this configuration and creates nothing twice.

    python3 -I sc_identity_realm_setup.py --idp http://127.0.0.1:PORT --realm sc --admin-user ADMIN \
        --admin-password-file FILE --client-secret-file FILE --smtp-file FILE \
        --workspace-origin https://WORKSPACE-HOST --backchannel-logout-url http://BACKEND:8089/v1/auth/backchannel-logout
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BROWSER_FLOW = "sc-browser-mfa"
RESET_FLOW = "sc-reset-mfa"


class Admin:
    def __init__(self, base, user, password):
        self.base = base.rstrip("/")
        code, js = self.call("POST", "/realms/master/protocol/openid-connect/token", form={
            "grant_type": "password", "client_id": "admin-cli", "username": user, "password": password})
        if code != 200:
            raise SystemExit(f"admin sign-in refused ({code})")
        self.token = js["access_token"]

    def call(self, method, path, body=None, form=None):
        headers = {"Accept": "application/json"}
        data = None
        if getattr(self, "token", None):
            headers["Authorization"] = f"Bearer {self.token}"
        if form is not None:
            data, headers["Content-Type"] = urllib.parse.urlencode(form).encode(), "application/x-www-form-urlencoded"
        elif body is not None:
            data, headers["Content-Type"] = json.dumps(body).encode(), "application/json"
        req = urllib.request.Request(self.base + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as e:
            return e.code, None


def ok(code, what, allowed=(200, 201, 204, 409)):
    if code not in allowed:
        raise SystemExit(f"NO-GO {what}: HTTP {code}")
    print(f"ok {what} ({code})")


def read(path):
    with open(path) as fh:
        return fh.read().strip()


def main(argv=None):
    p = argparse.ArgumentParser(prog="sc_identity_realm_setup")
    p.add_argument("--idp", required=True)
    p.add_argument("--realm", required=True)
    p.add_argument("--display-name", default="Sustainable Catalyst Identity")
    p.add_argument("--admin-user", required=True)
    p.add_argument("--admin-password-file", required=True)
    p.add_argument("--client-id", default="sc-workspace")
    p.add_argument("--client-secret-file", required=True)
    p.add_argument("--smtp-file", required=True, help="JSON: host, port, from, fromDisplayName, user, password, starttls, ssl")
    p.add_argument("--workspace-origin", required=True, help="public Workspace origin, e.g. https://workspace.example.org")
    p.add_argument("--backchannel-logout-url", required=True)
    a = p.parse_args(argv)
    origin = a.workspace_origin.rstrip("/")
    if not origin.startswith("https://") and not origin.startswith("http://"):
        raise SystemExit("workspace origin must be an http(s) origin")
    smtp = json.loads(read(a.smtp_file))
    adm = Admin(a.idp, a.admin_user, read(a.admin_password_file))
    R = f"/admin/realms/{urllib.parse.quote(a.realm, safe='')}"

    realm = {
        "realm": a.realm, "enabled": True, "displayName": a.display_name,
        "sslRequired": "external", "registrationAllowed": False, "resetPasswordAllowed": True,
        "rememberMe": False, "loginWithEmailAllowed": True, "duplicateEmailsAllowed": False, "editUsernameAllowed": False,
        "verifyEmail": True, "bruteForceProtected": True, "failureFactor": 5, "permanentLockout": False,
        "maxFailureWaitSeconds": 900, "waitIncrementSeconds": 60, "quickLoginCheckMilliSeconds": 1000,
        "minimumQuickLoginWaitSeconds": 60,
        "passwordPolicy": "length(12) and notUsername and notEmail and passwordHistory(3)",
        "accessTokenLifespan": 300, "ssoSessionIdleTimeout": 1800, "ssoSessionMaxLifespan": 28800,
        "accessCodeLifespan": 60, "accessCodeLifespanLogin": 600, "actionTokenGeneratedByUserLifespan": 900,
        "revokeRefreshToken": True, "refreshTokenMaxReuse": 0,
        "otpPolicyType": "totp", "otpPolicyAlgorithm": "HmacSHA1", "otpPolicyDigits": 6, "otpPolicyPeriod": 30,
        "otpPolicyLookAheadWindow": 1,
        "smtpServer": {"host": str(smtp["host"]), "port": str(smtp["port"]), "from": smtp["from"],
                       "fromDisplayName": smtp.get("fromDisplayName", a.display_name),
                       "auth": "true" if smtp.get("user") else "false", "user": smtp.get("user", ""),
                       "password": smtp.get("password", ""), "starttls": str(bool(smtp.get("starttls", True))).lower(),
                       "ssl": str(bool(smtp.get("ssl", False))).lower()},
        "eventsEnabled": True, "adminEventsEnabled": True, "adminEventsDetailsEnabled": False,
        "internationalizationEnabled": False,
    }
    code, _ = adm.call("POST", "/admin/realms", realm)
    if code == 409:
        code, _ = adm.call("PUT", R, realm)
    ok(code, f"realm {a.realm}")

    ok(adm.call("PUT", f"{R}/authentication/required-actions/CONFIGURE_TOTP", {
        "alias": "CONFIGURE_TOTP", "name": "Configure OTP", "providerId": "CONFIGURE_TOTP", "enabled": True,
        "defaultAction": True, "priority": 10, "config": {}})[0], "CONFIGURE_TOTP default required action")

    # Browser flow: the stock flow with OTP made unconditional (no password-only path), WebAuthn/recovery codes off.
    ok(adm.call("POST", f"{R}/authentication/flows/browser/copy", {"newName": BROWSER_FLOW})[0], "copy browser flow")
    _, execs = adm.call("GET", f"{R}/authentication/flows/{BROWSER_FLOW}/executions")
    for ex in execs:
        name = ex.get("displayName", "")
        if ex.get("providerId") == "conditional-user-configured" or name.endswith("Condition - user configured"):
            want = "DISABLED"
        elif "Conditional OTP" in name or "Conditional 2FA" in name or ex.get("providerId") == "auth-otp-form":
            want = "REQUIRED"
        elif ex.get("providerId") in ("webauthn-authenticator", "auth-recovery-authn-code-form"):
            want = "DISABLED"
        else:
            continue
        if ex.get("requirement") != want:
            ex["requirement"] = want
            ok(adm.call("PUT", f"{R}/authentication/flows/{BROWSER_FLOW}/executions", ex)[0], f"{name} -> {want}")

    # Recovery: e-mail link -> enrolled OTP -> new password; the conditional "Reset OTP" is disabled.
    q = urllib.parse.quote(RESET_FLOW)
    ok(adm.call("POST", f"{R}/authentication/flows/reset%20credentials/copy", {"newName": RESET_FLOW})[0], "copy reset flow")
    _, execs = adm.call("GET", f"{R}/authentication/flows/{q}/executions")
    if not any(e.get("providerId") == "auth-otp-form" for e in execs):
        ok(adm.call("POST", f"{R}/authentication/flows/{q}/executions/execution", {"provider": "auth-otp-form"})[0],
           "add OTP form to recovery")
    _, execs = adm.call("GET", f"{R}/authentication/flows/{q}/executions")
    for e in execs:
        if e.get("providerId") == "auth-otp-form" and e["requirement"] != "REQUIRED":
            e["requirement"] = "REQUIRED"
            ok(adm.call("PUT", f"{R}/authentication/flows/{q}/executions", e)[0], "recovery OTP REQUIRED")
        if e.get("level") == 0 and e.get("displayName", "").endswith("Conditional OTP") and e["requirement"] != "DISABLED":
            e["requirement"] = "DISABLED"
            ok(adm.call("PUT", f"{R}/authentication/flows/{q}/executions", e)[0], "recovery Reset OTP DISABLED")
    for _ in range(8):
        _, execs = adm.call("GET", f"{R}/authentication/flows/{q}/executions")
        top = [e.get("providerId") for e in execs if e.get("level") == 0]
        if top.index("auth-otp-form") < top.index("reset-password"):
            break
        otp = next(e for e in execs if e.get("level") == 0 and e.get("providerId") == "auth-otp-form")
        adm.call("POST", f"{R}/authentication/executions/{otp['id']}/raise-priority")
    else:
        raise SystemExit("NO-GO recovery flow order")

    _, current = adm.call("GET", R)
    current.update({"browserFlow": BROWSER_FLOW, "resetCredentialsFlow": RESET_FLOW})
    ok(adm.call("PUT", R, current)[0], "bind browser and recovery flows")

    amr = {"name": "amr", "protocol": "openid-connect", "protocolMapper": "oidc-amr-mapper",
           "config": {"id.token.claim": "true", "access.token.claim": "true", "introspection.token.claim": "true"}}
    client = {
        "clientId": a.client_id, "name": "Sustainable Catalyst Workspace", "enabled": True, "protocol": "openid-connect",
        "publicClient": False, "clientAuthenticatorType": "client-secret", "secret": read(a.client_secret_file),
        "standardFlowEnabled": True, "implicitFlowEnabled": False, "directAccessGrantsEnabled": False,
        "serviceAccountsEnabled": False, "frontchannelLogout": False, "consentRequired": False,
        "redirectUris": [f"{origin}/v1/auth/callback"], "webOrigins": [origin], "rootUrl": origin,
        "attributes": {"pkce.code.challenge.method": "S256",
                       "post.logout.redirect.uris": f"{origin}/v1/private-research/login",
                       "backchannel.logout.url": a.backchannel_logout_url,
                       "backchannel.logout.session.required": "true",
                       "backchannel.logout.revoke.offline.tokens": "true"},
    }
    _, found = adm.call("GET", f"{R}/clients?clientId={urllib.parse.quote(a.client_id)}")
    if found:
        cid = found[0]["id"]
        ok(adm.call("PUT", f"{R}/clients/{cid}", {**found[0], **client})[0], f"client {a.client_id} updated")
    else:
        ok(adm.call("POST", f"{R}/clients", {**client, "protocolMappers": [amr]})[0], f"client {a.client_id} created")
        _, found = adm.call("GET", f"{R}/clients?clientId={urllib.parse.quote(a.client_id)}")
        cid = found[0]["id"]
    _, mappers = adm.call("GET", f"{R}/clients/{cid}/protocol-mappers/models")
    if not any(m.get("protocolMapper") == "oidc-amr-mapper" for m in mappers or []):
        ok(adm.call("POST", f"{R}/clients/{cid}/protocol-mappers/models", amr)[0], "amr claim mapper")

    # Verification of what was configured (no secrets).
    _, cur = adm.call("GET", R)
    _, execs = adm.call("GET", f"{R}/authentication/flows/{BROWSER_FLOW}/executions")
    otp_required = any(e.get("providerId") == "auth-otp-form" and e.get("requirement") == "REQUIRED" for e in execs)
    password_alternatives = [e.get("providerId") for e in execs if e.get("requirement") == "ALTERNATIVE"
                             and e.get("providerId") in ("webauthn-authenticator", "auth-recovery-authn-code-form")]
    _, c = adm.call("GET", f"{R}/clients/{cid}")
    _, mappers = adm.call("GET", f"{R}/clients/{cid}/protocol-mappers/models")
    code, meta = Admin.call(adm, "GET", f"/realms/{urllib.parse.quote(a.realm, safe='')}/.well-known/openid-configuration")
    summary = {
        "registrationAllowed": cur["registrationAllowed"], "verifyEmail": cur["verifyEmail"],
        "bruteForceProtected": cur["bruteForceProtected"], "browserFlow": cur["browserFlow"],
        "resetCredentialsFlow": cur["resetCredentialsFlow"], "otpRequired": otp_required,
        "otherLoginAlternatives": password_alternatives, "smtpHost": cur.get("smtpServer", {}).get("host"),
        "client": {"publicClient": c["publicClient"], "directAccessGrants": c["directAccessGrantsEnabled"],
                   "implicit": c["implicitFlowEnabled"], "redirectUris": c["redirectUris"],
                   "pkce": c["attributes"].get("pkce.code.challenge.method"),
                   "backchannelLogout": c["attributes"].get("backchannel.logout.url"),
                   "amrMapper": any(m.get("protocolMapper") == "oidc-amr-mapper" for m in mappers or [])},
        "issuer": (meta or {}).get("issuer"), "authorizationEndpoint": (meta or {}).get("authorization_endpoint"),
        "tokenEndpoint": (meta or {}).get("token_endpoint"),
    }
    print("SUMMARY " + json.dumps(summary))
    good = (not summary["registrationAllowed"] and summary["verifyEmail"] and summary["bruteForceProtected"]
            and otp_required and not password_alternatives and summary["client"]["pkce"] == "S256"
            and not summary["client"]["publicClient"] and not summary["client"]["directAccessGrants"]
            and summary["client"]["amrMapper"])
    print("REALM " + ("GO" if good else "NO-GO"))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
