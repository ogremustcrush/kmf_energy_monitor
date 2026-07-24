from __future__ import annotations

from homeassistant.const import EntityCategory
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
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

    async_add_entities([
        KmfVoltage(coordinator, entry),
        KmfCurrent(coordinator, entry),
        KmfPower(coordinator, entry),
        KmfSOC(coordinator, entry),
        KmfRemainingAh(coordinator, entry),
        KmfFullCapacityAh(coordinator, entry),
        KmfChargeEnergy(coordinator, entry),
        KmfDischargeEnergy(coordinator, entry),
        KmfChargeStatus(coordinator, entry),
        KmfTimeRemainingMinutes(coordinator, entry),
        KmfEstimatedTime(coordinator, entry),
        KmfDate(coordinator, entry),
        KmfTime(coordinator, entry),
        KmfField6(coordinator, entry),
        KmfField7(coordinator, entry),
        KmfField8(coordinator, entry),
    ])


class KmfSensorBase(KmfBase, SensorEntity):
    pass


class KmfVoltage(KmfSensorBase):
    _attr_unique_id = "kmf_voltage"
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "V"
    _attr_name = "Battery voltage"

    @property
    def native_value(self):
        return self.coordinator.data.voltage


class KmfCurrent(KmfSensorBase):
    _attr_unique_id = "kmf_current"
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "A"
    _attr_name = "Battery current"

    @property
    def native_value(self):
        return self.coordinator.data.current


class KmfPower(KmfSensorBase):
    _attr_unique_id = "kmf_power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "W"
    _attr_name = "Battery power"

    @property
    def native_value(self):
        return self.coordinator.data.power


class KmfSOC(KmfSensorBase):
    _attr_unique_id = "kmf_soc"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_name = "Battery state of charge"

    @property
    def native_value(self):
        return self.coordinator.data.soc


class KmfRemainingAh(KmfSensorBase):
    _attr_unique_id = "kmf_remaining_ah"
    _attr_native_unit_of_measurement = "Ah"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "Battery remaining capacity"

    @property
    def native_value(self):
        return self.coordinator.data.remaining_ah


class KmfFullCapacityAh(KmfSensorBase):
    _attr_unique_id = "kmf_full_capacity_ah"
    _attr_native_unit_of_measurement = "Ah"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Battery nominal capacity"

    @property
    def native_value(self):
        return self.coordinator.data.full_capacity_ah


class KmfChargeEnergy(KmfSensorBase):
    _attr_unique_id = "kmf_charge_energy"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "kWh"
    _attr_name = "Charge energy"

    @property
    def native_value(self):
        return self.coordinator.data.charge_energy_kwh


class KmfDischargeEnergy(KmfSensorBase):
    _attr_unique_id = "kmf_discharge_energy"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "kWh"
    _attr_name = "Discharge energy"

    @property
    def native_value(self):
        return self.coordinator.data.discharge_energy_kwh


class KmfChargeStatus(KmfSensorBase):
    _attr_unique_id = "kmf_charge_status"
    _attr_name = "Charge status"

    @property
    def native_value(self):
        return self.coordinator.data.charge_status


class KmfTimeRemainingMinutes(KmfSensorBase):
    _attr_unique_id = "kmf_time_remaining_minutes"
    _attr_native_unit_of_measurement = "min"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:timer-sand"
    _attr_name = "Time remaining"

    @property
    def native_value(self):
        return self.coordinator.data.time_remaining_minutes


class KmfEstimatedTime(KmfSensorBase):
    _attr_unique_id = "kmf_estimated_time"
    _attr_icon = "mdi:timer-sand"
    _attr_name = "Estimated time"

    @property
    def native_value(self):
        return self.coordinator.data.est_time


class KmfDate(KmfSensorBase):
    _attr_unique_id = "kmf_date"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Device date"

    @property
    def native_value(self):
        return self.coordinator.data.date


class KmfTime(KmfSensorBase):
    _attr_unique_id = "kmf_time"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Device time"

    @property
    def native_value(self):
        return self.coordinator.data.time


class KmfField6(KmfSensorBase):
    _attr_unique_id = "kmf_field6"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_name = "field6"

    @property
    def native_value(self):
        return self.coordinator.data.field6


class KmfField7(KmfSensorBase):
    _attr_unique_id = "kmf_field7"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_name = "field7"

    @property
    def native_value(self):
        return self.coordinator.data.field7


class KmfField8(KmfSensorBase):
    _attr_unique_id = "kmf_field8"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_name = "field8"

    @property
    def native_value(self):
        return self.coordinator.data.field8
