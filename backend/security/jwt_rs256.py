"""
JWT RS256 Token Verification & RBAC Role Enforcement
T-GOV-002 — Enterprise Security Hardening

Verifies RS256-signed JWTs, extracts typed claims, and enforces role-based
access control without any HS256 fallback.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.exceptions import InvalidSignature
import jwt
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidAlgorithmError,
    InvalidAudienceError,
    InvalidIssuerError,
    MissingRequiredClaimError,
)


# ---------------------------------------------------------------------------
# Typed claims container
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class JWTClaims:
    sub: str
    role: str
    jti: str
    iat: int
    exp: int
    iss: Optional[str] = None
    aud: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "JWTClaims":
        required = {"sub", "role", "jti", "iat", "exp"}
        missing = required - payload.keys()
        if missing:
            raise ValueError(f"JWT missing required claims: {missing}")
        known = {"sub", "role", "jti", "iat", "exp", "iss", "aud"}
        return cls(
            sub=str(payload["sub"]),
            role=str(payload["role"]),
            jti=str(payload["jti"]),
            iat=int(payload["iat"]),
            exp=int(payload["exp"]),
            iss=payload.get("iss"),
            aud=payload.get("aud"),
            extra={k: v for k, v in payload.items() if k not in known},
        )


# ---------------------------------------------------------------------------
# RS256 Verifier
# ---------------------------------------------------------------------------

class RS256Verifier:
    """Verifies RS256-signed JWTs against a PEM public key.

    Accepts the public key as a PEM string, a file path, or reads from the
    ``UNIGURU_JWT_PUBLIC_KEY`` / ``UNIGURU_JWT_PUBLIC_KEY_PATH`` env vars.
    """

    ALGORITHM = "RS256"

    def __init__(
        self,
        public_key_pem: Optional[str] = None,
        public_key_path: Optional[str] = None,
        issuer: Optional[str] = None,
        audience: Optional[str] = None,
        leeway_seconds: int = 10,
    ) -> None:
        pem = (
            public_key_pem
            or os.getenv("UNIGURU_JWT_PUBLIC_KEY", "")
            or self._read_key_file(public_key_path or os.getenv("UNIGURU_JWT_PUBLIC_KEY_PATH", ""))
        )
        if not pem:
            raise ValueError(
                "RS256 public key required. Set UNIGURU_JWT_PUBLIC_KEY or UNIGURU_JWT_PUBLIC_KEY_PATH."
            )
        self._public_key = self._load_pem(pem.strip())
        self._issuer = issuer or os.getenv("UNIGURU_JWT_ISSUER")
        self._audience = audience or os.getenv("UNIGURU_JWT_AUDIENCE")
        self._leeway = leeway_seconds

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def verify(self, token: str) -> JWTClaims:
        """Decode and verify an RS256 JWT. Raises on any failure."""
        options: Dict[str, Any] = {
            "require": ["sub", "role", "jti", "iat", "exp"],
            "verify_signature": True,
            "verify_exp": True,
            "verify_iat": True,
        }
        decode_kwargs: Dict[str, Any] = {
            "algorithms": [self.ALGORITHM],
            "options": options,
            "leeway": self._leeway,
        }
        if self._issuer:
            decode_kwargs["issuer"] = self._issuer
        if self._audience:
            decode_kwargs["audience"] = self._audience

        try:
            payload: Dict[str, Any] = jwt.decode(token, self._public_key, **decode_kwargs)
        except ExpiredSignatureError as exc:
            raise PermissionError("JWT has expired.") from exc
        except InvalidAlgorithmError as exc:
            raise PermissionError("JWT algorithm must be RS256.") from exc
        except (InvalidAudienceError, InvalidIssuerError) as exc:
            raise PermissionError(f"JWT audience/issuer mismatch: {exc}") from exc
        except MissingRequiredClaimError as exc:
            raise PermissionError(f"JWT missing required claim: {exc}") from exc
        except DecodeError as exc:
            raise PermissionError(f"JWT decode failure: {exc}") from exc

        return JWTClaims.from_payload(payload)

    def is_valid(self, token: str) -> bool:
        """Return True if the token verifies without raising."""
        try:
            self.verify(token)
            return True
        except (PermissionError, ValueError):
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _read_key_file(path: str) -> str:
        if not path:
            return ""
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return fh.read()
        except OSError:
            return ""

    @staticmethod
    def _load_pem(pem: str) -> RSAPublicKey:
        try:
            key = load_pem_public_key(pem.encode("utf-8"))
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid RSA public key PEM: {exc}") from exc
        if not isinstance(key, RSAPublicKey):
            raise ValueError("Provided key is not an RSA public key.")
        return key


# ---------------------------------------------------------------------------
# RBAC Enforcer
# ---------------------------------------------------------------------------

# Role hierarchy: higher index = more privilege
_ROLE_HIERARCHY: List[str] = ["viewer", "user", "operator", "admin", "superadmin"]


class RBACEnforcer:
    """Enforces role-based access control against verified JWT claims.

    Usage::

        enforcer = RBACEnforcer(required_roles={"admin", "superadmin"})
        enforcer.enforce(claims)   # raises PermissionError if role insufficient
    """

    def __init__(
        self,
        required_roles: Optional[Set[str]] = None,
        min_role: Optional[str] = None,
    ) -> None:
        self._required_roles: Set[str] = required_roles or set()
        self._min_role = min_role

    def enforce(self, claims: JWTClaims) -> None:
        """Raise PermissionError if the claims do not satisfy the RBAC policy."""
        role = claims.role.lower()

        if self._required_roles and role not in {r.lower() for r in self._required_roles}:
            raise PermissionError(
                f"Role '{role}' not in required roles {self._required_roles}."
            )

        if self._min_role:
            min_idx = _role_index(self._min_role)
            if _role_index(role) < min_idx:
                raise PermissionError(
                    f"Role '{role}' is below minimum required role '{self._min_role}'."
                )

    def is_authorized(self, claims: JWTClaims) -> bool:
        try:
            self.enforce(claims)
            return True
        except PermissionError:
            return False


def _role_index(role: str) -> int:
    try:
        return _ROLE_HIERARCHY.index(role.lower())
    except ValueError:
        return -1
