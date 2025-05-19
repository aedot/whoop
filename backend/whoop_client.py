"""Tools for acquiring and analyzing Whoop API data.

WHOOP is a wearable strap for monitoring sleep, activity, and workouts. Learn more about
WHOOP at https://www.whoop.com.

WHOOP API documentation can be found at https://developer.whoop.com/api.

Examples:
    Loading environment variables:
        import os
        from dotenv import load_dotenv

        load_dotenv()

        username = os.getenv("USERNAME") or ""
        password = os.getenv("PASSWORD") or ""

    Creating a client:
        import whoop as wh

        client = wh.WhoopClient(username, password)
        ...

        with wh.WhoopClient(username, password) as client:
            ...

    Making requests:
        client = wh.WhoopClient(username, password)

        sleep = client.get_sleep_collection()
        recovery = client.get_recovery_collectuon()

        print(sleep)
        print(recovery)

Attributes:
    AUTH_URL (str): Base URL for authorization requests.
    REQUEST_URL (str): Base URL for API requests.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

import requests
from authlib.common.urls import extract_params

AUTH_URL = "https://api-7.whoop.com"
REQUEST_URL = "https://api.prod.whoop.com/developer"

logger = logging.getLogger(__name__)


def _auth_password_json(_client, _method, uri, headers, body):
    body = json.dumps(dict(extract_params(body)))
    headers["Content-Type"] = "application/json"
    return uri, headers, body


class WhoopClient:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token: dict[str, Any] = {}
        self.token_expires: Optional[datetime] = None
        self._authenticate()

    def _authenticate(self):
        logger.info("Authenticating with WHOOP API...")
        token_url = f"{AUTH_URL}/oauth/token"
        response = self.session.post(
            token_url,
            json={
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        raw_token = response.json()

        raw_token["token_type"] = "Bearer"
        self.token = raw_token

        self.token_expires = datetime.utcnow() + timedelta(seconds=self.token.get("expires_in", 3600))

        self.session.headers.update({
            "Authorization": f"Bearer {self.token['access_token']}"
        })
        logger.info("Authentication successful.")

    def _build_params(self, start: Optional[str], end: Optional[str]) -> dict[str, str]:
        return {k: v for k, v in {"start": start, "end": end}.items() if v}

    def _default_dates(self, days: int = 7) -> tuple[str, str]:
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        return start.isoformat() + "Z", end.isoformat() + "Z"

    def _get(self, endpoint: str, params: dict[str, Any] = None) -> Any:  # type: ignore
        url = f"{REQUEST_URL}{endpoint}"
        response = self.session.get(url, params=params or {})
        if response.status_code == 401:
            logger.warning("Token expired. Re-authenticating...")
            self._authenticate()
            response = self.session.get(url, params=params or {})
        response.raise_for_status()
        return response.json()

    def get_user_profile(self) -> dict[str, Any]:
        return self._get("/v1/user/profile/basic")

    def get_sleep_collection(self, start: Optional[str] = None, end: Optional[str] = None) -> list[dict[str, Any]]:
        if not start or not end:
            start, end = self._default_dates()
        return self._get("/v1/activity/sleep", self._build_params(start, end))

    def get_recovery_collection(self, start: Optional[str] = None, end: Optional[str] = None) -> list[dict[str, Any]]:
        if not start or not end:
            start, end = self._default_dates()
        return self._get("/v1/recovery", self._build_params(start, end))

    def get_cycle_collection(self, start: Optional[str] = None, end: Optional[str] = None) -> list[dict[str, Any]]:
        if not start or not end:
            start, end = self._default_dates()
        return self._get("/v1/cycle", self._build_params(start, end))

    def get_workout_collection(self, start: Optional[str] = None, end: Optional[str] = None) -> list[dict[str, Any]]:
        if not start or not end:
            start, end = self._default_dates()
        return self._get("/v1/activity/workout", self._build_params(start, end))

    def close(self):
        self.session.close()

    def __enter__(self) -> WhoopClient:
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()