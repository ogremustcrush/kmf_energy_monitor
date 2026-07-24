from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import KmfCoordinator


class KmfBase(CoordinatorEntity[KmfCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: KmfCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> dict[str, Any]:
        host = self._entry.data["host"]
        return {
            "identifiers": {(DOMAIN, host)},
            "name": f"KM-F Energy Monitor ({host})",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }
