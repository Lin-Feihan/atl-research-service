import os
import secrets

from fastapi import Header, HTTPException


def require_service_token(
    x_service_token: str | None = Header(
        default=None,
        alias="X-Service-Token",
    )
):
    expected_token = os.getenv("X_SERVICE_TOKEN")

    if (
        not expected_token
        or not x_service_token
        or not secrets.compare_digest(
            x_service_token,
            expected_token,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="unauthorized",
        )
