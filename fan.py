from homeassistant.components.fan import (
    FanEntity,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BskZephyrEntity


DEVICE_MIN = 22
DEVICE_MAX = 80


def pct_to_speed(pct: int) -> int:
    return round(DEVICE_MIN + (DEVICE_MAX - DEVICE_MIN) * (pct / 100))


def speed_to_pct(speed: int) -> int:
    if speed <= DEVICE_MIN:
        return 0
    if speed >= DEVICE_MAX:
        return 100
    return round((speed - DEVICE_MIN) * 100 / (DEVICE_MAX - DEVICE_MIN))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    add: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]

    add([BskZephyrFan(coordinator, client)])


class BskZephyrFan(BskZephyrEntity, FanEntity):
    """Full fan control for BSK Zephyr."""

    _attr_has_entity_name = True
    _attr_name = "Fan"

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator, client):
        super().__init__(coordinator, "fan")
        self._client = client

    @property
    def is_on(self) -> bool:
        power = str(self.coordinator.data.get("power", "")).upper()
        return power == "ON"

    @property
    def percentage(self) -> int | None:
        speed = self.coordinator.data.get("fan_speed")
        if speed is None:
            return None
        try:
            return speed_to_pct(int(speed))
        except (TypeError, ValueError):
            return None

    async def async_turn_on(self, *args, **kwargs) -> None:
        """Turn fan ON. Then optionally set speed."""
        percentage = kwargs.get("percentage")

        await self._client.power_on()

        if percentage is not None:
            await self._client.set_fan_speed(pct_to_speed(percentage))

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, *args, **kwargs) -> None:
        """Turn fan OFF."""
        await self._client.power_off()
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set fan speed. Auto power on."""
        if not self.is_on:
            await self._client.power_on()

        await self._client.set_fan_speed(pct_to_speed(percentage))
        await self.coordinator.async_request_refresh()
