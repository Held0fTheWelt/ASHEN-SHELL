"""Tests for OpenAPI → Postman URL mapping and grouping."""
from __future__ import annotations

import unittest

from postmanify.tools.openapi_postman import backend_postman_url_raw, group_operations_by_tag, iter_operations


class UrlMappingTests(unittest.TestCase):
    def test_backend_prefix_tail(self) -> None:
        self.assertEqual(
            backend_postman_url_raw("/api/v1/languages", backend_api_prefix="/api/v1"),
            "{{backendBaseUrl}}{{backendApiPrefix}}/languages",
        )
        self.assertEqual(
            backend_postman_url_raw("/api/v1", backend_api_prefix="/api/v1"),
            "{{backendBaseUrl}}{{backendApiPrefix}}",
        )

    def test_non_prefixed_path_uses_literal(self) -> None:
        self.assertEqual(
            backend_postman_url_raw("/other/path", backend_api_prefix="/api/v1"),
            "{{backendBaseUrl}}/other/path",
        )


class IterOperationsTests(unittest.TestCase):
    def test_iter_skips_non_operations(self) -> None:
        spec = {
            "paths": {
                "/api/v1/health": {
                    "get": {"tags": ["System"], "summary": "Health"},
                    "parameters": [],
                }
            }
        }
        ops = iter_operations(spec)
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0].method, "GET")
        self.assertEqual(ops[0].path, "/api/v1/health")

    def test_group_by_primary_tag(self) -> None:
        spec = {
            "paths": {
                "/api/v1/a": {"get": {"tags": ["Auth"], "summary": "A"}},
                "/api/v1/b": {"post": {"tags": ["Forum", "Auth"], "summary": "B"}},
            }
        }
        ops = iter_operations(spec)
        g = group_operations_by_tag(ops)
        self.assertIn("Auth", g)
        self.assertIn("Forum", g)
        self.assertEqual(len(g["Auth"]), 1)
        self.assertEqual(len(g["Forum"]), 1)


if __name__ == "__main__":
    unittest.main()
