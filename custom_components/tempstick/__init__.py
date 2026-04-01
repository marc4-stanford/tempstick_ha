"""TempStick integration for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TempStickApiClient
from .const import DOMAIN, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL, PLATFORMS
from .coordinator import TempStickCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS_LIST = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TempStick from a config entry."""
    api_key = entry.data[CONF_API_KEY]
    poll_interval = entry.options.get(
        CONF_POLL_INTERVAL, entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
    )

    session = async_get_clientsession(hass)
    client = TempStickApiClient(api_key, session)
    coordinator = TempStickCoordinator(hass, client, poll_interval)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_LIST)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS_LIST)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration when options change (e.g. poll interval)."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
