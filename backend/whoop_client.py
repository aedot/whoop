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
import requests
from datetime import datetime, time, timedelta
from typing import Any

from authlib.common.urls import extract_params
from authlib.integrations.requests_client import OAuth2Session


AUTH_URL = "https://api-7.whoop.com"
REQUEST_URL = "https://api.prod.whoop.com/developer"


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
        self._authenticate()

    def _authenticate(self):
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

        # Force token_type to Bearer if needed
        raw_token["token_type"] = "Bearer"
        self.token = raw_token

        # Add auth headers to session
        self.session.headers.update({
            "Authorization": f"Bearer {self.token['access_token']}"
        })

    def _get(self, endpoint: str, params: dict[str, Any] = None) -> Any: # type: ignore
        url = f"{REQUEST_URL}{endpoint}"
        response = self.session.get(url, params=params or {})
        response.raise_for_status()
        return response.json()

    def get_user_profile(self) -> dict[str, Any]:
        return self._get("/v1/user/profile/basic")


    def get_sleep_collection(self, start: str = None, end: str = None) -> list[dict[str, Any]]: # type: ignore
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return self._get("/v1/activity/sleep", params)

    def get_recovery_collection(self, start: str = None, end: str = None) -> list[dict[str, Any]]: # type: ignore
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return self._get("/v1/recovery", params)

    def get_cycle_collection(self, start: str = None, end: str = None) -> list[dict[str, Any]]: # type: ignore
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return self._get("/v1/cycle", params)

    def get_workout_collection(self, start: str = None, end: str = None) -> list[dict[str, Any]]: # type: ignore
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return self._get("/v1/activity/workout", params)

    def close(self):
        self.session.close()

    def __enter__(self) -> WhoopClient:
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
