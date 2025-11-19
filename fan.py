from __future__ import annotations

from homeassistant.components.fan import (
    FanEntity,
    FanEntityFeature,
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

    async_add_entities([BskZephyrFan(coordinator, client, entry.entry_id)], True)


def _map_percentage_to_device(percentage: int) -> int:
    device_min = 22
    device_max = 80
    return round(device_min + (device_max - device_min) * (percentage / 100))


def _map_device_to_percentage(speed: int) -> int:
    device_min = 22
    device_max = 80
    if speed <= device_min:
        return 0
    if speed >= device_max:
        return 100
    return round((speed - device_min) * 100 / (device_max - device_min))


class BskZephyrFan(CoordinatorEntity, FanEntity):
    _attr_has_entity_name = True
    _attr_name = "Fan"
    _attr_icon = "mdi:fan"
    _attr_supported_features = FanEntityFeature.SET_SPEED

    def __init__(self, coordinator, client, unique_base: str) -> None:
        super().__init__(coordinator)
        self._client = client
        self._attr_unique_id = f"{unique_base}_fan"

    @property
    def is_on(self) -> bool | None:
        # Prefer power state from coordinator
        power = str(self.coordinator.data.get("power", "")).upper()
        if power in ("ON", "OFF"):
            return power == "ON"

        # Fallback: infer from fan speed
        speed = self.coordinator.data.get("fan_speed")
        try:
            speed = int(speed)
        except (TypeError, ValueError):
            return None
        return speed > 22

    @property
    def percentage(self) -> int | None:
        speed = self.coordinator.data.get("fan_speed")
        if speed is None:
            return None
        try:
            speed = int(speed)
        except (TypeError, ValueError):
            return None
        return _map_device_to_percentage(speed)

    async def async_turn_on(self, **kwargs) -> None:
        percentage = kwargs.get("percentage")
        if percentage is not None:
            device_speed = _map_percentage_to_device(percentage)
            await self._client.set_fan_speed(device_speed)
        else:
            await self._client.power_on()

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self._client.power_off()
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        device_speed = _map_percentage_to_device(percentage)
        await self._client.set_fan_speed(device_speed)
        await self.coordinator.async_request_refresh()