"""
Pytest configuration and shared fixtures for quantum-entanglement-witness tests.
"""
import os


def pytest_configure(config):
    """Set default environment variables for tests if not already set."""
    if not os.environ.get("AUDIT_SECRET_KEY"):
        os.environ["AUDIT_SECRET_KEY"] = "test-audit-secret-key-for-pytest-32chars"
