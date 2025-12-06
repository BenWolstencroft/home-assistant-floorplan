"""The Floorplan integration."""

import logging
from pathlib import Path
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DATA_FLOORPLAN, DEFAULT_DATA_DIR
from .floorplan_manager import FloorplanManager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Floorplan integration (YAML config)."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Floorplan from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create data directory if it doesn't exist
    data_dir = Path(hass.config.config_dir) / DEFAULT_DATA_DIR
    data_dir.mkdir(exist_ok=True)

    # Initialize floorplan manager
    manager = FloorplanManager(hass, data_dir)
    await manager.async_load_floorplan()

    hass.data[DOMAIN][entry.entry_id] = {
        "manager": manager,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
