"""Helper functions for the Eopt Home integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from sensio_lib import SensioEnvironment

from .const import CONF_PROJECT_NAME, DOMAIN


def get_environment(use_ha_pilot: bool) -> SensioEnvironment:
    """Return the SensioEnvironment based on the user's choice."""
    return SensioEnvironment.HA_PILOT if use_ha_pilot else SensioEnvironment.UNITY


def device_info(
    entry: ConfigEntry,
    zone_id: str | None = None,
    zone_name: str | None = None,
) -> DeviceInfo:
    """Return DeviceInfo for the controller or a specific Sensio zone."""
    controller = (DOMAIN, entry.entry_id)
    if not zone_id or not zone_name:
        return DeviceInfo(
            identifiers={controller},
            name=f"Eopt Home ({entry.data.get(CONF_PROJECT_NAME, 'Hub')})",
            manufacturer="Eopt Home",
            model="Sensio Controller",
        )
    return DeviceInfo(
        identifiers={(DOMAIN, f"{entry.entry_id}_zone_{zone_id}")},
        name=zone_name,
        manufacturer="Eopt Home",
        model="Zone",
        via_device=controller,
    )
