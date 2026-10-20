"""Light platform for Eopt Home integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from sensio_lib import Dimmer, Hub, Light

from .const import DOMAIN
from .helpers import device_info

_LOGGER = logging.getLogger(__name__)


def _to_ha_brightness(level: int) -> int:
    """Convert Sensio brightness (0-100) to Home Assistant brightness (0-255)."""
    return round(min(level, 100) * 255 / 100)


def _to_sensio_level(brightness: int) -> int:
    """Convert Home Assistant brightness (0-255) to Sensio brightness (1-100)."""
    return max(1, min(100, round(brightness * 100 / 255)))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eopt Home lights and dimmers from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    hub: Hub = data["hub"]
    entity_map: dict = data["entity_map"]

    entities: list[LightEntity] = [
        SensioLightEntity(light, entry, entity_map) for light in hub.get_lights()
    ]
    entities.extend(
        SensioDimmerEntity(dimmer, entry, entity_map) for dimmer in hub.get_dimmers()
    )
    async_add_entities(entities)
    _LOGGER.debug("Added %d Eopt Home light/dimmer entities", len(entities))


class SensioLightEntity(LightEntity):
    """Representation of a Sensio/Eopt Home relay light."""

    _attr_has_entity_name = True
    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF

    def __init__(self, light: Light, entry: ConfigEntry, entity_map: dict) -> None:
        """Initialize the light entity."""
        self._light = light
        self._entity_map = entity_map
        self._attr_unique_id = f"{DOMAIN}_{light.unique_id}"
        self._attr_name = light.name
        self._attr_device_info = device_info(entry, light.zone_id, light.zone_name)

    async def async_added_to_hass(self) -> None:
        """Register this entity for push state updates."""
        self._entity_map[self._light] = self

    async def async_will_remove_from_hass(self) -> None:
        """Unregister from push state updates."""
        self._entity_map.pop(self._light, None)

    @property
    def is_on(self) -> bool | None:
        """Return True if the light is on."""
        return self._light.is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        await self._light.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self._light.turn_off()


class SensioDimmerEntity(LightEntity):
    """Representation of a Sensio/Eopt Home dimmer light."""

    _attr_has_entity_name = True
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(self, dimmer: Dimmer, entry: ConfigEntry, entity_map: dict) -> None:
        """Initialize the dimmer entity."""
        self._dimmer = dimmer
        self._entity_map = entity_map
        self._attr_unique_id = f"{DOMAIN}_{dimmer.unique_id}"
        self._attr_name = dimmer.name
        self._attr_device_info = device_info(entry, dimmer.zone_id, dimmer.zone_name)

    async def async_added_to_hass(self) -> None:
        """Register this entity for push state updates."""
        self._entity_map[self._dimmer] = self

    async def async_will_remove_from_hass(self) -> None:
        """Unregister from push state updates."""
        self._entity_map.pop(self._dimmer, None)

    @property
    def is_on(self) -> bool | None:
        """Return True if the dimmer is on."""
        return self._dimmer.is_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the dimmer between 0..255."""
        if self._dimmer.brightness is None:
            return None
        return _to_ha_brightness(self._dimmer.brightness)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the dimmer on, optionally setting brightness."""
        if (brightness := kwargs.get(ATTR_BRIGHTNESS)) is not None:
            await self._dimmer.set_brightness(_to_sensio_level(brightness))
        else:
            await self._dimmer.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the dimmer off."""
        await self._dimmer.turn_off()
