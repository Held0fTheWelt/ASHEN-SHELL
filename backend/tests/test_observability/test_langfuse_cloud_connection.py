"""Test Langfuse Cloud connection with real traces using official SDK pattern.

Uses get_client() singleton and context manager pattern from official Langfuse
documentation.

Run from repo root with:
python -m pytest backend/tests/test_observability/test_langfuse_cloud_connection.py::TestLangfuseCloudConnection::test_langfuse_sends_trace_to_cloud -v
"""

import pytest
import time


class TestLangfuseCloudConnection:
    """Integration tests for real Langfuse Cloud communication."""

    def test_langfuse_sends_trace_to_cloud(self):
        """Verify that traces are sent using the current encrypted backend settings."""
        langfuse_module = pytest.importorskip(
            "langfuse",
            reason="langfuse SDK not installed; skipping cloud connection test",
        )

        from app import create_app
        from app.config import Config

        current_app = create_app(Config)
        with current_app.app_context():
            from app.services.observability_governance_service import (
                get_observability_config,
                get_observability_credential_for_runtime,
            )

            db_config = get_observability_config()
            if not db_config.get("is_enabled"):
                pytest.skip("Langfuse is disabled in current backend settings; skipping cloud connection test")

            public_key = get_observability_credential_for_runtime("public_key") or ""
            secret_key = get_observability_credential_for_runtime("secret_key") or ""
            base_url = db_config.get("base_url", "https://cloud.langfuse.com")

        if not public_key or not secret_key:
            pytest.skip("Langfuse credentials are not configured in current backend settings; skipping cloud connection test")

        print(f"\n[TEST] Langfuse credentials found")
        print(f"[TEST] Base URL: {base_url}")

        # Initialize client directly with explicit credentials
        try:
            langfuse = langfuse_module.Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                base_url=base_url,
            )
            print(f"[TEST] Langfuse client initialized with explicit credentials")
        except Exception as e:
            pytest.fail(f"Failed to initialize Langfuse client: {e}")

        trace_seed = f"world-of-shadows-pytest-{time.time_ns()}"
        trace_id = langfuse.create_trace_id(seed=trace_seed)
        trace_url = langfuse.get_trace_url(trace_id=trace_id)

        # Create span using context manager (official pattern)
        print(f"[TEST] Creating trace using current backend settings...")
        print(f"[TEST] Trace ID: {trace_id}")
        print(f"[TEST] Trace URL: {trace_url}")
        try:
            with langfuse.start_as_current_observation(
                as_type="span",
                name="world_of_shadows.pytest_trace",
                trace_context={"trace_id": trace_id},
                input={"source": "pytest", "test": "test_langfuse_sends_trace_to_cloud"},
                metadata={
                    "test_type": "cloud_connection",
                    "source": "pytest_test_langfuse_cloud_connection",
                    "settings_source": "current_backend_database",
                },
            ) as span:
                assert langfuse.get_current_trace_id() == trace_id
                print(f"  [OK] Span created")

                with langfuse.start_as_current_observation(
                    as_type="span",
                    name="backend.test_span",
                    metadata={
                        "test_type": "cloud_connection",
                        "timestamp": time.time(),
                    },
                ) as span2:
                    print(f"  [OK] Child span created")
                    time.sleep(0.05)
                    span2.update(output={"message": "Test successful"})

                span.update(output={"status": "completed", "trace_id": trace_id})

            print(f"[TEST] Trace completed locally")
        except Exception as e:
            pytest.fail(f"Failed to create trace: {e}")

        # Flush all pending events
        print(f"[TEST] Flushing all spans to Langfuse Cloud...")
        try:
            langfuse.flush()
            print(f"[TEST] Flush completed successfully")
        except Exception as e:
            pytest.fail(f"Failed to flush spans: {e}")

        # Wait for network transmission
        print(f"[TEST] Waiting for Langfuse Cloud to make trace queryable...")
        fetched_trace = None
        last_error = None
        for _ in range(60):
            try:
                fetched_trace = langfuse.api.trace.get(trace_id)
                break
            except Exception as e:
                last_error = e
                time.sleep(1)

        if fetched_trace is None:
            pytest.fail(f"Trace {trace_id} was flushed but not queryable in Langfuse Cloud: {last_error}")

        print(f"\n[TEST] SUCCESS: Trace verified in Langfuse Cloud!")
        print(f"[TEST] Verified Trace ID: {fetched_trace.id}")
        print(f"[TEST] Dashboard: {base_url}")
        print(f"[TEST] Trace URL: {trace_url}")

    def test_langfuse_adapter_has_client_configured(self, app):
        """Verify the Langfuse adapter is properly configured with valid client."""
        from app.observability.langfuse_adapter import LangfuseAdapter

        adapter = LangfuseAdapter.get_instance()

        # Adapter should either be:
        # 1. Ready with a valid client (Langfuse enabled and configured)
        # 2. Not ready with no client (Langfuse disabled)
        if adapter.is_ready:
            assert adapter.client is not None, "Ready adapter must have a client"
            assert adapter.is_enabled(), "Ready adapter must report is_enabled() = True"
        # else: adapter not ready is acceptable (Langfuse can be disabled)

    def test_langfuse_credentials_from_database(self, app, db_session):
        """Verify Langfuse credentials are loaded from database when configured."""
        from app.observability.langfuse_adapter import LangfuseAdapter
        from app.models.governance_core import ObservabilityConfig, ObservabilityCredential

        adapter = LangfuseAdapter.get_instance()

        # Check database configuration
        config = db_session.query(ObservabilityConfig).filter_by(service_id="langfuse").first()

        if config and config.is_enabled:
            secret = db_session.query(ObservabilityCredential).filter_by(
                service_id=config.service_id, secret_name="secret_key", is_active=True
            ).first()

            if secret and secret.encrypted_secret:
                # Database has credentials configured
                assert adapter.is_ready, "Adapter should be ready when DB has valid credentials"
                print("\n[TEST] Langfuse configured in database: adapter is ready")
            else:
                print("\n[TEST] Langfuse enabled in DB but secret_key missing")
        else:
            print("\n[TEST] Langfuse not configured in database")
