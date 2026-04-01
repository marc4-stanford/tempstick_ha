"""Base entity for TempStick devices."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, API_KEY_SENSOR_NAME, API_KEY_MAC, API_KEY_FIRMWARE, API_KEY_TC_MODE, API_KEY_TC_TYPE
from .coordinator import TempStickCoordinator


class TempStickEntity(CoordinatorEntity[TempStickCoordinator]):
    """Base entity that all TempStick sensors inherit from."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TempStickCoordinator, sensor_id: str) -> None:
        super().__init__(coordinator)
        self._sensor_id = sensor_id

    @property
    def _sensor_data(self) -> dict:
        return self.coordinator.data.get(self._sensor_id, {})

    @property
    def device_info(self) -> DeviceInfo:
        data = self._sensor_data
        tc_mode = int(data.get(API_KEY_TC_MODE, 0))
        tc_type = data.get(API_KEY_TC_TYPE, "")
        model = f"TempStick (Thermocouple Type {tc_type})" if tc_mode == 1 and tc_type else "TempStick"

        return DeviceInfo(
            identifiers={(DOMAIN, self._sensor_id)},
            name=data.get(API_KEY_SENSOR_NAME, f"TempStick {self._sensor_id}"),
            manufacturer="Sensor Industries / Sensaphone",
            model=model,
            sw_version=data.get(API_KEY_FIRMWARE),
            connections={("mac", data[API_KEY_MAC])} if API_KEY_MAC in data else set(),
        )

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self._sensor_id in self.coordinator.data
        )
