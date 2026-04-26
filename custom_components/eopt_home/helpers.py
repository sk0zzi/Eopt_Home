"""Helper functions for the Eopt Home integration."""

from sensio_lib import SensioEnvironment


def get_environment(use_ha_pilot: bool) -> SensioEnvironment:
    """Return the SensioEnvironment based on the user's choice."""
    return SensioEnvironment.HA_PILOT if use_ha_pilot else SensioEnvironment.UNITY
