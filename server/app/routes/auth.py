"""
Auth API routes.

Proxies Kratos login/registration flows through the app's backend so the
frontend never talks to Kratos directly (no CORS issues, httpOnly cookies).
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from .. import config
from ..auth import (
    create_login_flow,
    create_registration_flow,
    get_current_user,
    submit_login_flow,
    submit_registration_flow,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    identifier: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str = ""
    last_name: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _set_session_cookie(response: Response, session_token: str) -> None:
    """Set the session token as an httpOnly cookie."""
    response.set_cookie(
        key=config.COOKIE_NAME,
        value=session_token,
        httponly=config.COOKIE_HTTPONLY,
        secure=config.COOKIE_SECURE,
        samesite=config.COOKIE_SAMESITE,
        path="/",
    )


def _extract_user(session: dict) -> dict:
    """Extract user info from a Kratos session response."""
    identity = session.get("identity", {})
    traits = identity.get("traits", {})
    name = traits.get("name", {}) or {}
    return {
        "id": identity.get("id"),
        "email": traits.get("email"),
        "first_name": name.get("first", ""),
        "last_name": name.get("last", ""),
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/login")
async def login(body: LoginRequest, response: Response):
    """
    Log in with email/password.

    Creates a Kratos API login flow, submits the credentials, and sets
    an httpOnly session cookie on success.
    """
    if not config.AUTH_ENABLED:
        raise HTTPException(status_code=400, detail="Auth is disabled")

    try:
        flow = await create_login_flow()
        flow_id = flow.get("id")
        if not flow_id:
            raise HTTPException(status_code=500, detail="Failed to create login flow")

        session = await submit_login_flow(flow_id, body.identifier, body.password)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error: %s", e)
        raise HTTPException(status_code=500, detail="Login failed") from e

    session_token = session.get("session_token")
    if not session_token:
        raise HTTPException(status_code=500, detail="No session token returned")

    _set_session_cookie(response, session_token)
    return _extract_user(session.get("session", session))


@router.post("/register")
async def register(body: RegisterRequest, response: Response):
    """
    Register a new account.

    Creates a Kratos API registration flow, submits the data, and sets
    an httpOnly session cookie on success (auto-login after registration).
    """
    if not config.AUTH_ENABLED:
        raise HTTPException(status_code=400, detail="Auth is disabled")

    try:
        flow = await create_registration_flow()
        flow_id = flow.get("id")
        if not flow_id:
            raise HTTPException(
                status_code=500, detail="Failed to create registration flow"
            )

        session = await submit_registration_flow(
            flow_id, body.email, body.password, body.first_name, body.last_name
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration error: %s", e)
        raise HTTPException(status_code=500, detail="Registration failed") from e

    session_token = session.get("session_token")
    if not session_token:
        raise HTTPException(status_code=500, detail="No session token returned")

    _set_session_cookie(response, session_token)
    return _extract_user(session.get("session", session))


@router.get("/session")
async def get_session(user: dict = Depends(get_current_user)):
    """Return the current authenticated user's info."""
    return user


@router.post("/logout")
async def logout(response: Response):
    """Clear the session cookie."""
    response.delete_cookie(
        key=config.COOKIE_NAME,
        path="/",
    )
    return {"status": "ok"}
