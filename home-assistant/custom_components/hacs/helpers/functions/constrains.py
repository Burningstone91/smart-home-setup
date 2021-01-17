"""HACS Startup constrains."""
# pylint: disable=bad-continuation
import os

from custom_components.hacs.const import (
    CUSTOM_UPDATER_LOCATIONS,
    CUSTOM_UPDATER_WARNING,
    MINIMUM_HA_VERSION,
)
from custom_components.hacs.helpers.functions.misc import version_left_higher_then_right
from custom_components.hacs.share import get_hacs


def check_constrains():
    """Check HACS constrains."""
    if not constrain_custom_updater():
        return False
    if not constrain_version():
        return False
    return True


def constrain_custom_updater():
    """Check if custom_updater exist."""
    hacs = get_hacs()
    for location in CUSTOM_UPDATER_LOCATIONS:
        if os.path.exists(location.format(hacs.core.config_path)):
            msg = CUSTOM_UPDATER_WARNING.format(location.format(hacs.core.config_path))
            hacs.log.critical(msg)
            return False
    return True


def constrain_version():
    """Check if the version is valid."""
    hacs = get_hacs()
    if not version_left_higher_then_right(hacs.system.ha_version, MINIMUM_HA_VERSION):
        hacs.log.critical(
            "You need HA version %s or newer to use this integration.",
            MINIMUM_HA_VERSION,
        )
        return False
    return True
