"""Button platform for Eopt Home integration."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.storage import Store
from sensio_lib import SensioApi, SensioAuthenticationError, SensioConnectionError

from .const import (
    CONF_PASSWORD,
    CONF_PROJECT_ID,
    CONF_USE_HA_PILOT,
    CONF_USERNAME,
    DOMAIN,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .helpers import get_environment

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eopt Home buttons from a config entry."""
    async_add_entities([SensioSyncButton(entry)])


class SensioSyncButton(ButtonEntity):
    """Button that re-syncs devices from the Sensio cloud."""

    _attr_has_entity_name = True
    _attr_name = "Sync Devices"
    _attr_icon = "mdi:cloud-sync"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the sync button."""
        self._entry = entry
        self._attr_unique_id = f"{DOMAIN}_{entry.unique_id}_sync"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Eopt Home ({entry.data.get('project_name', 'Hub')})",
            "manufacturer": "Eopt Home",
            "model": "Sensio Controller",
        }

    async def async_press(self) -> None:
        """Fetch fresh device data from cloud and reload the integration."""
        username = self._entry.data[CONF_USERNAME]
        password = self._entry.data[CONF_PASSWORD]
        project_id = self._entry.data[CONF_PROJECT_ID]
        use_ha_pilot = self._entry.data.get(CONF_USE_HA_PILOT, False)
        environment = get_environment(use_ha_pilot)

        try:
            async with SensioApi(username, password, environment) as api:
                await api.login()
                functions_data = await api.get_devices(project_id)
                _LOGGER.debug("Retrieved %s devices from Sensio cloud", len(functions_data))
        except (SensioAuthenticationError, SensioConnectionError) as err:
            raise HomeAssistantError(
                f"Failed to sync devices from cloud: {err}"
            ) from err

        store = Store(
            self.hass, STORAGE_VERSION, f"{STORAGE_KEY}_{self._entry.unique_id}"
        )
        await store.async_save(functions_data)

        _LOGGER.info("Device data synced from cloud, reloading integration")
        await self.hass.config_entries.async_reload(self._entry.entry_id)
