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
    """Map 0–100% to device speed range 22–80."""
    return round(DEVICE_MIN + (DEVICE_MAX - DEVICE_MIN) * (pct / 100))


def speed_to_pct(speed: int) -> int:
    """Map device speed 22–80 to 0–100%."""
    if speed <= DEVICE_MIN:
        return 0
    if speed >= DEVICE_MAX:
        return 100
    return round((speed - DEVICE_MIN) * 100 / (DEVICE_MAX - DEVICE_MIN))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    client = data["client"]

    add_entities([BskZephyrFan(coordinator, client)])


class BskZephyrFan(BskZephyrEntity, FanEntity):
    """Full fan control for BSK Zephyr (power + speed + mode)."""

    _attr_has_entity_name = True
    _attr_name = "Fan"

    # Support on/off, speed and preset modes (Cycle / Intake / Exhaust)
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.PRESET_MODE
    )

    _preset_modes = ["Cycle", "Intake", "Exhaust"]

    def __init__(self, coordinator, client):
        super().__init__(coordinator, "fan")
        self._client = client

    # ---------------------------
    #   STATE (from coordinator)
    # ---------------------------

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

    # --------- PRESET MODES (mode integrated) ---------

    @property
    def preset_modes(self) -> list[str]:
        """Available fan modes."""
        return self._preset_modes

    @property
    def preset_mode(self) -> str | None:
        """Current mode based on operation_mode from status page."""
        mode = str(self.coordinator.data.get("operation_mode", "")).capitalize()
        return mode if mode in self._preset_modes else None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the fan mode: Cycle / Intake / Exhaust."""
        if preset_mode not in self._preset_modes:
            raise ValueError(f"Unsupported preset mode: {preset_mode}")

        if preset_mode == "Cycle":
            await self._client.set_mode_cycle()
        elif preset_mode == "Intake":
            await self._client.set_mode_intake()
        elif preset_mode == "Exhaust":
            await self._client.set_mode_exhaust()

        await self.coordinator.async_request_refresh()

    # --------- ICON (symbols for modes) ---------

    @property
    def icon(self) -> str:
        """Return icon based on current mode."""
        mode = self.preset_mode

        if mode == "Intake":
            return "mdi:arrow-collapse-left"
        if mode == "Exhaust":
            return "mdi:arrow-collapse-right"
        if mode == "Cycle":
            return "mdi:autorenew"

        return "mdi:fan"

    # ---------------------------
    #   CONTROL HANDLERS
    # ---------------------------

    async def async_turn_on(self, *args, **kwargs) -> None:
        """Turn fan ON. Then optionally set speed."""
        percentage = kwargs.get("percentage")

        # Always ensure device power is ON
        await self._client.power_on()

        # Set the speed if provided
        if percentage is not None:
            await self._client.set_fan_speed(pct_to_speed(percentage))

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, *args, **kwargs) -> None:
        """Turn fan OFF (device off)."""
        await self._client.power_off()
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set fan speed. Auto power on if needed."""
        # If currently off, turn on before changing speed
        if not self.is_on:
            await self._client.power_on()

        await self._client.set_fan_speed(pct_to_speed(percentage))
        await self.coordinator.async_request_refresh()
