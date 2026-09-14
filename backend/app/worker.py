import os
import signal
import socket
import time
from uuid import uuid4

from .config import get_settings
from .db import initialize_schema, session_scope
from .jobs import block_job, claim_next_job, complete_job, fail_or_requeue_job, update_heartbeat
from .routing import RemoteExecutionError, RouteBlocked, execute_job

RUNNING = True


def _stop(*_args):
    global RUNNING
    RUNNING = False


def worker_id() -> str:
    return os.getenv("SC_WORKSPACE_WORKER_ID", "").strip() or f"{socket.gethostname()}-{uuid4().hex[:8]}"


def main():
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    settings = get_settings()
    initialize_schema()
    wid = worker_id()
    print(f"Workspace worker {wid} starting for backend {settings.service_version}.", flush=True)

    last_heartbeat = 0.0
    while RUNNING:
        now = time.monotonic()
        if now - last_heartbeat >= settings.worker_heartbeat_seconds:
            with session_scope() as db:
                update_heartbeat(db, wid, settings.service_version, "idle", "")
            last_heartbeat = now

        with session_scope() as db:
            row = claim_next_job(db, wid)
        if row is None:
            time.sleep(settings.worker_poll_seconds)
            continue

        with session_scope() as db:
            update_heartbeat(db, wid, settings.service_version, "running", row.job_id)
        try:
            with session_scope() as db:
                result = execute_job(db, row)
            with session_scope() as db:
                complete_job(db, row, result)
        except RouteBlocked as exc:
            with session_scope() as db:
                block_job(db, row, "route-unconfigured", str(exc))
        except RemoteExecutionError as exc:
            with session_scope() as db:
                fail_or_requeue_job(db, row, "remote-execution-error", str(exc))
        except Exception as exc:
            with session_scope() as db:
                fail_or_requeue_job(db, row, "worker-exception", f"{exc.__class__.__name__}: {exc}")
        finally:
            with session_scope() as db:
                update_heartbeat(db, wid, settings.service_version, "idle", "")

    with session_scope() as db:
        update_heartbeat(db, wid, settings.service_version, "stopped", "")
    print(f"Workspace worker {wid} stopped.", flush=True)


if __name__ == "__main__":
    main()
