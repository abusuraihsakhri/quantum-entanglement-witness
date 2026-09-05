"""
Security-focused tests for quantum-entanglement-witness.
Tests for PHI guard, audit trail, path traversal protection, and input validation.
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import (
    PHIGuard,
    AuditTrail,
    AuditLogger,
    SecurityException,
    safe_resolve_path,
)


class TestPHIGuard:
    """Tests for Zero-PHI outbound guard."""

    def test_blocks_mrn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive")

    def test_blocks_ssn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_blocks_phone_number(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call patient at 555-123-4567")

    def test_blocks_email(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email patient at john@example.com")

    def test_blocks_patient_name(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient Name: John Smith")

    def test_blocks_doe(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient John Doe admitted")

    def test_allows_clean_text(self):
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")
        PHIGuard.assert_no_phi("Task TASK-2026-001 processed successfully")

    def test_allows_empty_string(self):
        PHIGuard.assert_no_phi("")

    def test_redact_phi(self):
        result = PHIGuard.redact_phi("Patient MRN-12345678 has SSN 123-45-6789")
        assert "MRN" not in result
        assert "123-45-6789" not in result
        assert "[REDACTED_IDENTIFIER]" in result


class TestAuditTrail:
    """Tests for HMAC-SHA256 tamper-evident audit trail."""

    def setup_method(self):
        """Reset global audit before each test."""
        AuditLogger.reset()
        os.environ["AUDIT_SECRET_KEY"] = "test-audit-secret-key-32chars-long"

    def teardown_method(self):
        AuditLogger.reset()
        if "AUDIT_SECRET_KEY" in os.environ:
            del os.environ["AUDIT_SECRET_KEY"]

    def test_requires_secret_key(self):
        del os.environ["AUDIT_SECRET_KEY"]
        AuditLogger.reset()
        with pytest.raises(RuntimeError, match="AUDIT_SECRET_KEY"):
            AuditLogger.log("test", "tier", "event", {"data": "value"})

    def test_rejects_short_key(self):
        os.environ["AUDIT_SECRET_KEY"] = "short"
        AuditLogger.reset()
        with pytest.raises(ValueError, match="at least 16 characters"):
            AuditLogger.log("test", "tier", "event", {"data": "value"})

    def test_log_creates_entry(self):
        entry = AuditLogger.log("test_actor", "worker", "TEST_EVENT", {"key": "value"})
        assert "audit_id" in entry
        assert "current_hash" in entry
        assert entry["actor"] == "test_actor"

    def test_verify_integrity_valid(self):
        AuditLogger.log("actor1", "worker", "EVENT_1", {"a": 1})
        AuditLogger.log("actor2", "worker", "EVENT_2", {"b": 2})
        assert AuditLogger.verify_integrity() is True

    def test_get_trail_returns_entries(self):
        AuditLogger.log("actor", "worker", "EVENT", {"data": "test"})
        trail = AuditLogger.get_trail()
        assert len(trail) == 1
        assert trail[0]["event_type"] == "EVENT"

    def test_custom_secret_key(self):
        trail = AuditTrail(secret_key="my-custom-secret-key-1234567890")
        entry = trail.log("actor", "tier", "event", {"data": "value"})
        assert entry["current_hash"] != ""
        assert trail.verify_integrity() is True


class TestSafeResolvePath:
    """Tests for path traversal protection."""

    def test_resolves_relative_path(self):
        result = safe_resolve_path("sample.csv")
        assert Path(result).exists()

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            safe_resolve_path("nonexistent_file_12345.csv", must_exist=True)

    def test_raises_on_system_path_windows(self):
        with pytest.raises(PermissionError):
            safe_resolve_path("\\Windows\\System32\\config\\SAM")

    def test_raises_on_system_path_unix(self):
        with pytest.raises(PermissionError):
            safe_resolve_path("/etc/passwd")

    def test_raises_on_network_path(self):
        with pytest.raises(PermissionError):
            safe_resolve_path("\\\\server\\share\\file.csv")

    def test_raises_on_url_path(self):
        with pytest.raises(PermissionError):
            safe_resolve_path("http://evil.com/malicious.csv")
