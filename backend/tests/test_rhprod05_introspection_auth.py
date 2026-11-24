"""Private introspection request/response authentication: no bearer secret on wire."""
import pytest
from fastapi import HTTPException

from app.research_bridge_proof import (
    request_proof, response_proof, verify_request, verify_response,
)
from app.research_session_introspection import verify_service_proof

KEY = "synthetic-independent-research-service-proof-" + "x" * 32
NONCE = "a" * 64
PAYLOAD = {
    "schema_version": "rh-prod-05.1/1.0",
    "project_id": None,
    "session_token": "synthetic-not-a-real-cookie",
}


def test_private_introspection_requires_dedicated_secret():
    with pytest.raises(HTTPException) as err:
        verify_service_proof(NONCE, request_proof(KEY, NONCE, PAYLOAD), PAYLOAD, expected="")
    assert err.value.status_code == 503


def test_request_proof_is_exact_and_required():
    valid = request_proof(KEY, NONCE, PAYLOAD)
    assert verify_service_proof(NONCE, valid, PAYLOAD, expected=KEY) is None
    for nonce, proof in ((NONCE, None), (NONCE, "0" * 64), ("x" * 64, valid),
                         ("b" * 64, valid), (None, valid)):
        with pytest.raises(HTTPException) as error:
            verify_service_proof(nonce, proof, PAYLOAD, expected=KEY)
        assert error.value.status_code == 401


def test_proof_binds_session_token_and_project_grant():
    proof = request_proof(KEY, NONCE, PAYLOAD)
    for changed in (
        dict(PAYLOAD, session_token="replayed-another-cookie"),
        dict(PAYLOAD, project_id="other-project"),
    ):
        assert not verify_request(KEY, NONCE, changed, proof)


def test_response_proof_has_separate_domain_and_nonce_binding():
    result = {"active": True, "authorized_projects": ["project-a"]}
    proof = response_proof(KEY, NONCE, result)
    assert verify_response(KEY, NONCE, result, proof)
    assert not verify_response(KEY, "b" * 64, result, proof)
    assert not verify_response(KEY, NONCE, {"active": True, "authorized_projects": ["project-b"]}, proof)
    assert not verify_response(KEY, NONCE, result, request_proof(KEY, NONCE, result))


def test_protocol_does_not_transmit_reusable_bearer_secret():
    proof = request_proof(KEY, NONCE, PAYLOAD)
    assert KEY not in proof
    assert len(proof) == 64
