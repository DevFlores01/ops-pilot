import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(
    name="X_API_Key",
    auto_error=False,
)


async def require_api_key(
    api_key: str | None = Security(api_key_header),
) -> None:
    expected_key = settings.opspilot_api_key

    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "APIKey"},
        )
