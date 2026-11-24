"""Protocol compatibility fixture: both independent services must produce this proof.

The inputs are synthetic and are never production credentials or cookies.
"""
from app.research_bridge_proof import request_proof, response_proof, verify_request, verify_response

KEY = "synthetic-independent-research-service-proof-" + "x" * 32
NONCE = "a" * 64
REQUEST = {
    "schema_version": "rh-prod-05.1/1.0",
    "project_id": None,
    "session_token": "synthetic-not-a-real-cookie",
}
EXPECTED = "ea4d558271fa58b6039c2968d7b3578219da17c5fd0a24d07d2d7f939f58b6b6"


def test_shared_protocol_known_vector():
    assert request_proof(KEY, NONCE, REQUEST) == EXPECTED
    assert verify_request(KEY, NONCE, REQUEST, EXPECTED)
    assert not verify_request(KEY, NONCE, dict(REQUEST, project_id="other"), EXPECTED)


def test_response_proof_cannot_be_used_as_request_proof():
    result = {"authorized_projects": ["project-a"], "active": True}
    proof = response_proof(KEY, NONCE, result)
    assert verify_response(KEY, NONCE, result, proof)
    assert not verify_request(KEY, NONCE, result, proof)
    assert not verify_response(KEY, NONCE, {"authorized_projects": ["project-b"], "active": True}, proof)
