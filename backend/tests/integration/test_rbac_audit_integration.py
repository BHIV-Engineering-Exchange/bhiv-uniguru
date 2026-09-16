"""
Integration tests — RBAC + Replay + Audit end-to-end
T-GOV-002

Verifies that the three security components work together correctly:
  1. RS256 JWT is verified
  2. jti is consumed in the replay table (replay blocked on second use)
  3. Every decision is emitted to the immutable audit log
  4. The audit chain remains valid throughout
"""
from __future__ import annotations

import time
import uuid

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _generate_rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return private_pem, public_pem


def _make_token(private_pem: str, payload: dict) -> str:
    import jwt as pyjwt
    return pyjwt.encode(payload, private_pem, algorithm="RS256")


def _valid_payload(role: str = "admin", jti: str | None = None) -> dict:
    now = int(time.time())
    return {
        "sub": "user-integration",
        "role": role,
        "jti": jti or str(uuid.uuid4()),
        "iat": now,
        "exp": now + 3600,
    }


@pytest.fixture(scope="module")
def keypair():
    return _generate_rsa_keypair()


@pytest.fixture()
def security_stack(keypair, tmp_path):
    """Returns (verifier, rbac_enforcer, replay_table, audit_emitter)."""
    from security.jwt_rs256 import RS256Verifier, RBACEnforcer
    from security.replay_table import ReplayMitigationTable
    from security.audit_emitter import AuditEmitter

    _, public_pem = keypair
    verifier = RS256Verifier(public_key_pem=public_pem)
    enforcer = RBACEnforcer(required_roles={"admin", "superadmin"})
    replay = ReplayMitigationTable()
    audit = AuditEmitter(log_path=tmp_path / "audit_integration.jsonl")
    return verifier, enforcer, replay, audit


def _process_request(security_stack, token: str, resource: str = "/runtime/ecosystem/execute"):
    """Simulate a governed request: verify → RBAC → replay → audit."""
    verifier, enforcer, replay, audit = security_stack
    try:
        claims = verifier.verify(token)
    except PermissionError as exc:
        audit.emit(event="jwt_verification_failed", actor="unknown", resource=resource,
                   outcome="DENY", metadata={"reason": str(exc)})
        return {"allowed": False, "reason": str(exc)}

    try:
        enforcer.enforce(claims)
    except PermissionError as exc:
        audit.emit(event="rbac_denied", actor=claims.sub, resource=resource,
                   outcome="DENY", metadata={"role": claims.role, "reason": str(exc)})
        return {"allowed": False, "reason": str(exc)}

    if not replay.try_consume(claims.jti, exp=claims.exp):
        audit.emit(event="replay_blocked", actor=claims.sub, resource=resource,
                   outcome="DENY", metadata={"jti": claims.jti})
        return {"allowed": False, "reason": "replay_detected"}

    audit.emit(event="request_allowed", actor=claims.sub, resource=resource,
               outcome="ALLOW", metadata={"jti": claims.jti, "role": claims.role})
    return {"allowed": True, "sub": claims.sub, "role": claims.role}


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

def test_valid_admin_token_is_allowed(keypair, security_stack):
    private_pem, _ = keypair
    token = _make_token(private_pem, _valid_payload(role="admin"))
    result = _process_request(security_stack, token)
    assert result["allowed"] is True
    assert result["role"] == "admin"


def test_replay_of_same_token_is_blocked(keypair, security_stack):
    private_pem, _ = keypair
    jti = str(uuid.uuid4())
    token = _make_token(private_pem, _valid_payload(role="admin", jti=jti))
    r1 = _process_request(security_stack, token)
    r2 = _process_request(security_stack, token)
    assert r1["allowed"] is True
    assert r2["allowed"] is False
    assert r2["reason"] == "replay_detected"


def test_insufficient_role_is_denied(keypair, security_stack):
    private_pem, _ = keypair
    token = _make_token(private_pem, _valid_payload(role="viewer"))
    result = _process_request(security_stack, token)
    assert result["allowed"] is False
    assert "role" in result["reason"].lower() or "not in required" in result["reason"].lower()


def test_expired_token_is_denied(keypair, security_stack):
    private_pem, _ = keypair
    now = int(time.time())
    payload = _valid_payload()
    payload["iat"] = now - 7200
    payload["exp"] = now - 3600
    token = _make_token(private_pem, payload)
    result = _process_request(security_stack, token)
    assert result["allowed"] is False


def test_tampered_token_is_denied(keypair, security_stack):
    private_pem, _ = keypair
    token = _make_token(private_pem, _valid_payload())
    parts = token.split(".")
    parts[-1] = parts[-1][:-4] + "XXXX"
    bad_token = ".".join(parts)
    result = _process_request(security_stack, bad_token)
    assert result["allowed"] is False


def test_audit_chain_valid_after_mixed_outcomes(keypair, security_stack):
    private_pem, _ = keypair
    _, _, _, audit = security_stack

    # Allow
    _process_request(security_stack, _make_token(private_pem, _valid_payload(role="admin")))
    # Deny (viewer)
    _process_request(security_stack, _make_token(private_pem, _valid_payload(role="viewer")))
    # Deny (expired)
    now = int(time.time())
    expired = _valid_payload()
    expired["exp"] = now - 1
    _process_request(security_stack, _make_token(private_pem, expired))

    result = audit.verify_chain()
    assert result["valid"] is True


def test_audit_log_records_all_events(keypair, tmp_path):
    from security.jwt_rs256 import RS256Verifier, RBACEnforcer
    from security.replay_table import ReplayMitigationTable
    from security.audit_emitter import AuditEmitter

    private_pem, public_pem = keypair
    stack = (
        RS256Verifier(public_key_pem=public_pem),
        RBACEnforcer(required_roles={"admin"}),
        ReplayMitigationTable(),
        AuditEmitter(log_path=tmp_path / "audit_count.jsonl"),
    )
    _, _, _, audit = stack

    # 3 distinct requests
    for _ in range(3):
        _process_request(stack, _make_token(private_pem, _valid_payload(role="admin")))

    tail = audit.tail(10)
    assert len(tail) == 3
    assert all(e["outcome"] == "ALLOW" for e in tail)


def test_fifty_consecutive_runs_produce_identical_audit_hashes(keypair, tmp_path):
    """Determinism gate: 50 runs with fixed inputs must produce identical entry hashes."""
    from security.audit_emitter import AuditEntry

    fixed_ts = "2026-01-01T00:00:00Z"
    fixed_prev = "0" * 64
    hashes = set()
    for _ in range(50):
        entry = AuditEntry(
            seq=0,
            event="jwt_verified",
            actor="user-123",
            resource="/runtime/ecosystem/execute",
            outcome="ALLOW",
            metadata={"jti": "fixed-jti"},
            timestamp=fixed_ts,
            prev_hash=fixed_prev,
        )
        hashes.add(entry.entry_hash)
    assert len(hashes) == 1, "Non-deterministic entry_hash across 50 runs"
