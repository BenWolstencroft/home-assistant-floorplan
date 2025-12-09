"""The Floorplan integration."""

import logging
from pathlib import Path
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, callback, SupportsResponse

from .const import (
    DOMAIN,
    DATA_FLOORPLAN,
    DEFAULT_DATA_DIR,
    CONF_PROVIDERS,
    CONF_BERMUDA,
    CONF_ENABLED,
    ROOM_NAME,
    ROOM_FLOOR,
    ROOM_AREA,
    ROOM_BOUNDARIES,
    FLOOR_HEIGHT,
)
from .floorplan_manager import FloorplanManager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []

# Config schema - integration can be set up via config entry only
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

# Service names
SERVICE_GET_ENTITY_COORDINATES = "get_entity_coordinates"
SERVICE_GET_ALL_ENTITY_COORDINATES = "get_all_entity_coordinates"
SERVICE_GET_ROOMS_BY_FLOOR = "get_rooms_by_floor"
SERVICE_ADD_BEACON_NODE = "add_beacon_node"
SERVICE_GET_BEACON_NODES = "get_beacon_nodes"
SERVICE_UPDATE_BEACON_NODE = "update_beacon_node"
SERVICE_DELETE_BEACON_NODE = "delete_beacon_node"
SERVICE_GET_MOVING_ENTITY_COORDINATES = "get_moving_entity_coordinates"
SERVICE_GET_ALL_MOVING_ENTITY_COORDINATES = "get_all_moving_entity_coordinates"
SERVICE_RELOAD = "reload"

# Service schemas
GET_ENTITY_COORDINATES_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.string,
    }
)

GET_ROOMS_BY_FLOOR_SCHEMA = vol.Schema(
    {
        vol.Required("floor_id"): cv.string,
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

    # Store manager in hass.data
    hass.data[DOMAIN][entry.entry_id] = {
        "manager": manager,
    }

    # Set up file watcher for automatic reload
    async def watch_floorplan_file():
        """Watch floorplan.yaml for changes and reload automatically."""
        import asyncio
        
        config_file = manager.config_file
        last_mtime = None
        
        while True:
            try:
                await asyncio.sleep(2)  # Check every 2 seconds
                if config_file.exists():
                    current_mtime = config_file.stat().st_mtime
                    if last_mtime is not None and current_mtime != last_mtime:
                        _LOGGER.info("Detected change in floorplan.yaml, reloading...")
                        await manager.async_load_floorplan()
                        _LOGGER.info("Floorplan configuration reloaded successfully")
                    last_mtime = current_mtime
            except Exception as err:
                _LOGGER.error("Error watching floorplan file: %s", err)
    
    # Start file watcher task
    hass.data[DOMAIN][entry.entry_id]["watcher_task"] = hass.async_create_task(
        watch_floorplan_file()
    )

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
        beacon_nodes = manager.get_all_beacon_node_data()
        
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
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_ALL_ENTITY_COORDINATES,
        handle_get_all_entity_coordinates,
        supports_response=SupportsResponse.ONLY,
    )

    async def handle_get_rooms_by_floor(call: ServiceCall) -> dict[str, Any]:
        """Handle get_rooms_by_floor service call."""
        floor_id = call.data.get("floor_id")
        rooms_dict = manager.get_rooms_by_floor(floor_id)
        floor_data = manager.get_floor(floor_id)
        
        # Get all floors to calculate floor range (for beacon filtering)
        all_floors = manager.get_all_floors()
        current_floor_height = floor_data.get(FLOOR_HEIGHT, 0.0) if floor_data else 0.0
        
        # Find the previous floor's ceiling height (floor below current floor)
        # Floors are defined by their ceiling height, so we need to find the highest
        # floor that has a height less than the current floor
        previous_floor_height = 0.0
        for fid, fdata in all_floors.items():
            if fid != floor_id:
                fheight = fdata.get(FLOOR_HEIGHT, 0.0)
                if fheight < current_floor_height and fheight > previous_floor_height:
                    previous_floor_height = fheight
        
        # Convert to list format for the card
        rooms_list = [
            {
                "id": room_id,
                "name": room_data.get(ROOM_NAME, room_id),
                "floor": room_data.get(ROOM_FLOOR),
                "area": room_data.get(ROOM_AREA),
                "boundaries": room_data.get(ROOM_BOUNDARIES, []),
            }
            for room_id, room_data in rooms_dict.items()
        ]
        
        return {
            "rooms": rooms_list,
            "count": len(rooms_list),
            "floor_height": current_floor_height,
            "floor_min_height": previous_floor_height,
        }

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_ROOMS_BY_FLOOR,
        handle_get_rooms_by_floor,
        schema=GET_ROOMS_BY_FLOOR_SCHEMA,
        supports_response=SupportsResponse.ONLY,
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
        supports_response=SupportsResponse.ONLY,
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
            # Import at runtime to avoid circular dependencies
            from .providers.bermuda import BermudaLocationProvider
            bermuda_provider = BermudaLocationProvider(hass, manager)
        except Exception as err:
            _LOGGER.error("Failed to import Bermuda provider: %s", err, exc_info=True)
            _LOGGER.warning("Bermuda location provider will be disabled")
            enable_bermuda = False
        
    if enable_bermuda:

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
            _LOGGER.debug(f"Bermuda provider returned {len(coordinates)} moving entities: {list(coordinates.keys())}")
            return {
                "moving_entities": coordinates,
                "count": len(coordinates),
            }

        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_MOVING_ENTITY_COORDINATES,
            handle_get_moving_entity_coordinates,
            schema=GET_ENTITY_COORDINATES_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_ALL_MOVING_ENTITY_COORDINATES,
            handle_get_all_moving_entity_coordinates,
            supports_response=SupportsResponse.ONLY,
        )
        
        _LOGGER.info("Bermuda location provider enabled")
    else:
        _LOGGER.info("Bermuda location provider disabled")

    # Register reload service
    async def handle_reload(call: ServiceCall) -> None:
        """Handle reload service call to manually reload floorplan.yaml."""
        _LOGGER.info("Manual reload requested")
        await manager.async_load_floorplan()
        _LOGGER.info("Floorplan configuration reloaded successfully")

    hass.services.async_register(
        DOMAIN,
        SERVICE_RELOAD,
        handle_reload,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Cancel file watcher task
        entry_data = hass.data[DOMAIN].get(entry.entry_id, {})
        if "watcher_task" in entry_data:
            entry_data["watcher_task"].cancel()
        
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
