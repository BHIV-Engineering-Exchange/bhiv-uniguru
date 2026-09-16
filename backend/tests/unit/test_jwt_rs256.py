"""
Unit tests — JWT RS256 Verifier & RBAC Enforcer
T-GOV-002
"""
from __future__ import annotations

import time
import uuid

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# ---------------------------------------------------------------------------
# Key generation helpers (test-only)
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


def _make_token(private_pem: str, payload: dict, algorithm: str = "RS256") -> str:
    import jwt as pyjwt
    return pyjwt.encode(payload, private_pem, algorithm=algorithm)


@pytest.fixture(scope="module")
def rsa_keypair():
    return _generate_rsa_keypair()


@pytest.fixture(scope="module")
def verifier(rsa_keypair):
    from security.jwt_rs256 import RS256Verifier
    _, public_pem = rsa_keypair
    return RS256Verifier(public_key_pem=public_pem)


def _valid_payload(extra: dict | None = None) -> dict:
    now = int(time.time())
    base = {
        "sub": "user-123",
        "role": "admin",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + 3600,
    }
    if extra:
        base.update(extra)
    return base


# ---------------------------------------------------------------------------
# RS256Verifier — happy path
# ---------------------------------------------------------------------------

def test_verify_valid_token_returns_claims(rsa_keypair, verifier):
    private_pem, _ = rsa_keypair
    token = _make_token(private_pem, _valid_payload())
    claims = verifier.verify(token)
    assert claims.sub == "user-123"
    assert claims.role == "admin"
    assert claims.jti != ""


def test_verify_extracts_all_standard_claims(rsa_keypair, verifier):
    private_pem, _ = rsa_keypair
    payload = _valid_payload({"iss": "uniguru-test", "aud": "bhiv"})
    _, public_pem = rsa_keypair
    from security.jwt_rs256 import RS256Verifier
    v = RS256Verifier(public_key_pem=public_pem, issuer="uniguru-test", audience="bhiv")
    token = _make_token(private_pem, payload)
    claims = v.verify(token)
    assert claims.iss == "uniguru-test"
    assert claims.aud == "bhiv"


def test_is_valid_returns_true_for_good_token(rsa_keypair, verifier):
    private_pem, _ = rsa_keypair
    token = _make_token(private_pem, _valid_payload())
    assert verifier.is_valid(token) is True


# ---------------------------------------------------------------------------
# RS256Verifier — failure cases
# ---------------------------------------------------------------------------

def test_verify_expired_token_raises(rsa_keypair, verifier):
    private_pem, _ = rsa_keypair
    now = int(time.time())
    payload = _valid_payload({"iat": now - 7200, "exp": now - 3600})
    token = _make_token(private_pem, payload)
    with pytest.raises(PermissionError, match="expired"):
        verifier.verify(token)


def test_verify_wrong_algorithm_raises(rsa_keypair, verifier):
    private_pem, _ = rsa_keypair
    token = _make_token(private_pem, _valid_payload(), algorithm="RS384")
    with pytest.raises(PermissionError):
        verifier.verify(token)


def test_verify_tampered_signature_raises(rsa_keypair, verifier):
    private_pem, _ = rsa_keypair
    token = _make_token(private_pem, _valid_payload())
    # Corrupt the signature (last segment)
    parts = token.split(".")
    parts[-1] = parts[-1][:-4] + "XXXX"
    bad_token = ".".join(parts)
    with pytest.raises(PermissionError):
        verifier.verify(bad_token)


def test_verify_wrong_key_raises():
    from security.jwt_rs256 import RS256Verifier
    priv1, _ = _generate_rsa_keypair()
    _, pub2 = _generate_rsa_keypair()
    token = _make_token(priv1, _valid_payload())
    verifier2 = RS256Verifier(public_key_pem=pub2)
    with pytest.raises(PermissionError):
        verifier2.verify(token)


def test_verify_missing_required_claim_raises(rsa_keypair, verifier):
    private_pem, _ = rsa_keypair
    now = int(time.time())
    # Missing 'role'
    payload = {"sub": "u1", "jti": str(uuid.uuid4()), "iat": now, "exp": now + 3600}
    token = _make_token(private_pem, payload)
    with pytest.raises(PermissionError):
        verifier.verify(token)


def test_is_valid_returns_false_for_bad_token(verifier):
    assert verifier.is_valid("not.a.token") is False


def test_invalid_public_key_raises_on_construction():
    from security.jwt_rs256 import RS256Verifier
    with pytest.raises(ValueError, match="Invalid RSA public key"):
        RS256Verifier(public_key_pem="not-a-pem")


# ---------------------------------------------------------------------------
# RBACEnforcer
# ---------------------------------------------------------------------------

def _claims(role: str) -> object:
    from security.jwt_rs256 import JWTClaims
    now = int(time.time())
    return JWTClaims(sub="u1", role=role, jti="j1", iat=now, exp=now + 3600)


def test_rbac_enforcer_allows_matching_role():
    from security.jwt_rs256 import RBACEnforcer
    enforcer = RBACEnforcer(required_roles={"admin"})
    enforcer.enforce(_claims("admin"))  # must not raise


def test_rbac_enforcer_rejects_wrong_role():
    from security.jwt_rs256 import RBACEnforcer
    enforcer = RBACEnforcer(required_roles={"admin"})
    with pytest.raises(PermissionError):
        enforcer.enforce(_claims("viewer"))


def test_rbac_enforcer_min_role_allows_higher():
    from security.jwt_rs256 import RBACEnforcer
    enforcer = RBACEnforcer(min_role="operator")
    enforcer.enforce(_claims("admin"))  # admin > operator


def test_rbac_enforcer_min_role_rejects_lower():
    from security.jwt_rs256 import RBACEnforcer
    enforcer = RBACEnforcer(min_role="operator")
    with pytest.raises(PermissionError):
        enforcer.enforce(_claims("viewer"))


def test_rbac_is_authorized_returns_bool():
    from security.jwt_rs256 import RBACEnforcer
    enforcer = RBACEnforcer(required_roles={"superadmin"})
    assert enforcer.is_authorized(_claims("admin")) is False
    assert enforcer.is_authorized(_claims("superadmin")) is True


def test_rbac_unknown_role_treated_as_lowest():
    from security.jwt_rs256 import RBACEnforcer
    enforcer = RBACEnforcer(min_role="viewer")
    with pytest.raises(PermissionError):
        enforcer.enforce(_claims("unknown_role"))
