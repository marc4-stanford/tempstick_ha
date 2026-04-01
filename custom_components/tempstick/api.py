"""TempStick API client."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import (
    TEMPSTICK_API_SENSORS,
    TEMPSTICK_API_SENSOR,
    API_KEY_SENSOR_ID,
)

_LOGGER = logging.getLogger(__name__)


class TempStickAuthError(Exception):
    """Raised when authentication fails."""


class TempStickApiError(Exception):
    """Raised when the API returns an unexpected error."""


class TempStickApiClient:
    """Async client for the TempStick cloud API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        self._api_key = api_key
        self._session = session
        self._headers = {
            "X-API-KEY": api_key,
            "Accept": "application/json",
        }

    async def async_get_sensors(self) -> list[dict[str, Any]]:
        """Fetch all sensors associated with the account."""
        try:
            async with self._session.get(
                TEMPSTICK_API_SENSORS, headers=self._headers, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 401:
                    raise TempStickAuthError("Invalid API key")
                if resp.status != 200:
                    raise TempStickApiError(f"Unexpected status: {resp.status}")
                data = await resp.json()
                # API returns {"status":"success","data":{"items":[...]}}
                return data.get("data", {}).get("items", [])
        except aiohttp.ClientError as err:
            raise TempStickApiError(f"Network error: {err}") from err

    async def async_get_sensor(self, sensor_id: str) -> dict[str, Any]:
        """Fetch latest data for a single sensor."""
        url = f"{TEMPSTICK_API_SENSOR}/{sensor_id}"
        try:
            async with self._session.get(
                url, headers=self._headers, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 401:
                    raise TempStickAuthError("Invalid API key")
                if resp.status != 200:
                    raise TempStickApiError(f"Unexpected status: {resp.status}")
                data = await resp.json()
                return data.get("data", {})
        except aiohttp.ClientError as err:
            raise TempStickApiError(f"Network error: {err}") from err

    async def async_validate_api_key(self) -> bool:
        """Validate the API key by attempting a sensor list fetch."""
        try:
            await self.async_get_sensors()
            return True
        except TempStickAuthError:
            return False
