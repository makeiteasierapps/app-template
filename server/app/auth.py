"""
Kratos authentication module.

When AUTH_ENABLED is true, validates sessions against the Ory Kratos public API.
When AUTH_ENABLED is false (local dev), returns a mock user.
"""

import logging
from typing import Optional

import httpx
from fastapi import HTTPException, Request, status

from . import config

logger = logging.getLogger(__name__)

_http_client: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            base_url=config.KRATOS_PUBLIC_URL,
            timeout=30.0,
        )
    return _http_client


# ---------------------------------------------------------------------------
# Kratos API flow helpers
# ---------------------------------------------------------------------------


async def create_login_flow() -> dict:
    """Create a Kratos API login flow."""
    client = _get_client()
    resp = await client.get("/self-service/login/api")
    resp.raise_for_status()
    return resp.json()


async def submit_login_flow(flow_id: str, identifier: str, password: str) -> dict:
    """Submit credentials to a Kratos login flow. Returns session dict on success."""
    client = _get_client()
    resp = await client.post(
        f"/self-service/login?flow={flow_id}",
        json={
            "method": "password",
            "identifier": identifier,
            "password": password,
        },
    )
    if resp.status_code == 400:
        # Kratos returns 400 with validation errors in the flow body
        data = resp.json()
        ui_messages = data.get("ui", {}).get("messages", [])
        node_messages = []
        for node in data.get("ui", {}).get("nodes", []):
            node_messages.extend(node.get("messages", []))
        all_messages = ui_messages + node_messages
        error_text = (
            "; ".join(m.get("text", "") for m in all_messages) or "Invalid credentials"
        )
        raise HTTPException(status_code=401, detail=error_text)
    resp.raise_for_status()
    return resp.json()


async def create_registration_flow() -> dict:
    """Create a Kratos API registration flow."""
    client = _get_client()
    resp = await client.get("/self-service/registration/api")
    resp.raise_for_status()
    return resp.json()


async def submit_registration_flow(
    flow_id: str,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
) -> dict:
    """Submit registration data to a Kratos registration flow."""
    client = _get_client()
    payload = {
        "method": "password",
        "password": password,
        "traits": {
            "email": email,
        },
    }
    if first_name or last_name:
        payload["traits"]["name"] = {}
        if first_name:
            payload["traits"]["name"]["first"] = first_name
        if last_name:
            payload["traits"]["name"]["last"] = last_name

    resp = await client.post(
        f"/self-service/registration?flow={flow_id}",
        json=payload,
    )
    if resp.status_code == 400:
        data = resp.json()
        ui_messages = data.get("ui", {}).get("messages", [])
        node_messages = []
        for node in data.get("ui", {}).get("nodes", []):
            node_messages.extend(node.get("messages", []))
        all_messages = ui_messages + node_messages
        error_text = (
            "; ".join(m.get("text", "") for m in all_messages) or "Registration failed"
        )
        raise HTTPException(status_code=400, detail=error_text)
    resp.raise_for_status()
    return resp.json()


async def validate_session(session_token: str) -> dict:
    """Validate a session token against Kratos. Returns the session dict."""
    client = _get_client()
    resp = await client.get(
        "/sessions/whoami",
        headers={"X-Session-Token": session_token},
    )
    if resp.status_code == 401:
        return None
    resp.raise_for_status()
    return resp.json()


def _extract_user(session: dict) -> dict:
    """Extract a user dict from a Kratos session."""
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
# FastAPI dependency
# ---------------------------------------------------------------------------

MOCK_USER = {
    "id": "00000000-0000-0000-0000-000000000000",
    "email": "dev@localhost",
    "first_name": "Dev",
    "last_name": "User",
}


async def get_current_user(request: Request) -> dict:
    """
    FastAPI dependency that returns the current authenticated user.

    When AUTH_ENABLED is false, returns a mock user for local development.
    When AUTH_ENABLED is true, reads the session cookie and validates it
    against the Kratos public API.
    """
    if not config.AUTH_ENABLED:
        return MOCK_USER

    session_token = request.cookies.get(config.COOKIE_NAME)
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    session = await validate_session(session_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    return _extract_user(session)
