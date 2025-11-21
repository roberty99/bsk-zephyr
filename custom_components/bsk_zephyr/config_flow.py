import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_IP


class BskZephyrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            ip = user_input[CONF_IP]

            await self.async_set_unique_id(ip)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"BSK Zephyr ({ip})",
                data={CONF_IP: ip},
            )

        schema = vol.Schema({
            vol.Required(CONF_IP): selector.TextSelector()
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema
        )