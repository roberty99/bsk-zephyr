from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class BskZephyrEntity(CoordinatorEntity):
    """Base entity for all BSK Zephyr entities."""

    def __init__(self, coordinator, unique_id_suffix: str):
        super().__init__(coordinator)

        device_id = coordinator.data.get("device_id")
        self._attr_unique_id = f"{device_id}_{unique_id_suffix}"

    @property
    def device_info(self):
        data = self.coordinator.data

        return {
            "identifiers": {(DOMAIN, data.get("device_id"))},
            "name": f"BSK Zephyr {data.get('device_id')}",
            "manufacturer": "BSK",
            "model": data.get("model", "Zephyr"),
            "sw_version": data.get("version"),
            "connections": {("ip", data.get("ip"))},
        }