"""The Eopt Home integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.storage import Store
from sensio_lib import (
    Hub,
    SensioApi,
    SensioAuthenticationError,
    SensioConnectionError,
    SensioEnvironment,
)

from .const import (
    CONF_HUB_IP,
    CONF_PASSWORD,
    CONF_PROJECT_ID,
    CONF_USE_HA_PILOT,
    CONF_USERNAME,
    DOMAIN,
    STORAGE_KEY,
    STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["light", "scene", "button"]


def _get_environment(entry: ConfigEntry) -> SensioEnvironment:
    """Return the SensioEnvironment for this config entry."""
    if entry.data.get(CONF_USE_HA_PILOT, False):
        return SensioEnvironment.HA_PILOT
    return SensioEnvironment.UNITY


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eopt Home from a config entry."""
    hub_ip = entry.data[CONF_HUB_IP]

    store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry.unique_id}")
    functions_data = await store.async_load()

    if functions_data is None:
        # No cached data — fetch from cloud (first boot or cache cleared)
        _LOGGER.info("No cached device data, fetching from Sensio cloud")
        functions_data = await _fetch_from_cloud(entry)
        await store.async_save(functions_data)

    hub = Hub(hub_ip)

    try:
        await hub.connect(functions_data)
    except SensioConnectionError as err:
        await hub.close()
        _LOGGER.error("Cannot connect to Eopt Home hub at %s: %s", hub_ip, err)
        raise ConfigEntryNotReady(
            f"Cannot connect to hub at {hub_ip}"
        ) from err
    except Exception as err:
        await hub.close()
        _LOGGER.exception("Unexpected error setting up Eopt Home")
        raise ConfigEntryNotReady(
            f"Unexpected error setting up hub at {hub_ip}"
        ) from err

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = hub

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Eopt Home config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hub: Hub = hass.data[DOMAIN].pop(entry.entry_id)
        await hub.close()

    return unload_ok


async def _fetch_from_cloud(entry: ConfigEntry) -> dict:
    """Fetch device data from the Sensio cloud API."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    project_id = entry.data[CONF_PROJECT_ID]
    environment = _get_environment(entry)

    try:
        async with SensioApi(username, password, environment) as api:
            await api.login()
            data = await api.get_devices(project_id)
            _LOGGER.debug("Retrieved %s devices from Sensio cloud", len(data))
            return data
    except SensioAuthenticationError as err:
        raise ConfigEntryNotReady(
            f"Cloud authentication failed: {err}"
        ) from err
    except SensioConnectionError as err:
        raise ConfigEntryNotReady(
            f"Cannot reach Sensio cloud: {err}"
        ) from err


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old config entries to the current version.

    v1 -> v2: Add use_ha_pilot flag (defaults to False for backwards
    compatibility — existing installs use the Unity environment).
    """
    if config_entry.version == 1:
        _LOGGER.debug("Migrating config entry %s from version 1 to 2", config_entry.entry_id)
        new_data = {**config_entry.data, CONF_USE_HA_PILOT: False}
        hass.config_entries.async_update_entry(config_entry, data=new_data, version=2)
        _LOGGER.info("Migration of config entry %s to version 2 successful", config_entry.entry_id)

    return True

