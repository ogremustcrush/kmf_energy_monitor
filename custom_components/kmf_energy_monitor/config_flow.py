from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.dhcp import DhcpServiceInfo
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

    def __init__(self) -> None:
        self._discovered_host: str | None = None
        self._discovered_hostname: str | None = None
        self._discovered_mac: str | None = None

    # ── Manual setup ──────────────────────────────────────────────────────────

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

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_RECONNECT_DELAY, default=DEFAULT_RECONNECT_DELAY): int,
            }),
            errors=errors,
        )

    # ── DHCP discovery ────────────────────────────────────────────────────────

    async def async_step_dhcp(self, discovery_info: DhcpServiceInfo) -> FlowResult:
        """Triggered when HA sees a DHCP request matching our MAC/hostname filter."""
        mac = discovery_info.macaddress
        await self.async_set_unique_id(mac)
        # If already configured, silently update the stored IP in case it changed.
        self._abort_if_unique_id_configured(updates={CONF_HOST: discovery_info.ip})

        self._discovered_host = discovery_info.ip
        self._discovered_hostname = discovery_info.hostname
        self._discovered_mac = mac

        self.context["title_placeholders"] = {"name": discovery_info.hostname}
        return await self.async_step_dhcp_confirm()

    async def async_step_dhcp_confirm(self, user_input=None) -> FlowResult:
        """Ask the user to confirm the discovered device."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"KM-F Energy Monitor ({self._discovered_hostname})",
                data={
                    CONF_HOST: self._discovered_host,
                    CONF_PORT: DEFAULT_PORT,
                    CONF_RECONNECT_DELAY: DEFAULT_RECONNECT_DELAY,
                },
            )

        return self.async_show_form(
            step_id="dhcp_confirm",
            description_placeholders={
                "hostname": self._discovered_hostname,
                "host": self._discovered_host,
            },
        )
