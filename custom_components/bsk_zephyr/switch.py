from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BskZephyrEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]

    add([
        BskZephyrPowerSwitch(coordinator, client),
        BskZephyrBuzzerSwitch(coordinator, client),
    ])


class BskZephyrPowerSwitch(BskZephyrEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Power"

    def __init__(self, coordinator, client):
        super().__init__(coordinator, "power")
        self._client = client

    @property
    def is_on(self):
        power = str(self.coordinator.data.get("power", "")).upper()
        return power == "ON"

    async def async_turn_on(self):
        await self._client.power_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        await self._client.power_off()
        await self.coordinator.async_request_refresh()


class BskZephyrBuzzerSwitch(BskZephyrEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Buzzer"

    def __init__(self, coordinator, client):
        super().__init__(coordinator, "buzzer_switch")
        self._client = client

    @property
    def is_on(self):
        return int(self.coordinator.data.get("buzzer", 0)) == 1

    async def async_turn_on(self):
        await self._client.set_buzzer_state(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        await self._client.set_buzzer_state(False)
        await self.coordinator.async_request_refresh()