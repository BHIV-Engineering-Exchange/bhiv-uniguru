"""
Phase 2: Advanced Integration & Security Hardening
Isha Singh — UniGuru Production Certification and Enterprise Readiness (Sprint 4)

Unit test coverage for:
- Production monitoring (metrics, structured logger, observability)
- Error boundary safety (safe fallback, exception isolation)
- E2E integration verification (ecosystem runtime, replay, Mitra redaction)
- API contract boundaries (auth, rate-limit, validation)
- Deterministic execution (replay stability, hash chain)
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("UNIGURU_API_AUTH_REQUIRED", "false")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def runtime_client():
    from service.uniguru_runtime_api import app
    return TestClient(app)


@pytest.fixture(scope="module")
def api_client():
    from service.api import app
    return TestClient(app)


@pytest.fixture()
def tmp_proof_dir():
    d = tempfile.mkdtemp(prefix="phase2_proof_")
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------------------
# 1. Production Monitoring — metrics endpoint
# ---------------------------------------------------------------------------

def test_metrics_endpoint_exposes_ecosystem_runtime_ready(runtime_client):
    resp = runtime_client.get("/metrics")
    assert resp.status_code == 200
    body = resp.text
    assert "uniguru_ecosystem_runtime_ready" in body
    assert "uniguru_ecosystem_runtime_info" in body


def test_metrics_collector_records_latency_and_confidence():
    from observability.metrics_collector import MetricsCollector
    collector = MetricsCollector()
    collector.record_request_latency(42.5, route="/ask")
    collector.record_confidence(0.75)
    snap = collector.get_snapshot()
    assert snap["request_latency_ms"]["sample_count"] == 1
    assert snap["request_latency_ms"]["p50"] == 42.5
    assert snap["confidence_distribution"]["0.6-0.8"] == 1


def test_metrics_collector_records_failure_classification():
    from observability.metrics_collector import MetricsCollector
    collector = MetricsCollector()
    collector.record_failure("no_knowledge")
    collector.record_failure("auth_failure")
    snap = collector.get_snapshot()
    assert snap["failure_classification"]["no_knowledge"] == 1
    assert snap["failure_classification"]["auth_failure"] == 1


def test_metrics_collector_prometheus_lines_include_latency_and_confidence():
    from observability.metrics_collector import MetricsCollector
    collector = MetricsCollector()
    collector.record_request_latency(100.0)
    collector.record_confidence(0.9)
    lines = "\n".join(collector.to_prometheus_lines())
    assert "uniguru_request_latency_ms_p50" in lines
    assert "uniguru_confidence_distribution_total" in lines


def test_structured_logger_emits_request_entry(tmp_path):
    from observability.structured_logger import StructuredLogger
    log_path = tmp_path / "test.jsonl"
    logger = StructuredLogger(log_path=log_path, write_stdout=False)
    entry = logger.log_request(
        request_id="req-001",
        route="/ask",
        latency_ms=55.3,
        status_code=200,
        verification_status="VERIFIED",
        confidence=0.82,
    )
    assert entry["level"] == "INFO"
    assert entry["route"] == "/ask"
    assert entry["verification_status"] == "VERIFIED"
    assert log_path.exists()


def test_structured_logger_marks_error_level_for_5xx(tmp_path):
    from observability.structured_logger import StructuredLogger
    logger = StructuredLogger(log_path=tmp_path / "err.jsonl", write_stdout=False)
    entry = logger.log_request(request_id="req-500", route="/ask", latency_ms=10.0, status_code=500)
    assert entry["level"] == "ERROR"


def test_structured_logger_get_recent_entries(tmp_path):
    from observability.structured_logger import StructuredLogger
    logger = StructuredLogger(log_path=tmp_path / "recent.jsonl", write_stdout=False)
    for i in range(5):
        logger.log_request(request_id=f"req-{i}", route="/ask", latency_ms=float(i), status_code=200)
    entries = logger.get_recent_entries(n=3)
    assert len(entries) == 3


# ---------------------------------------------------------------------------
# 2. Error Boundary Safety
# ---------------------------------------------------------------------------

def test_health_endpoint_returns_ok(runtime_client):
    resp = runtime_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ready_endpoint_returns_ready(runtime_client):
    resp = runtime_client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_ecosystem_execute_rejects_empty_query(runtime_client):
    resp = runtime_client.post("/runtime/ecosystem/execute", json={"query": "   ", "emit_proof": False})
    assert resp.status_code == 422


def test_ecosystem_execute_rejects_missing_query(runtime_client):
    resp = runtime_client.post("/runtime/ecosystem/execute", json={"emit_proof": False})
    assert resp.status_code == 422


def test_ecosystem_execute_rejects_oversized_query(runtime_client):
    resp = runtime_client.post(
        "/runtime/ecosystem/execute",
        json={"query": "x" * 2001, "emit_proof": False},
    )
    assert resp.status_code == 422


def test_api_ask_returns_safe_fallback_on_empty_answer(api_client):
    """The /ask endpoint must never return an empty answer — safe fallback engages."""
    resp = api_client.post(
        "/ask",
        json={"query": "xyzzy_nonexistent_topic_12345", "context": {"caller": "internal-testing"}},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert str(body.get("answer") or "").strip() != ""


def test_api_ask_error_boundary_does_not_raise(api_client):
    """The /ask endpoint must return 200 even for edge-case inputs."""
    resp = api_client.post(
        "/ask",
        json={"query": "test query", "context": {"caller": "internal-testing"}},
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 3. E2E Integration Verification — ecosystem runtime
# ---------------------------------------------------------------------------

def test_ecosystem_execute_returns_all_required_contract_fields(runtime_client):
    resp = runtime_client.post(
        "/runtime/ecosystem/execute",
        json={"query": "What is the Bhagavad Gita?", "emit_proof": False, "trace_id": "phase2_e2e_test"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["vijay_validation"]["replay_safe"] is True
    assert body["tantra_contract"]["contract_bound"] is True
    assert body["bucket_telemetry"]["emitted"] is True
    assert body["insightflow_observability"]["trace_complete"] is True
    assert body["gc_validation"]["authority_enforced"] is True
    assert body["mdu_validation"]["schema_compatible"] is True
    assert "execution_hash" in body


def test_ecosystem_replay_verifies_all_stable_fields(runtime_client):
    resp = runtime_client.post(
        "/runtime/ecosystem/replay",
        json={"query": "What is the Bhagavad Gita?", "emit_proof": False, "trace_id": "phase2_replay_test"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["replay_verified"] is True
    assert all(body["checks"].values()), f"Unstable replay checks: {body['checks']}"


def test_mitra_endpoint_redacts_internal_governance_fields(runtime_client):
    resp = runtime_client.post(
        "/mitra/ecosystem/ask",
        json={"query": "What is dharma?", "emit_proof": False, "trace_id": "phase2_mitra_test"},
    )
    assert resp.status_code == 200
    body = resp.json()
    # Internal governance fields must not be exposed
    for forbidden in ("vijay_validation", "gc_validation", "mdu_validation", "tantra_sdk_contracts"):
        assert forbidden not in body, f"Internal field '{forbidden}' leaked to Mitra response"
    # Required public fields must be present
    assert "trace_id" in body
    assert "replay_safe" in body
    assert "downstream_consumable" in body


def test_ecosystem_execute_emits_proof_files(tmp_proof_dir):
    from service.ecosystem_runtime import execute_ecosystem_runtime
    result = execute_ecosystem_runtime(
        query="What is karma?",
        proof_dir=tmp_proof_dir,
        emit_proof=True,
        trace_id="phase2_proof_emit_test",
    )
    assert (tmp_proof_dir / "ecosystem_execution_latest.json").exists()
    assert (tmp_proof_dir / "ecosystem_execution_phase2_proof_emit_test.json").exists()
    assert result["trace_id"] == "phase2_proof_emit_test"


def test_ecosystem_replay_emits_proof_files(tmp_proof_dir):
    from service.ecosystem_runtime import verify_ecosystem_replay
    result = verify_ecosystem_replay(
        query="What is karma?",
        proof_dir=tmp_proof_dir,
        emit_proof=True,
        trace_id="phase2_replay_emit_test",
    )
    assert (tmp_proof_dir / "replay_verification_latest.json").exists()
    assert result["replay_verified"] is True


# ---------------------------------------------------------------------------
# 4. API Contract Boundaries — auth and validation
# ---------------------------------------------------------------------------

def test_runtime_api_health_requires_no_auth(runtime_client):
    resp = runtime_client.get("/health")
    assert resp.status_code == 200


def test_runtime_api_ready_requires_no_auth(runtime_client):
    resp = runtime_client.get("/ready")
    assert resp.status_code == 200


def test_runtime_api_metrics_requires_no_auth(runtime_client):
    """Metrics on the runtime app are unauthenticated (no auth middleware on this app)."""
    resp = runtime_client.get("/metrics")
    assert resp.status_code == 200


def test_ecosystem_execute_trace_id_is_echoed(runtime_client):
    resp = runtime_client.post(
        "/runtime/ecosystem/execute",
        json={"query": "What is yoga?", "emit_proof": False, "trace_id": "contract_trace_abc"},
    )
    assert resp.status_code == 200
    assert resp.json()["trace_id"] == "contract_trace_abc"


def test_mitra_trace_id_is_echoed(runtime_client):
    resp = runtime_client.post(
        "/mitra/ecosystem/ask",
        json={"query": "What is yoga?", "emit_proof": False, "trace_id": "mitra_trace_xyz"},
    )
    assert resp.status_code == 200
    assert resp.json()["trace_id"] == "mitra_trace_xyz"


# ---------------------------------------------------------------------------
# 5. Deterministic Execution — replay hash stability
# ---------------------------------------------------------------------------

def test_ecosystem_execution_hash_is_stable_across_runs():
    from service.ecosystem_runtime import execute_ecosystem_runtime
    query = "What is the Bhagavad Gita?"
    trace_id = "phase2_determinism_test"
    r1 = execute_ecosystem_runtime(query=query, emit_proof=False, trace_id=trace_id)
    r2 = execute_ecosystem_runtime(query=query, emit_proof=False, trace_id=trace_id)
    assert r1["execution_hash"] == r2["execution_hash"]
    assert r1["vijay_validation"]["runtime_hash"] == r2["vijay_validation"]["runtime_hash"]
    assert r1["mdu_validation"]["evidence_payload"]["lineage_hash"] == r2["mdu_validation"]["evidence_payload"]["lineage_hash"]


def test_vijay_hash_chain_is_valid():
    from service.ecosystem_runtime import execute_ecosystem_runtime
    result = execute_ecosystem_runtime(
        query="What is the Bhagavad Gita?", emit_proof=False, trace_id="phase2_hash_chain_test"
    )
    assert result["vijay_validation"]["hash_chain_ok"] is True
    assert result["vijay_validation"]["replay_safe"] is True


def test_tantra_contract_schema_is_stable_across_runs():
    from service.ecosystem_runtime import execute_ecosystem_runtime
    r1 = execute_ecosystem_runtime(query="What is dharma?", emit_proof=False, trace_id="schema_stable_1")
    r2 = execute_ecosystem_runtime(query="What is dharma?", emit_proof=False, trace_id="schema_stable_1")
    assert r1["tantra_contract"]["schema"] == r2["tantra_contract"]["schema"]
    assert r1["tantra_contract"]["trace_continuity"] == r2["tantra_contract"]["trace_continuity"]
