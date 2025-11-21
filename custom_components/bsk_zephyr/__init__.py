from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_IP, UPDATE_INTERVAL_SECONDS
from .api import BskZephyrClient, BskZephyrApiError

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "switch", "fan", "select", "number"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    ip = entry.data[CONF_IP]
    session = async_get_clientsession(hass)

    client = BskZephyrClient(ip, session)

    async def _update():
        try:
            return await client.get_device_status()
        except BskZephyrApiError as err:
            raise UpdateFailed(str(err))

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="bsk_zephyr",
        update_method=_update,
        update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload