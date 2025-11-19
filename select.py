from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR

OPTIONS = ["Cycle", "Intake", "Exhaust"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data[DATA_COORDINATOR]
    client = data["client"]

    async_add_entities([BskZephyrModeSelect(coordinator, client, entry.entry_id)], True)


class BskZephyrModeSelect(CoordinatorEntity, SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Mode"
    _attr_options = OPTIONS

    def __init__(self, coordinator, client, unique_base: str) -> None:
        super().__init__(coordinator)
        self._client = client
        self._attr_unique_id = f"{unique_base}_mode"

    @property
    def current_option(self) -> str | None:
        mode = self.coordinator.data.get("operation_mode")
        if not mode:
            return None
        # Normalise: "Cycle", "Intake", "Exhaust"
        return mode.capitalize()

    async def async_select_option(self, option: str) -> None:
        if option not in OPTIONS:
            raise ValueError(f"Unsupported mode: {option}")

        if option == "Cycle":
            await self._client.set_mode_cycle()
        elif option == "Intake":
            await self._client.set_mode_intake()
        elif option == "Exhaust":
            await self._client.set_mode_exhaust()

        await self.coordinator.async_request_refresh()