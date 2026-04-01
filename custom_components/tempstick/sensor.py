"""TempStick sensor platform — temperature, humidity, battery, RSSI, tcTemp."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_TEMPERATURE_UNIT,
    API_KEY_LAST_TEMP,
    API_KEY_LAST_HUMIDITY,
    API_KEY_BATTERY_PCT,
    API_KEY_RSSI,
    API_KEY_TC_MODE,
    API_KEY_TC_TEMP,
    API_KEY_TC_TYPE,
)
from .coordinator import TempStickCoordinator
from .entity_base import TempStickEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class TempStickSensorDescription(SensorEntityDescription):
    """Extends SensorEntityDescription with a value extractor."""
    value_fn: Callable[[dict], Any]


def _temp_value_fn(unit: str) -> Callable[[dict], float | None]:
    """last_temp is always returned in Celsius by the TempStick API."""
    def _fn(data: dict) -> float | None:
        raw = data.get(API_KEY_LAST_TEMP)
        if raw is None:
            return None
        temp_c = float(raw)
        return round(temp_c * 9 / 5 + 32, 1) if unit == "F" else round(temp_c, 1)
    return _fn


def _tc_temp_value_fn(unit: str) -> Callable[[dict], float | None]:
    """Return tcTemp (probe) value. TempStick reports it in Celsius always."""
    def _fn(data: dict) -> float | None:
        raw = data.get(API_KEY_TC_TEMP)
        if raw is None:
            return None
        try:
            temp_c = float(raw)
        except (ValueError, TypeError):
            return None
        # Sentinel: -9999 means no valid probe reading
        if temp_c <= -9990:
            return None
        return round(temp_c * 9 / 5 + 32, 1) if unit == "F" else round(temp_c, 1)
    return _fn


SENSOR_DESCRIPTIONS_BASE: tuple[TempStickSensorDescription, ...] = (
    TempStickSensorDescription(
        key="humidity",
        translation_key="humidity",
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: round(float(d[API_KEY_LAST_HUMIDITY]), 1) if API_KEY_LAST_HUMIDITY in d else None,
    ),
    TempStickSensorDescription(
        key="battery",
        translation_key="battery",
        name="Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: int(d[API_KEY_BATTERY_PCT]) if API_KEY_BATTERY_PCT in d else None,
    ),
    TempStickSensorDescription(
        key="rssi",
        translation_key="rssi",
        name="Signal Strength",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda d: int(d[API_KEY_RSSI]) if API_KEY_RSSI in d else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TempStick sensor entities."""
    coordinator: TempStickCoordinator = hass.data[DOMAIN][entry.entry_id]
    unit = entry.options.get(CONF_TEMPERATURE_UNIT, entry.data.get(CONF_TEMPERATURE_UNIT, "F"))

    temp_description = TempStickSensorDescription(
        key="temperature",
        translation_key="temperature",
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT if unit == "F" else UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_temp_value_fn(unit),
    )

    tc_temp_description = TempStickSensorDescription(
        key="tc_temperature",
        translation_key="tc_temperature",
        name="Probe Temperature",
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT if unit == "F" else UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_tc_temp_value_fn(unit),
    )

    entities: list[TempStickSensor] = []
    for sensor_id, sensor_data in coordinator.data.items():
        # All devices get the standard sensors
        for description in (temp_description,) + SENSOR_DESCRIPTIONS_BASE:
            entities.append(TempStickSensor(coordinator, sensor_id, description))

        # Only add Probe Temperature when thermocouple mode is active (TC_M == 1)
        if int(sensor_data.get(API_KEY_TC_MODE, 0)) == 1:
            tc_type = sensor_data.get(API_KEY_TC_TYPE, "")
            tc_desc_with_type = TempStickSensorDescription(
                key="tc_temperature",
                translation_key="tc_temperature",
                name=f"Probe Temperature (Type {tc_type})" if tc_type else "Probe Temperature",
                native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT if unit == "F" else UnitOfTemperature.CELSIUS,
                device_class=SensorDeviceClass.TEMPERATURE,
                state_class=SensorStateClass.MEASUREMENT,
                value_fn=_tc_temp_value_fn(unit),
            )
            entities.append(TempStickSensor(coordinator, sensor_id, tc_desc_with_type))
            _LOGGER.debug(
                "Sensor %s has thermocouple mode enabled (Type %s) — adding Probe Temperature entity",
                sensor_id, tc_type,
            )

    async_add_entities(entities)


class TempStickSensor(TempStickEntity, SensorEntity):
    """A single measurement sensor for a TempStick device."""

    entity_description: TempStickSensorDescription

    def __init__(
        self,
        coordinator: TempStickCoordinator,
        sensor_id: str,
        description: TempStickSensorDescription,
    ) -> None:
        super().__init__(coordinator, sensor_id)
        self.entity_description = description
        self._attr_unique_id = f"{sensor_id}_{description.key}"

    @property
    def native_value(self):
        """Return the sensor reading."""
        return self.entity_description.value_fn(self._sensor_data)
