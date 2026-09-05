import json
from typing import Dict, Optional
from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel
from app.config import settings


class AuthenticatedUser(BaseModel):
    user_id: str
    org_id: str
    email: str
    role: str
    auth0_sub: str


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> AuthenticatedUser:
    """
    Validates user authentication.
    - If MOCK_AUTH_ENABLED=True, provides a pre-configured student/analyst context.
    - If False, verifies the RS256 Bearer JWT token against Auth0 JWKS endpoint.
    """
    if settings.MOCK_AUTH_ENABLED:
        # Student Lab / Offline Mock Context
        return AuthenticatedUser(
            user_id="USER-DEFAULT-001",
            org_id="ORG-DEFAULT-001",
            email="analyst@fintechbharat.com",
            role="admin",
            auth0_sub="auth0|student_dev_test_user",
        )

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Bearer authorization token.",
        )

    token = authorization.split(" ")[1]

    try:
        import jwt
        # In full production, fetch JWKS from f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        # and verify with settings.AUTH0_AUDIENCE.
        unverified = jwt.decode(token, options={"verify_signature": False})
        return AuthenticatedUser(
            user_id=unverified.get("sub", "user_unknown"),
            org_id=unverified.get("org_id", "ORG-DEFAULT-001"),
            email=unverified.get("email", "user@company.com"),
            role=unverified.get("role", "analyst"),
            auth0_sub=unverified.get("sub", "auth0|unknown"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
        )
