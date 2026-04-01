"""Config flow for TempStick integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TempStickApiClient, TempStickAuthError, TempStickApiError
from .const import (
    DOMAIN,
    CONF_POLL_INTERVAL,
    CONF_TEMPERATURE_UNIT,
    DEFAULT_POLL_INTERVAL,
    TEMPSTICK_API_KEY_DEFAULT,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY, default=TEMPSTICK_API_KEY_DEFAULT): str,
        vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): vol.All(
            int, vol.Range(min=1, max=60)
        ),
        vol.Optional(CONF_TEMPERATURE_UNIT, default="F"): vol.In(["F", "C"]),
    }
)


async def validate_api_key(hass: HomeAssistant, api_key: str) -> None:
    """Validate credentials by attempting a real API call."""
    session = async_get_clientsession(hass)
    client = TempStickApiClient(api_key, session)
    await client.async_get_sensors()  # raises TempStickAuthError on bad key


class TempStickConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial setup config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_api_key(self.hass, user_input[CONF_API_KEY])
            except TempStickAuthError:
                errors["base"] = "invalid_auth"
            except TempStickApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during config flow")
                errors["base"] = "unknown"
            else:
                # Prevent duplicate entries for the same API key
                await self.async_set_unique_id(user_input[CONF_API_KEY][:16])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="TempStick", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return TempStickOptionsFlow(config_entry)


class TempStickOptionsFlow(config_entries.OptionsFlow):
    """Allow changing poll interval and temperature unit after setup."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_POLL_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
                    ),
                ): vol.All(int, vol.Range(min=1, max=60)),
                vol.Optional(
                    CONF_TEMPERATURE_UNIT,
                    default=self.config_entry.options.get(CONF_TEMPERATURE_UNIT, "F"),
                ): vol.In(["F", "C"]),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
