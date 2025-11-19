from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_IP, DEFAULT_NAME


class BskZephyrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BSK Zephyr."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            ip = user_input[CONF_IP]

            # You could perform a quick connection test here if you want.
            await self.async_set_unique_id(ip)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"{DEFAULT_NAME} ({ip})",
                data={CONF_IP: ip},
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_IP): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                )
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)