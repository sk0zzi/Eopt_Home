"""Climate platform for Eopt Home integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from sensio_lib import Hub, Thermostat

from .const import DOMAIN
from .helpers import device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eopt Home thermostats from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    hub: Hub = data["hub"]
    entity_map: dict = data["entity_map"]

    entities = [
        SensioThermostatEntity(thermostat, entry, entity_map)
        for thermostat in hub.get_thermostats()
    ]
    async_add_entities(entities)
    _LOGGER.debug("Added %d Eopt Home climate entities", len(entities))


class SensioThermostatEntity(ClimateEntity):
    """Representation of a Sensio/Eopt Home heated floor thermostat."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_hvac_mode = HVACMode.HEAT
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(
        self,
        thermostat: Thermostat,
        entry: ConfigEntry,
        entity_map: dict,
    ) -> None:
        """Initialize the thermostat entity."""
        self._thermostat = thermostat
        self._entity_map = entity_map
        self._attr_unique_id = f"{DOMAIN}_{thermostat.unique_id}"
        if thermostat.zone_name and thermostat.name.startswith(
            f"{thermostat.zone_name} "
        ):
            self._attr_name = thermostat.name.removeprefix(f"{thermostat.zone_name} ")
        else:
            self._attr_name = thermostat.name
        self._attr_min_temp = thermostat.min_temp
        self._attr_max_temp = thermostat.max_temp
        self._attr_target_temperature_step = thermostat.temp_step
        self._attr_device_info = device_info(
            entry, thermostat.zone_id, thermostat.zone_name
        )

    async def async_added_to_hass(self) -> None:
        """Register this entity for push state updates."""
        self._entity_map[self._thermostat] = self

    async def async_will_remove_from_hass(self) -> None:
        """Unregister from push state updates."""
        self._entity_map.pop(self._thermostat, None)

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._thermostat.current_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self._thermostat.target_temperature

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac operation."""
        if self._thermostat.is_heating is None:
            return None
        return HVACAction.HEATING if self._thermostat.is_heating else HVACAction.IDLE

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode (only HEAT is supported)."""

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self._thermostat.set_temperature(float(temperature))
