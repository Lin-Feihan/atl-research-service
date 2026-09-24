from fastapi import Depends, FastAPI

from .auth import require_service_token
from .registry import get_manifest


app = FastAPI(
    title="ATL Research Agent Service",
    version="1.0.0",
)


@app.get(
    "/manifest",
    dependencies=[
        Depends(require_service_token)
    ],
)
def manifest(agent_id: str):
    return get_manifest(agent_id)
