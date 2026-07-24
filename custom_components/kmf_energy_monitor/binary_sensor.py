from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import KmfCoordinator
from .entity import KmfBase


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: KmfCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KmfCharging(coordinator, entry)])


class KmfCharging(KmfBase, BinarySensorEntity):
    _attr_unique_id = "kmf_charging"
    _attr_name = "Charging"
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.charging
