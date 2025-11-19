from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BskZephyrEntity


OPTIONS = ["Cycle", "Intake", "Exhaust"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]

    add([BskZephyrModeSelect(coordinator, client)])


class BskZephyrModeSelect(BskZephyrEntity, SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Mode"
    _attr_options = OPTIONS

    def __init__(self, coordinator, client):
        super().__init__(coordinator, "mode")
        self._client = client

    @property
    def current_option(self):
        mode = str(self.coordinator.data.get("operation_mode", "")).capitalize()
        return mode if mode in OPTIONS else None

    async def async_select_option(self, option: str):
        if option == "Cycle":
            await self._client.set_mode_cycle()
        elif option == "Intake":
            await self._client.set_mode_intake()
        elif option == "Exhaust":
            await self._client.set_mode_exhaust()

        await self.coordinator.async_request_refresh()