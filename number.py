from __future__ import annotations

from homeassistant.components.number import (
    NumberEntity,
    NumberMode,
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
    client = data["client"]

    async_add_entities(
        [BskZephyrHumidityTargetNumber(coordinator, client, entry.entry_id)],
        True,
    )


class BskZephyrHumidityTargetNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Humidity Target"
    _attr_mode = NumberMode.AUTO
    _attr_native_unit_of_measurement = "%"
    _attr_native_min_value = 35
    _attr_native_max_value = 100
    _attr_native_step = 1.0

    def __init__(self, coordinator, client, unique_base: str) -> None:
        super().__init__(coordinator)
        self._client = client
        self._attr_unique_id = f"{unique_base}_humidity_target"

    @property
    def native_value(self) -> float | None:
        val = self.coordinator.data.get("set_humidity")
        if val is None:
            return None
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        level = int(round(value))
        await self._client.set_humidity_level(level)
        await self.coordinator.async_request_refresh()