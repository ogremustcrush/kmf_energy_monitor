from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_RECONNECT_DELAY,
    DEFAULT_PORT,
    DEFAULT_RECONNECT_DELAY,
)


class KmfConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle KM-F Energy Monitor config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"KM-F Energy Monitor ({host})",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_RECONNECT_DELAY, default=DEFAULT_RECONNECT_DELAY): int,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
