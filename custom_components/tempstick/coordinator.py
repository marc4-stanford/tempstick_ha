"""DataUpdateCoordinator for TempStick."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TempStickApiClient, TempStickApiError
from .const import DOMAIN, API_KEY_SENSOR_ID

_LOGGER = logging.getLogger(__name__)


class TempStickCoordinator(DataUpdateCoordinator):
    """Polls TempStick cloud for all sensor readings.

    Data shape:
        { "<sensor_id>": { ...raw API sensor dict... }, ... }

    The API returns sensor_id (e.g. "EX00FWNWR3") as the unique device key.
    The numeric "id" field is the account-scoped database row ID and is NOT used.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: TempStickApiClient,
        poll_interval: int,
    ) -> None:
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=poll_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch fresh data from the TempStick API."""
        try:
            sensors = await self.client.async_get_sensors()
        except TempStickApiError as err:
            raise UpdateFailed(f"TempStick API error: {err}") from err

        result = {}
        for s in sensors:
            sid = s.get(API_KEY_SENSOR_ID)
            if sid:
                result[sid] = s
            else:
                _LOGGER.warning("Sensor entry missing sensor_id, skipping: %s", s)
        return result
