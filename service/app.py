from datetime import datetime, timezone
import uuid

from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .auth import require_service_token
from .database import (
    create_run_record,
    get_run_record,
    init_database,
)
from .registry import get_manifest
from .validation import validate_and_build_settings


app = FastAPI(
    title="ATL Research Agent Service",
    version="1.0.0",
)


init_database()


def utc_now():
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


@app.get(
    "/manifest",
    dependencies=[
        Depends(require_service_token)
    ],
)
def manifest(agent_id: str):
    return get_manifest(agent_id)


@app.post(
    "/runs",
    status_code=202,
    dependencies=[
        Depends(require_service_token)
    ],
)
def create_run(
    body: dict = Body(...),
):
    agent_id = body.get("agent_id")
    submitted_settings = body.get("settings")

    field_errors = {}

    if not isinstance(agent_id, str) or not agent_id:
        field_errors["agent_id"] = "required"

    if not isinstance(submitted_settings, dict):
        field_errors["settings"] = "required"

    if field_errors:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "validation failed",
                "field_errors": field_errors,
            },
        )

    manifest_data = get_manifest(agent_id)

    settings, errors = validate_and_build_settings(
        agent_id,
        manifest_data,
        submitted_settings,
    )

    if errors:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "validation failed",
                "field_errors": errors,
            },
        )

    run_id = "run_" + uuid.uuid4().hex
    created_at = utc_now()

    create_run_record(
        run_id=run_id,
        agent_id=agent_id,
        status="queued",
        settings=settings,
        created_at=created_at,
    )

    return {
        "run_id": run_id,
        "status": "queued",
        "created_at": created_at,
    }


@app.get(
    "/runs/{run_id}",
    dependencies=[
        Depends(require_service_token)
    ],
)
def run_status(run_id: str):
    run = get_run_record(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="run not found",
        )

    response = {
        "run_id": run["run_id"],
        "status": run["status"],
        "created_at": run["created_at"],
    }

    if (
        run["status"] == "failed"
        and run["error"]
    ):
        response["error"] = run["error"]

    return response
