"""The Floorplan integration."""

import logging
from pathlib import Path
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, callback

from .const import DOMAIN, DATA_FLOORPLAN, DEFAULT_DATA_DIR, CONF_PROVIDERS, CONF_BERMUDA, CONF_ENABLED
from .floorplan_manager import FloorplanManager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []

# Service names
SERVICE_GET_ENTITY_COORDINATES = "get_entity_coordinates"
SERVICE_GET_ALL_ENTITY_COORDINATES = "get_all_entity_coordinates"
SERVICE_ADD_BEACON_NODE = "add_beacon_node"
SERVICE_GET_BEACON_NODES = "get_beacon_nodes"
SERVICE_UPDATE_BEACON_NODE = "update_beacon_node"
SERVICE_DELETE_BEACON_NODE = "delete_beacon_node"
SERVICE_GET_MOVING_ENTITY_COORDINATES = "get_moving_entity_coordinates"
SERVICE_GET_ALL_MOVING_ENTITY_COORDINATES = "get_all_moving_entity_coordinates"

# Service schemas
GET_ENTITY_COORDINATES_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.string,
    }
)

BEACON_NODE_SCHEMA = vol.Schema(
    {
        vol.Required("node_id"): cv.string,
        vol.Required("coordinates"): [cv.positive_float],
    }
)


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

    # Register services
    async def handle_get_entity_coordinates(call: ServiceCall) -> dict[str, Any]:
        """Handle get_entity_coordinates service call."""
        entity_id = call.data.get("entity_id")
        coordinates = manager.get_entity_coordinates(entity_id)
        return {
            "entity_id": entity_id,
            "coordinates": coordinates,
        }

    async def handle_get_all_entity_coordinates(call: ServiceCall) -> dict[str, Any]:
        """Handle get_all_entity_coordinates service call."""
        all_coords = manager.get_all_entity_coordinates()
        beacon_nodes = manager.get_all_beacon_node_coordinates()
        
        return {
            "entity_coordinates": all_coords,
            "count": len(all_coords),
            "beacon_nodes": beacon_nodes,
            "beacon_nodes_count": len(beacon_nodes),
        }

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_ENTITY_COORDINATES,
        handle_get_entity_coordinates,
        schema=GET_ENTITY_COORDINATES_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_ALL_ENTITY_COORDINATES,
        handle_get_all_entity_coordinates,
    )

    async def handle_add_beacon_node(call: ServiceCall) -> None:
        """Handle add_beacon_node service call."""
        node_id = call.data.get("node_id")
        coordinates = call.data.get("coordinates")
        try:
            manager.add_beacon_node(node_id, coordinates)
            await manager.async_save_floorplan()
            _LOGGER.info("Added beacon node: %s at %s", node_id, coordinates)
        except ValueError as err:
            _LOGGER.error("Error adding beacon node: %s", err)
            raise

    async def handle_get_beacon_nodes(call: ServiceCall) -> dict[str, Any]:
        """Handle get_beacon_nodes service call."""
        nodes = manager.get_all_beacon_node_coordinates()
        return {
            "nodes": nodes,
            "count": len(nodes),
        }

    async def handle_update_beacon_node(call: ServiceCall) -> None:
        """Handle update_beacon_node service call."""
        node_id = call.data.get("node_id")
        coordinates = call.data.get("coordinates")
        try:
            manager.update_beacon_node(node_id, coordinates)
            await manager.async_save_floorplan()
            _LOGGER.info("Updated beacon node: %s to %s", node_id, coordinates)
        except ValueError as err:
            _LOGGER.error("Error updating beacon node: %s", err)
            raise

    async def handle_delete_beacon_node(call: ServiceCall) -> None:
        """Handle delete_beacon_node service call."""
        node_id = call.data.get("node_id")
        manager.delete_beacon_node(node_id)
        await manager.async_save_floorplan()
        _LOGGER.info("Deleted beacon node: %s", node_id)

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_BEACON_NODE,
        handle_add_beacon_node,
        schema=BEACON_NODE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_BEACON_NODES,
        handle_get_beacon_nodes,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_BEACON_NODE,
        handle_update_beacon_node,
        schema=BEACON_NODE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_BEACON_NODE,
        handle_delete_beacon_node,
        schema=vol.Schema({vol.Required("node_id"): cv.string}),
    )

    # Initialize location provider (Bermuda) if enabled
    providers_config = entry.data.get(CONF_PROVIDERS, {})
    bermuda_config = providers_config.get(CONF_BERMUDA, {})
    enable_bermuda = bermuda_config.get(CONF_ENABLED, True)
    
    if enable_bermuda:
        try:
            from .providers.bermuda import BermudaLocationProvider
        except ImportError as err:
            _LOGGER.error("Failed to import Bermuda provider: %s", err)
            _LOGGER.warning("Bermuda location provider will be disabled")
            enable_bermuda = False
        
    if enable_bermuda:
        bermuda_provider = BermudaLocationProvider(hass, manager)

        async def handle_get_moving_entity_coordinates(call: ServiceCall) -> dict[str, Any]:
            """Handle get_moving_entity_coordinates service call."""
            entity_id = call.data.get("entity_id")
            result = await bermuda_provider.get_moving_entity_coordinates(entity_id)
            if result:
                return result
            return {
                "entity_id": entity_id,
                "coordinates": None,
            }

        async def handle_get_all_moving_entity_coordinates(
            call: ServiceCall,
        ) -> dict[str, Any]:
            """Handle get_all_moving_entity_coordinates service call."""
            coordinates = await bermuda_provider.get_all_moving_entity_coordinates()
            return {
                "moving_entities": coordinates,
                "count": len(coordinates),
            }

        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_MOVING_ENTITY_COORDINATES,
            handle_get_moving_entity_coordinates,
            schema=GET_ENTITY_COORDINATES_SCHEMA,
        )

        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_ALL_MOVING_ENTITY_COORDINATES,
            handle_get_all_moving_entity_coordinates,
        )
        
        _LOGGER.info("Bermuda location provider enabled")
    else:
        _LOGGER.info("Bermuda location provider disabled")


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
