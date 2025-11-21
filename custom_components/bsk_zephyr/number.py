from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BskZephyrEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]

    add([BskZephyrHumidityTarget(coordinator, client)])


class BskZephyrHumidityTarget(BskZephyrEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Humidity Target"
    _attr_mode = NumberMode.AUTO
    _attr_native_unit_of_measurement = "%"
    _attr_native_min_value = 35
    _attr_native_max_value = 100
    _attr_native_step = 1

    def __init__(self, coordinator, client):
        super().__init__(coordinator, "humidity_target")
        self._client = client

    @property
    def native_value(self):
        return float(self.coordinator.data.get("set_humidity", 0))

    async def async_set_native_value(self, value: float):
        await self._client.set_humidity_level(int(value))
        await self.coordinator.async_request_refresh()