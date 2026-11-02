"""Sensor platform for Eopt Home integration (thermostat power & energy)."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
import time

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from sensio_lib import Hub, Thermostat

from .const import CONF_ENABLE_POWER_REPORTING, DOMAIN
from .helpers import device_info

_LOGGER = logging.getLogger(__name__)

_ENERGY_UPDATE_INTERVAL = timedelta(seconds=60)


def _base_thermostat_label(thermostat: Thermostat) -> str:
    """Return the thermostat label stripped of any leading zone name prefix."""
    if thermostat.zone_name and thermostat.name.startswith(f"{thermostat.zone_name} "):
        return thermostat.name.removeprefix(f"{thermostat.zone_name} ")
    return thermostat.name


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eopt Home power and energy sensors from a config entry."""
    enable_power_reporting = entry.options.get(
        CONF_ENABLE_POWER_REPORTING,
        entry.data.get(CONF_ENABLE_POWER_REPORTING, True),
    )

    if not enable_power_reporting:
        ent_reg = er.async_get(hass)
        for reg_entry in er.async_entries_for_config_entry(ent_reg, entry.entry_id):
            if reg_entry.domain == "sensor":
                ent_reg.async_remove(reg_entry.entity_id)
        _LOGGER.debug("Thermostat power/energy reporting is disabled in options")
        return

    data = hass.data[DOMAIN][entry.entry_id]
    hub: Hub = data["hub"]
    sensor_entities: dict[Thermostat, list[SensorEntity]] = data["sensor_entities"]

    entities: list[SensorEntity] = []
    for thermostat in hub.get_thermostats():
        entities.append(
            SensioThermostatPowerSensor(thermostat, entry, sensor_entities)
        )
        entities.append(
            SensioThermostatEnergySensor(thermostat, entry, sensor_entities)
        )

    async_add_entities(entities)
    _LOGGER.debug("Added %d Eopt Home sensor entities", len(entities))


class SensioThermostatPowerSensor(SensorEntity):
    """Live power sensor (W) for a Sensio heated floor thermostat."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(
        self,
        thermostat: Thermostat,
        entry: ConfigEntry,
        sensor_entities: dict[Thermostat, list[SensorEntity]],
    ) -> None:
        """Initialize the thermostat power sensor."""
        self._thermostat = thermostat
        self._sensor_entities = sensor_entities
        self._attr_unique_id = f"{DOMAIN}_{thermostat.unique_id}_power"
        base_label = _base_thermostat_label(thermostat)
        self._attr_name = f"{base_label} Power"
        self._attr_device_info = device_info(
            entry, thermostat.zone_id, thermostat.zone_name
        )

    async def async_added_to_hass(self) -> None:
        """Register this entity for push state updates."""
        self._sensor_entities.setdefault(self._thermostat, []).append(self)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister from push state updates."""
        listeners = self._sensor_entities.get(self._thermostat)
        if listeners and self in listeners:
            listeners.remove(self)

    @property
    def native_value(self) -> float | None:
        """Return the current heating power in Watts."""
        return self._thermostat.last_hour_heating


class SensioThermostatEnergySensor(RestoreSensor):
    """Cumulative energy sensor (kWh) for a Sensio heated floor thermostat."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_suggested_display_precision = 3

    def __init__(
        self,
        thermostat: Thermostat,
        entry: ConfigEntry,
        sensor_entities: dict[Thermostat, list[SensorEntity]],
    ) -> None:
        """Initialize the thermostat energy sensor."""
        self._thermostat = thermostat
        self._sensor_entities = sensor_entities
        self._attr_unique_id = f"{DOMAIN}_{thermostat.unique_id}_energy"
        base_label = _base_thermostat_label(thermostat)
        self._attr_name = f"{base_label} Energy"
        self._attr_device_info = device_info(
            entry, thermostat.zone_id, thermostat.zone_name
        )
        self._total_kwh: float = 0.0
        self._last_update_mono: float | None = None
        self._last_power_w: float = 0.0

    async def async_added_to_hass(self) -> None:
        """Restore previous cumulative kWh total and register for updates."""
        await super().async_added_to_hass()
        if (last_data := await self.async_get_last_sensor_data()) is not None:
            try:
                if last_data.native_value is not None:
                    self._total_kwh = max(0.0, float(last_data.native_value))
            except (TypeError, ValueError):
                self._total_kwh = 0.0

        self._last_update_mono = time.monotonic()
        self._last_power_w = self._thermostat.last_hour_heating or 0.0

        self._sensor_entities.setdefault(self._thermostat, []).append(self)
        self.async_on_remove(
            async_track_time_interval(
                self.hass,
                self._async_periodic_update,
                _ENERGY_UPDATE_INTERVAL,
            )
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unregister from push state updates."""
        listeners = self._sensor_entities.get(self._thermostat)
        if listeners and self in listeners:
            listeners.remove(self)

    @callback
    def _accumulate(self) -> None:
        """Integrate power (W) over elapsed time into cumulative kWh."""
        now = time.monotonic()
        if self._last_update_mono is not None:
            elapsed_hours = max(0.0, (now - self._last_update_mono) / 3600.0)
            if self._last_power_w > 0.0 and elapsed_hours > 0.0:
                self._total_kwh += (self._last_power_w / 1000.0) * elapsed_hours
        self._last_update_mono = now
        self._last_power_w = self._thermostat.last_hour_heating or 0.0

    @callback
    def _async_write_ha_state(self) -> None:
        """Integrate elapsed energy before writing state to Home Assistant."""
        self._accumulate()
        super()._async_write_ha_state()

    @callback
    def _async_periodic_update(self, _now: datetime) -> None:
        """Periodically flush energy accumulation while actively heating."""
        current_power = self._thermostat.last_hour_heating or 0.0
        if self._last_power_w > 0.0 or current_power > 0.0:
            self.async_write_ha_state()

    @property
    def native_value(self) -> float:
        """Return the cumulative heating energy in kWh."""
        return round(self._total_kwh, 4)
