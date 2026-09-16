# CODE_PACKET — T-GOV-002
## Enterprise RBAC, Replay-Proof Verification & Automated Audit Emitters

---

## Directory Tree (new files only)

```
backend/
├── security/
│   ├── __init__.py                  # Package exports: RS256Verifier, RBACEnforcer, JWTClaims,
│   │                                #   ReplayMitigationTable, AuditEmitter
│   ├── jwt_rs256.py                 # RS256 JWT verifier + RBAC enforcer + JWTClaims dataclass
│   ├── replay_table.py              # Thread-safe jti replay mitigation table
│   └── audit_emitter.py            # SHA-256 hash-chained immutable audit log
│
├── tests/
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_jwt_rs256.py        # 16 tests: verify, RBAC, edge cases
│   │   ├── test_replay_table.py     # 12 tests: consume, replay, TTL, persistence
│   │   └── test_audit_emitter.py   # 13 tests: emit, chain, tamper detection, reload
│   └── integration/
│       ├── __init__.py
│       └── test_rbac_audit_integration.py  # 8 tests: end-to-end + 50-run determinism gate
│
├── REVIEW_PACKET_T_GOV_002.md
└── CODE_PACKET_T_GOV_002.md        # (this file)
```

---

## Module Summaries

### `security/jwt_rs256.py`

| Symbol | Type | Description |
|---|---|---|
| `JWTClaims` | frozen dataclass | Typed container for verified JWT claims (sub, role, jti, iat, exp, iss, aud, extra) |
| `RS256Verifier` | class | Verifies RS256 JWTs against a PEM public key; raises `PermissionError` on any failure |
| `RS256Verifier.verify(token)` | method | Returns `JWTClaims`; raises on expiry, wrong algo, bad sig, missing claims |
| `RS256Verifier.is_valid(token)` | method | Returns bool; never raises |
| `RBACEnforcer` | class | Enforces role membership or minimum role level from `JWTClaims` |
| `RBACEnforcer.enforce(claims)` | method | Raises `PermissionError` if role policy not satisfied |
| `RBACEnforcer.is_authorized(claims)` | method | Returns bool; never raises |
| `_ROLE_HIERARCHY` | list | `["viewer","user","operator","admin","superadmin"]` |

### `security/replay_table.py`

| Symbol | Type | Description |
|---|---|---|
| `ReplayMitigationTable` | class | Thread-safe jti/nonce store with TTL eviction and optional file persistence |
| `.consume(jti, exp)` | method | Marks jti consumed; raises `ValueError` on replay |
| `.try_consume(jti, exp)` | method | Returns False on replay; never raises |
| `.is_replayed(jti)` | method | Returns True if jti is active in the table |
| `.size()` | method | Count of non-expired entries |
| `.clear()` | method | Empties the table |

### `security/audit_emitter.py`

| Symbol | Type | Description |
|---|---|---|
| `AuditEntry` | class | Immutable entry with `entry_hash = SHA-256(all fields)` and `prev_hash` chain link |
| `AuditEmitter` | class | Append-only JSONL audit log with hash chain |
| `.emit(event, actor, resource, outcome, metadata)` | method | Appends entry; returns `AuditEntry` |
| `.verify_chain()` | method | Re-reads file, recomputes all hashes; returns `{valid, entry_count, broken_at_seq}` |
| `.tail(n)` | method | Returns last n entries as dicts |
| `.last_hash` | property | Current chain tip hash |
| `_GENESIS_HASH` | constant | `"0" * 64` — sentinel for first entry's prev_hash |

---

## Test Summary

| File | Tests | Coverage |
|---|---|---|
| `tests/unit/test_jwt_rs256.py` | 16 | RS256 verify, RBAC enforce, all failure modes |
| `tests/unit/test_replay_table.py` | 12 | Consume, replay detection, TTL eviction, persistence |
| `tests/unit/test_audit_emitter.py` | 13 | Emit, chain integrity, tamper detection, reload, determinism |
| `tests/integration/test_rbac_audit_integration.py` | 8 | E2E flow, replay block, RBAC deny, audit chain, 50-run determinism |
| **Total** | **48** | **100% pass** |

---

## Runtime Evidence

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.3
collected 48 items

tests/unit/test_jwt_rs256.py                          16 passed
tests/unit/test_replay_table.py                       12 passed
tests/unit/test_audit_emitter.py                      13 passed
tests/integration/test_rbac_audit_integration.py       8 passed

48 passed in 3.15s
```
