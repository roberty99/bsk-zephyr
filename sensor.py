from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BskZephyrEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    add([
        Temp(coordinator),
        Humid(coordinator),
        RSSI(coordinator),
        Mode(coordinator),
        SetHumidity(coordinator),
        HumidityBoost(coordinator),
        FilterTimer(coordinator),
        HygieneStatus(coordinator),
        BuzzerState(coordinator),
    ])


class BaseSensor(BskZephyrEntity, SensorEntity):
    """Base sensor inheriting device + coordinator logic."""

    def __init__(self, coordinator, uid):
        super().__init__(coordinator, uid)


class Temp(BaseSensor):
    _attr_name = "Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "°C"

    def __init__(self, coordinator):
        super().__init__(coordinator, "temperature")

    @property
    def native_value(self):
        return self.coordinator.data.get("temperature")


class Humid(BaseSensor):
    _attr_name = "Humidity"
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"

    def __init__(self, coordinator):
        super().__init__(coordinator, "humidity")

    @property
    def native_value(self):
        return self.coordinator.data.get("humidity")


class RSSI(BaseSensor):
    _attr_name = "WiFi RSSI"
    _attr_native_unit_of_measurement = "dBm"

    def __init__(self, coordinator):
        super().__init__(coordinator, "rssi")

    @property
    def native_value(self):
        return self.coordinator.data.get("rssi")


class Mode(BaseSensor):
    _attr_name = "Operation Mode"

    def __init__(self, coordinator):
        super().__init__(coordinator, "operation_mode")

    @property
    def native_value(self):
        return self.coordinator.data.get("operation_mode")


class SetHumidity(BaseSensor):
    _attr_name = "Set Humidity"
    _attr_native_unit_of_measurement = "%"

    def __init__(self, coordinator):
        super().__init__(coordinator, "set_humidity")

    @property
    def native_value(self):
        return self.coordinator.data.get("set_humidity")


class HumidityBoost(BaseSensor):
    _attr_name = "Humidity Boost"

    def __init__(self, coordinator):
        super().__init__(coordinator, "humidity_boost")

    @property
    def native_value(self):
        return self.coordinator.data.get("humidity_boost")


class FilterTimer(BaseSensor):
    _attr_name = "Filter Timer"
    _attr_native_unit_of_measurement = "h"

    def __init__(self, coordinator):
        super().__init__(coordinator, "filter_timer")

    @property
    def native_value(self):
        return self.coordinator.data.get("filter_timer")


class HygieneStatus(BaseSensor):
    _attr_name = "Hygiene Status"

    def __init__(self, coordinator):
        super().__init__(coordinator, "hygiene_status")

    @property
    def native_value(self):
        return self.coordinator.data.get("hygiene_status")


class BuzzerState(BaseSensor):
    _attr_name = "Buzzer State"

    def __init__(self, coordinator):
        super().__init__(coordinator, "buzzer_state")

    @property
    def native_value(self):
        return self.coordinator.data.get("buzzer")