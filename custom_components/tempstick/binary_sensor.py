"""TempStick binary sensor platform — alert state."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, API_KEY_ALERT_ACTIVE
from .coordinator import TempStickCoordinator
from .entity_base import TempStickEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TempStick binary sensor entities."""
    coordinator: TempStickCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TempStickAlertSensor(coordinator, sensor_id)
        for sensor_id in coordinator.data
    )


class TempStickAlertSensor(TempStickEntity, BinarySensorEntity):
    """Binary sensor that is ON when the TempStick has an active alert."""

    _attr_name = "Alert"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: TempStickCoordinator, sensor_id: str) -> None:
        super().__init__(coordinator, sensor_id)
        self._attr_unique_id = f"{sensor_id}_alert"

    @property
    def is_on(self) -> bool | None:
        """Return True when an alert is active."""
        raw = self._sensor_data.get(API_KEY_ALERT_ACTIVE)
        if raw is None:
            return None
        return bool(raw)
