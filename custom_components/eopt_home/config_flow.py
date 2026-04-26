"""Config flow for Eopt Home integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from sensio_lib import SensioApi, SensioAuthenticationError, SensioConnectionError, SensioEnvironment

from .const import (
    CONF_HUB_IP,
    CONF_PASSWORD,
    CONF_PROJECT_ID,
    CONF_PROJECT_NAME,
    CONF_USE_HA_PILOT,
    CONF_USERNAME,
    DOMAIN,
    STORAGE_KEY,
    STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HUB_IP): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_USE_HA_PILOT, default=False): bool,
    }
)


def _get_environment(use_ha_pilot: bool) -> SensioEnvironment:
    """Return the SensioEnvironment based on the user's choice."""
    return SensioEnvironment.HA_PILOT if use_ha_pilot else SensioEnvironment.UNITY


class EoptHomeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eopt Home."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step — collect hub IP, username, password."""
        errors: dict[str, str] = {}

        if user_input is not None:
            hub_ip = user_input[CONF_HUB_IP]
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            use_ha_pilot = user_input.get(CONF_USE_HA_PILOT, False)
            environment = _get_environment(use_ha_pilot)

            try:
                async with SensioApi(username, password, environment) as api:
                    projects = await api.login()

                    if not projects:
                        errors["base"] = "cannot_connect"
                    else:
                        # Auto-select the first project
                        project_name, project_id = next(iter(projects.items()))
                        functions_data = await api.get_devices(project_id)

                        unique_id = f"{hub_ip}_{project_id}"
                        await self.async_set_unique_id(unique_id)
                        self._abort_if_unique_id_configured()

                        # Cache device data for offline boots
                        store = Store(
                            self.hass,
                            STORAGE_VERSION,
                            f"{STORAGE_KEY}_{unique_id}",
                        )
                        await store.async_save(functions_data)

                        return self.async_create_entry(
                            title=f"Eopt Home ({project_name})",
                            data={
                                CONF_HUB_IP: hub_ip,
                                CONF_USERNAME: username,
                                CONF_PASSWORD: password,
                                CONF_PROJECT_ID: project_id,
                                CONF_PROJECT_NAME: project_name,
                                CONF_USE_HA_PILOT: use_ha_pilot,
                            },
                        )
            except SensioAuthenticationError:
                errors["base"] = "invalid_auth"
            except SensioConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

