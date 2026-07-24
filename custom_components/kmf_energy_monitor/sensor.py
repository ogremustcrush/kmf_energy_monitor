from __future__ import annotations

from typing import Any

from homeassistant.const import EntityCategory
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import KmfCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: KmfCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        KmfVoltage(coordinator, entry),
        KmfCurrent(coordinator, entry),
        KmfPower(coordinator, entry),
        KmfSOC(coordinator, entry),
        KmfRemainingAh(coordinator, entry),
        KmfFullCapacityAh(coordinator, entry),
        KmfChargeEnergy(coordinator, entry),
        KmfDischargeEnergy(coordinator, entry),
        KmfChargeStatus(coordinator, entry),
        KmfEstimatedTime(coordinator, entry),
        KmfDate(coordinator, entry),
        KmfTime(coordinator, entry),

        # Diagnostic raw fields (disabled by default)
        KmfField6(coordinator, entry),
        KmfField7(coordinator, entry),
        KmfField8(coordinator, entry),
    ]

    async_add_entities(entities)


class KmfBase(CoordinatorEntity[KmfCoordinator], SensorEntity):
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


class KmfVoltage(KmfBase):
    _attr_unique_id = "kmf_voltage"
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "V"
    _attr_name = "Battery voltage"

    @property
    def native_value(self):
        return self.coordinator.data.voltage


class KmfCurrent(KmfBase):
    _attr_unique_id = "kmf_current"
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "A"
    _attr_name = "Battery current"

    @property
    def native_value(self):
        return self.coordinator.data.current


class KmfPower(KmfBase):
    _attr_unique_id = "kmf_power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "W"
    _attr_name = "Battery power"

    @property
    def native_value(self):
        return self.coordinator.data.power


class KmfSOC(KmfBase):
    _attr_unique_id = "kmf_soc"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_name = "Battery state of charge"

    @property
    def native_value(self):
        return self.coordinator.data.soc


class KmfRemainingAh(KmfBase):
    _attr_unique_id = "kmf_remaining_ah"
    _attr_native_unit_of_measurement = "Ah"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "Battery remaining capacity"

    @property
    def native_value(self):
        return self.coordinator.data.remaining_ah


class KmfFullCapacityAh(KmfBase):
    _attr_unique_id = "kmf_full_capacity_ah"
    _attr_native_unit_of_measurement = "Ah"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "Battery nominal capacity"

    @property
    def native_value(self):
        return self.coordinator.data.full_capacity_ah


class KmfChargeEnergy(KmfBase):
    _attr_unique_id = "kmf_charge_energy"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "kWh"
    _attr_name = "Charge energy"

    @property
    def native_value(self):
        return self.coordinator.data.charge_energy_kwh


class KmfDischargeEnergy(KmfBase):
    _attr_unique_id = "kmf_discharge_energy"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "kWh"
    _attr_name = "Discharge energy"

    @property
    def native_value(self):
        return self.coordinator.data.discharge_energy_kwh


class KmfChargeStatus(KmfBase):
    _attr_unique_id = "kmf_charge_status"
    _attr_name = "Charge status"

    @property
    def native_value(self):
        return self.coordinator.data.charge_status


class KmfEstimatedTime(KmfBase):
    _attr_unique_id = "kmf_estimated_time"
    _attr_name = "Estimated time"

    @property
    def native_value(self):
        return self.coordinator.data.est_time


class KmfDate(KmfBase):
    _attr_unique_id = "kmf_date"
    _attr_name = "Device date"

    @property
    def native_value(self):
        return self.coordinator.data.date


class KmfTime(KmfBase):
    _attr_unique_id = "kmf_time"
    _attr_name = "Device time"

    @property
    def native_value(self):
        return self.coordinator.data.time


# -------------------------
# Diagnostic raw fields
# -------------------------

class KmfField6(KmfBase):
    _attr_unique_id = "kmf_field6"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_name = "field6"

    @property
    def native_value(self):
        return self.coordinator.data.field6


class KmfField7(KmfBase):
    _attr_unique_id = "kmf_field7"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_name = "field7"

    @property
    def native_value(self):
        return self.coordinator.data.field7


class KmfField8(KmfBase):
    _attr_unique_id = "kmf_field8"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_name = "field8"

    @property
    def native_value(self):
        return self.coordinator.data.field8
