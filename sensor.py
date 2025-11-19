from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data[DATA_COORDINATOR]

    entities: list[SensorEntity] = [
        BskZephyrTemperatureSensor(coordinator, entry.entry_id),
        BskZephyrHumiditySensor(coordinator, entry.entry_id),
        BskZephyrRssiSensor(coordinator, entry.entry_id),
        BskZephyrModeSensor(coordinator, entry.entry_id),
        BskZephyrSetHumiditySensor(coordinator, entry.entry_id),
        BskZephyrHumidityBoostSensor(coordinator, entry.entry_id),
        BskZephyrFilterTimerSensor(coordinator, entry.entry_id),
        BskZephyrHygieneStatusSensor(coordinator, entry.entry_id),
        BskZephyrBuzzerStateSensor(coordinator, entry.entry_id),
    ]
    async_add_entities(entities, True)


class BskZephyrBaseSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, unique_base: str, name_suffix: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{unique_base}_{name_suffix}"


class BskZephyrTemperatureSensor(BskZephyrBaseSensor):
    _attr_name = "Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "°C"

    def __init__(self, coordinator, unique_base: str) -> None:
        super().__init__(coordinator, unique_base, "temperature")

    @property
    def native_value(self):
        return self.coordinator.data.get("temperature")


class BskZephyrHumiditySensor(BskZephyrBaseSensor):
    _attr_name = "Humidity"
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"

    def __init__(self, coordinator, unique_base: str) -> None:
        super().__init__(coordinator, unique_base, "humidity")

    @property
    def native_value(self):
        return self.coordinator.data.get("humidity")


class BskZephyrRssiSensor(BskZephyrBaseSensor):
    _attr_name = "WiFi RSSI"
    _attr_native_unit_of_measurement = "dBm"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, unique_base: str) -> None:
        super().__init__(coordinator, unique_base, "rssi")

    @property
    def native_value(self):
        return self.coordinator.data.get("rssi")


class BskZephyrModeSensor(BskZephyrBaseSensor):
    _attr_name = "Operation Mode"

    def __init__(self, coordinator, unique_base: str) -> None:
        super().__init__(coordinator, unique_base, "operation_mode")

    @property
    def native_value(self):
        return self.coordinator.data.get("operation_mode")


class BskZephyrSetHumiditySensor(BskZephyrBaseSensor):
    _attr_name = "Set Humidity"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, unique_base: str) -> None:
        super().__init__(coordinator, unique_base, "set_humidity")

    @property
    def native_value(self):
        return self.coordinator.data.get("set_humidity")


class BskZephyrHumidityBoostSensor(BskZephyrBaseSensor):
    _attr_name = "Humidity Boost"

    def __init__(self, coordinator, unique_base: str) -> None:
        super().__init__(coordinator, unique_base, "humidity_boost")

    @property
    def native_value(self):
        return self.coordinator.data.get("humidity_boost")


class BskZephyrFilterTimerSensor(BskZephyrBaseSensor):
    _attr_name = "Filter Timer"
    _attr_native_unit_of_measurement = "h"

    def __init__(self, coordinator, unique_base: str) -> None:
        super().__init__(coordinator, unique_base, "filter_timer")

    @property
    def native_value(self):
        return self.coordinator.data.get("filter_timer")


class BskZephyrHygieneStatusSensor(BskZephyrBaseSensor):
    _attr_name = "Hygiene Status"

    def __init__(self, coordinator, unique_base: str) -> None:
        super().__init__(coordinator, unique_base, "hygiene_status")

    @property
    def native_value(self):
        return self.coordinator.data.get("hygiene_status")


class BskZephyrBuzzerStateSensor(BskZephyrBaseSensor):
    _attr_name = "Buzzer State"

    def __init__(self, coordinator, unique_base: str) -> None:
        super().__init__(coordinator, unique_base, "buzzer_state")

    @property
    def native_value(self):
        # 0/1 from parsed HTML; we keep it as-is
        return self.coordinator.data.get("buzzer")