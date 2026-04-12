"""Light platform for Eopt Home integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from sensio_lib import Hub, Light

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eopt Home lights from a config entry."""
    hub: Hub = hass.data[DOMAIN][entry.entry_id]
    lights = hub.get_lights()

    entities = [SensioLightEntity(light, entry) for light in lights]
    async_add_entities(entities)
    _LOGGER.debug("Added %d Eopt Home light entities", len(entities))


class SensioLightEntity(LightEntity):
    """Representation of a Sensio/Eopt Home light."""

    _attr_has_entity_name = True
    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF

    def __init__(self, light: Light, entry: ConfigEntry) -> None:
        """Initialize the light entity."""
        self._light = light
        self._attr_unique_id = f"{DOMAIN}_{light.unique_id}"
        self._attr_name = light.name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Eopt Home ({entry.data.get('project_name', 'Hub')})",
            "manufacturer": "Eopt Home",
            "model": "Sensio Controller",
        }

    @property
    def is_on(self) -> bool | None:
        """Return True if the light is on."""
        return self._light.is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        await self._light.turn_on()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self._light.turn_off()
        self.async_write_ha_state()
