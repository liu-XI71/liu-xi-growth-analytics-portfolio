from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.routes import router
from backend.main import app as production_app
from backend.services import copilot_service


def _router_client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_bundle_service_returns_complete_copilot_contract() -> None:
    bundle = copilot_service.bundle()
    assert bundle is copilot_service.payload()
    assert {
        "meta",
        "decisions",
        "questions",
        "analysis_threads",
        "weekly_reports",
        "cases",
        "experiment_defaults",
        "metric_contracts",
        "evidence",
        "claims",
    } <= bundle.keys()
    assert "evals" not in bundle


def test_bundle_route_returns_the_full_service_payload_and_accepts_trailing_slash() -> None:
    with _router_client() as client:
        response = client.get("/api/v1/analytics/bundle")
        trailing_slash = client.get("/api/v1/analytics/bundle/")

    assert response.status_code == 200, response.text
    assert response.json() == copilot_service.bundle()
    assert trailing_slash.status_code == 200, trailing_slash.text
    assert trailing_slash.json() == response.json()


def test_bundle_route_translates_service_errors_without_leaking_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail() -> dict:
        raise KeyError("sensitive internal detail")

    monkeypatch.setattr(copilot_service, "bundle", fail)
    with _router_client() as client:
        response = client.get("/api/v1/analytics/bundle")

    assert response.status_code == 500
    assert response.json() == {"detail": "Unexpected analytics service error"}
    assert "sensitive" not in response.text


def test_production_cors_allows_local_frontend_for_bundle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr("backend.main.ensure_database", lambda: tmp_path / "unused.duckdb")
    with TestClient(production_app) as client:
        response = client.options(
            "/api/v1/analytics/bundle",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    assert "GET" in response.headers["access-control-allow-methods"]
