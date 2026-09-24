import json
from pathlib import Path

from fastapi import HTTPException


ROOT_DIR = Path(__file__).resolve().parents[1]

MANIFEST_PATHS = {
    "shell-company-screening":
        ROOT_DIR
        / "agents"
        / "shell_company_screening"
        / "manifest.json",

    "due-diligence-agent":
        ROOT_DIR
        / "agents"
        / "due_diligence"
        / "manifest.json",
}


def get_manifest(agent_id: str):
    manifest_path = MANIFEST_PATHS.get(agent_id)

    if manifest_path is None:
        raise HTTPException(
            status_code=404,
            detail="agent not found",
        )

    try:
        with manifest_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="manifest missing",
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="manifest invalid",
        )
