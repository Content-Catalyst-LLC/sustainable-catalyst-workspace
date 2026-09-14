import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def iso(dt: datetime | None) -> str:
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def ordered_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=False, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def workspace_project_fingerprint(project: dict) -> str:
    # Compatibility with the existing browser/PHP sync fingerprint contract.
    copy = json.loads(json.dumps(project, ensure_ascii=False))
    copy["persistence"] = {
        "scope": "account-sync-copy",
        "syncState": "sync-head",
        "accountEligible": True,
        "serverStored": True,
    }
    copy["recentTools"] = []
    return hashlib.sha256(ordered_json_bytes(copy)).hexdigest()


def ordered_sha256_hex(value: Any) -> str:
    return hashlib.sha256(ordered_json_bytes(value)).hexdigest()
