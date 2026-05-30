import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from llm_skills_bench.dashboard import create_app


def _make_run(run_id, model, timestamp, summary):
    return {
        "run_id": run_id,
        "model": model,
        "timestamp": timestamp,
        "skills_filter": [],
        "results": [],
        "summary": summary,
    }


def _write_run(directory: Path, run: dict) -> Path:
    path = directory / f"{run['run_id']}.json"
    path.write_text(json.dumps(run), encoding="utf-8")
    return path


@pytest.fixture()
def empty_dir(tmp_path):
    return tmp_path


@pytest.fixture()
def client_empty(empty_dir):
    return TestClient(create_app(empty_dir))


def test_index_ok(client_empty):
    resp = client_empty.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_index_contains_chart_js(client_empty):
    resp = client_empty.get("/")
    body = resp.text.lower()
    assert "chart.js" in body


def test_api_runs_empty(client_empty):
    resp = client_empty.get("/api/runs")
    assert resp.status_code == 200
    assert resp.json() == []


def test_api_runs_returns_sorted_data(tmp_path):
    run_old = _make_run("run-old", "gpt-4o", "2024-01-01T00:00:00", {"coding": 0.5})
    run_new = _make_run("run-new", "gpt-4o", "2024-06-01T00:00:00", {"coding": 0.8})
    _write_run(tmp_path, run_old)
    _write_run(tmp_path, run_new)

    client = TestClient(create_app(tmp_path))
    resp = client.get("/api/runs")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    # Most recent first
    assert data[0]["run_id"] == "run-new"
    assert data[1]["run_id"] == "run-old"


def test_api_run_by_id_found(tmp_path):
    run = _make_run("run-abc", "claude-3-5-sonnet", "2024-03-15T12:00:00", {"reasoning": 0.7})
    _write_run(tmp_path, run)

    client = TestClient(create_app(tmp_path))
    resp = client.get("/api/runs/run-abc")
    assert resp.status_code == 200
    assert resp.json()["model"] == "claude-3-5-sonnet"


def test_api_run_by_id_not_found(tmp_path):
    client = TestClient(create_app(tmp_path))
    resp = client.get("/api/runs/nonexistent")
    assert resp.status_code == 404


def test_api_runs_skips_bad_json(tmp_path):
    run = _make_run("run-good", "gpt-4o", "2024-05-01T00:00:00", {"coding": 0.9})
    _write_run(tmp_path, run)
    (tmp_path / "bad.json").write_text("not valid json", encoding="utf-8")

    client = TestClient(create_app(tmp_path))
    resp = client.get("/api/runs")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["run_id"] == "run-good"
