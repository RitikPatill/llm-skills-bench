from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

import json

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def load_runs(results_dir: Path) -> list[dict]:
    """Load all run JSON files from results_dir, sorted newest first."""
    runs = []
    try:
        paths = list(results_dir.glob("*.json"))
    except FileNotFoundError:
        return []
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            runs.append(data)
        except Exception:
            continue
    runs.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
    return runs


def create_app(results_dir: Path) -> FastAPI:
    app = FastAPI(title="LLM Skills Bench Dashboard")
    app.state.results_dir = results_dir

    templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

    @app.get("/", response_class=None)
    async def index(request: Request):
        return templates.TemplateResponse(request, "dashboard.html")

    @app.get("/api/runs")
    async def api_runs(request: Request):
        runs = load_runs(request.app.state.results_dir)
        return JSONResponse(content=runs)

    @app.get("/api/runs/{run_id}")
    async def api_run_by_id(run_id: str, request: Request):
        runs = load_runs(request.app.state.results_dir)
        for run in runs:
            if run.get("run_id") == run_id:
                return JSONResponse(content=run)
        raise HTTPException(status_code=404, detail="Run not found")

    return app
