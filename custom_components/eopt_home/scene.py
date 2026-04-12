"""Scene platform for Eopt Home integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.scene import Scene as SceneEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from sensio_lib import Hub, Scene

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eopt Home scenes from a config entry."""
    hub: Hub = hass.data[DOMAIN][entry.entry_id]
    scenes = hub.get_scenes()

    entities = [SensioSceneEntity(scene, entry) for scene in scenes]
    async_add_entities(entities)
    _LOGGER.debug("Added %d Eopt Home scene entities", len(entities))


class SensioSceneEntity(SceneEntity):
    """Representation of a Sensio/Eopt Home scene."""

    _attr_has_entity_name = True

    def __init__(self, scene: Scene, entry: ConfigEntry) -> None:
        """Initialize the scene entity."""
        self._scene = scene
        self._attr_unique_id = f"{DOMAIN}_{scene.unique_id}"
        self._attr_name = scene.name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Eopt Home ({entry.data.get('project_name', 'Hub')})",
            "manufacturer": "Eopt Home",
            "model": "Sensio Controller",
        }

    async def async_activate(self, **kwargs: Any) -> None:
        """Activate the scene."""
        await self._scene.activate()
