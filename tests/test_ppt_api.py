"""Integration tests for the physical PPT API and tamper-detection of the audit trail."""
import math

import pytest
from fastapi.testclient import TestClient
from agents.api import app
from agents.base import AuditTrail


def _bell_matrix():
    return [[0.5, 0, 0, 0.5], [0, 0, 0, 0], [0, 0, 0, 0], [0.5, 0, 0, 0.5]]


def test_api_bell_and_invalid_matrix():
    client = TestClient(app)
    response = client.post("/api/ppt", json={"matrix": _bell_matrix()})
    assert response.status_code == 200
    result = response.json()
    assert result["classification"] == "entangled"
    assert result["negativity"] == pytest.approx(0.5)
    assert result["witness_expectation"] == pytest.approx(-0.5)

    bad = client.post("/api/ppt", json={"matrix": [[1, 0], [0, 1]]})
    assert bad.status_code == 422
    assert "4x4" in bad.json()["detail"]


def test_signed_ledger_detects_mutations():
    trail = AuditTrail(secret_key="unique-long-testing-secret-0001")
    trail.log("actor", "tier", "EVENT", {"count": 1})
    trail.log("actor", "tier", "EVENT", {"count": 2})
    assert trail.verify_integrity() is True

    records = trail.get_trail()
    records[0]["event_type"] = "EXTERNAL_MUTATION"
    assert trail.verify_integrity() is True

    trail.logs[0]["event_type"] = "TAMPERED"
    assert trail.verify_integrity() is False


def test_wrong_hmac_rejected_even_with_unchanged_links():
    trail = AuditTrail(secret_key="unique-long-testing-secret-0001")
    trail.log("actor", "tier", "EVENT", {"count": 1})
    trail.logs[0]["current_hash"] = "0" * 64
    assert trail.verify_integrity() is False
