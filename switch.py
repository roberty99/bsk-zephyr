from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
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

    entities: list[SwitchEntity] = [
        BskZephyrPowerSwitch(coordinator, client, entry.entry_id),
        BskZephyrBuzzerSwitch(coordinator, client, entry.entry_id),
    ]

    async_add_entities(entities, True)


class BskZephyrPowerSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Power"

    def __init__(self, coordinator, client, unique_base: str) -> None:
        super().__init__(coordinator)
        self._client = client
        self._attr_unique_id = f"{unique_base}_power"

    @property
    def is_on(self) -> bool:
        power = str(self.coordinator.data.get("power", "")).upper()
        return power == "ON"

    async def async_turn_on(self, **kwargs) -> None:
        await self._client.power_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self._client.power_off()
        await self.coordinator.async_request_refresh()


class BskZephyrBuzzerSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Buzzer"

    def __init__(self, coordinator, client, unique_base: str) -> None:
        super().__init__(coordinator)
        self._client = client
        self._attr_unique_id = f"{unique_base}_buzzer"

    @property
    def is_on(self) -> bool:
        val = self.coordinator.data.get("buzzer")
        try:
            return int(val) == 1
        except (TypeError, ValueError):
            return False

    async def async_turn_on(self, **kwargs) -> None:
        await self._client.set_buzzer_state(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self._client.set_buzzer_state(False)
        await self.coordinator.async_request_refresh()