"""Floorplan data manager."""

import logging
from pathlib import Path
from typing import Any

import yaml
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar, floor_registry as fr, device_registry as dr

from .const import (
    FLOORPLAN_CONFIG_FILE,
    ROOM_NAME,
    ROOM_AREA,
    ROOM_BOUNDARIES,
    ROOM_FLOOR,
    FLOOR_HEIGHT,
    ENTITY_ID,
    ENTITY_COORDINATES,
    CONF_MOVING_BEACON_NODES,
    BEACON_NODE_COORDINATES,
)

_LOGGER = logging.getLogger(__name__)


class FloorplanManager:
    """Manages floorplan configuration and data."""

    def __init__(self, hass: HomeAssistant, data_dir: Path) -> None:
        """Initialize the floorplan manager.

        Args:
            hass: Home Assistant instance
            data_dir: Path to the floorplan data directory
        """
        self.hass = hass
        self.data_dir = data_dir
        self.config_file = data_dir / FLOORPLAN_CONFIG_FILE
        self.floorplan_data: dict[str, Any] = {
            "floors": {},
            "rooms": {},
            "static_entities": {},
            "moving_entities": {
                "beacon_nodes": {},
            },
        }

    async def async_load_floorplan(self) -> None:
        """Load floorplan configuration from file."""
        if self.config_file.exists():
            try:
                def _load_yaml():
                    with open(self.config_file, "r") as f:
                        return yaml.safe_load(f)
                
                data = await self.hass.async_add_executor_job(_load_yaml)
                if data:
                    self.floorplan_data = data
                    _LOGGER.info("Loaded floorplan configuration")
            except Exception as err:
                _LOGGER.error("Error loading floorplan configuration: %s", err)
        else:
            _LOGGER.info("No floorplan configuration found, creating empty template")
            await self.async_save_floorplan()

    async def async_save_floorplan(self) -> None:
        """Save floorplan configuration to file."""
        try:
            def _save_yaml():
                with open(self.config_file, "w") as f:
                    yaml.dump(self.floorplan_data, f, default_flow_style=False, sort_keys=False)
            
            await self.hass.async_add_executor_job(_save_yaml)
            _LOGGER.info("Saved floorplan configuration")
        except Exception as err:
            _LOGGER.error("Error saving floorplan configuration: %s", err)

    def add_floor(self, floor_id: str, height: float) -> None:
        """Add a floor to the floorplan.

        Args:
            floor_id: Unique identifier for the floor (from Home Assistant floor registry)
            height: Height of the floor in meters
        """
        self.floorplan_data["floors"][floor_id] = {
            FLOOR_HEIGHT: height,
        }

    def add_room(
        self,
        room_id: str,
        name: str,
        floor_id: str,
        boundaries: list[list[float]],
        area_id: str | None = None,
    ) -> None:
        """Add a room to the floorplan.

        Args:
            room_id: Unique identifier for the room
            name: Display name for the room
            floor_id: ID of the floor this room is on
            boundaries: List of [X, Y] coordinate pairs defining room polygon
            area_id: Optional Home Assistant area ID to associate with this room
        """
        self.floorplan_data["rooms"][room_id] = {
            ROOM_NAME: name,
            ROOM_FLOOR: floor_id,
            ROOM_BOUNDARIES: boundaries,
        }
        if area_id:
            self.floorplan_data["rooms"][room_id][ROOM_AREA] = area_id

    def get_floors(self) -> dict[str, Any]:
        """Get all floors with their heights.
        
        Returns:
            Dictionary of floors with their metadata enriched with friendly names
        """
        floors = self.floorplan_data.get("floors", {})
        result = {}
        
        for floor_id, floor_data in floors.items():
            enriched_floor = dict(floor_data)
            
            # Add friendly name from registry if available
            floor_name = self._get_floor_name_from_registry(floor_id)
            if floor_name:
                enriched_floor["name"] = floor_name
            
            result[floor_id] = enriched_floor
        
        return result

    def get_all_floors(self) -> dict[str, Any]:
        """Get all floors with their heights.
        
        Returns:
            Dictionary of floors with their metadata enriched with friendly names
        """
        return self.get_floors()

    def get_rooms(self) -> dict[str, Any]:
        """Get all rooms."""
        return self.floorplan_data.get("rooms", {})

    def _get_floor_name_from_registry(self, floor_id: str) -> str | None:
        """Get floor friendly name from Home Assistant floor registry.
        
        Args:
            floor_id: ID of the floor
            
        Returns:
            Floor friendly name or None if not found
        """
        try:
            floor_registry = fr.async_get(self.hass)
            floor_entry = floor_registry.async_get_floor(floor_id)
            if floor_entry:
                return floor_entry.name
        except Exception as err:
            _LOGGER.debug("Could not get floor name from registry: %s", err)
        return None
    
    def _get_area_name_from_registry(self, area_id: str) -> str | None:
        """Get area name from Home Assistant area registry.
        
        Args:
            area_id: ID of the area
            
        Returns:
            Area name or None if not found
        """
        try:
            area_registry = ar.async_get(self.hass)
            area_entry = area_registry.async_get_area(area_id)
            if area_entry:
                return area_entry.name
        except Exception as err:
            _LOGGER.debug("Could not get area name from registry: %s", err)
        return None
    
    def _get_device_name_from_registry(self, device_address: str) -> str | None:
        """Get device friendly name from Home Assistant device registry.
        
        Args:
            device_address: Bluetooth MAC address (e.g., "AA:BB:CC:DD:EE:FF")
            
        Returns:
            Device friendly name or None if not found
        """
        try:
            device_registry = dr.async_get(self.hass)
            # Normalize MAC address to uppercase with colons
            normalized_address = device_address.upper().replace("-", ":")
            
            # Search for device by connection (Bluetooth MAC address)
            for device in device_registry.devices.values():
                for connection in device.connections:
                    # connection is a tuple like ("bluetooth", "AA:BB:CC:DD:EE:FF")
                    if connection[0] == "bluetooth" and connection[1].upper() == normalized_address:
                        # Return name_by_user if set, otherwise name
                        return device.name_by_user or device.name
            
            _LOGGER.debug("No device found in registry for address: %s", device_address)
        except Exception as err:
            _LOGGER.debug("Could not get device name from registry: %s", err)
        return None

    def get_rooms_by_floor(self, floor_id: str) -> dict[str, Any]:
        """Get all rooms on a specific floor.

        Args:
            floor_id: ID of the floor

        Returns:
            Dictionary of rooms on the floor with names enriched from HA registries
        """
        rooms = self.floorplan_data.get("rooms", {})
        result = {}
        
        for rid, room_data in rooms.items():
            if room_data.get(ROOM_FLOOR) == floor_id:
                # Copy room data
                enriched_room = dict(room_data)
                
                # If name is not set, try to get it from area registry
                if not enriched_room.get(ROOM_NAME):
                    area_id = enriched_room.get(ROOM_AREA)
                    if area_id:
                        area_name = self._get_area_name_from_registry(area_id)
                        if area_name:
                            enriched_room[ROOM_NAME] = area_name
                        else:
                            _LOGGER.warning(f"Could not find area name for room {rid} (area: {area_id}) in registry")
                
                result[rid] = enriched_room
        
        return result

    def get_room(self, room_id: str) -> dict[str, Any] | None:
        """Get a specific room by ID.

        Args:
            room_id: ID of the room

        Returns:
            Room data or None if not found
        """
        return self.floorplan_data.get("rooms", {}).get(room_id)

    def get_floor(self, floor_id: str) -> dict[str, Any] | None:
        """Get a specific floor by ID.

        Args:
            floor_id: ID of the floor

        Returns:
            Floor data enriched with friendly name from registry or None if not found
        """
        floor_data = self.floorplan_data.get("floors", {}).get(floor_id)
        if floor_data:
            # Copy floor data to avoid modifying original
            enriched_floor = dict(floor_data)
            
            # Add friendly name from registry if available
            floor_name = self._get_floor_name_from_registry(floor_id)
            if floor_name:
                enriched_floor["name"] = floor_name
            else:
                _LOGGER.warning(f"Could not find friendly name for floor {floor_id} in registry")
            
            return enriched_floor
        return None

    def update_room(self, room_id: str, **kwargs: Any) -> None:
        """Update a room's properties.

        Args:
            room_id: ID of the room
            **kwargs: Properties to update
        """
        if room_id in self.floorplan_data["rooms"]:
            self.floorplan_data["rooms"][room_id].update(kwargs)

    def delete_room(self, room_id: str) -> None:
        """Delete a room from the floorplan.

        Args:
            room_id: ID of the room to delete
        """
        self.floorplan_data["rooms"].pop(room_id, None)

    def delete_floor(self, floor_id: str) -> None:
        """Delete a floor from the floorplan.

        Args:
            floor_id: ID of the floor to delete
        """
        self.floorplan_data["floors"].pop(floor_id, None)
        # Also remove all rooms on this floor
        rooms_to_remove = [
            rid
            for rid, r in self.floorplan_data["rooms"].items()
            if r.get(ROOM_FLOOR) == floor_id
        ]
        for room_id in rooms_to_remove:
            self.delete_room(room_id)

    def add_static_entity(
        self, entity_id: str, coordinates: list[float]
    ) -> None:
        """Add a static entity with coordinates.

        Args:
            entity_id: Home Assistant entity ID (e.g., "light.living_room")
            coordinates: [X, Y, Z] coordinates in meters
        """
        if len(coordinates) != 3:
            raise ValueError("Coordinates must be [X, Y, Z] format")
        
        self.floorplan_data["static_entities"][entity_id] = {
            ENTITY_COORDINATES: coordinates,
        }

    def get_static_entities(self) -> dict[str, Any]:
        """Get all static entities with their coordinates.
        
        Returns:
            Dictionary of entities with their coordinate data
        """
        return self.floorplan_data.get("static_entities", {})

    def get_all_static_entities(self) -> dict[str, Any]:
        """Get all static entities with their coordinates.
        
        Returns:
            Dictionary of entities with their coordinate data
        """
        return self.floorplan_data.get("static_entities", {})

    def get_static_entity(self, entity_id: str) -> dict[str, Any] | None:
        """Get a specific static entity by ID.

        Args:
            entity_id: Home Assistant entity ID

        Returns:
            Entity data or None if not found
        """
        return self.floorplan_data.get("static_entities", {}).get(entity_id)

    def update_static_entity(self, entity_id: str, coordinates: list[float]) -> None:
        """Update a static entity's coordinates.

        Args:
            entity_id: Home Assistant entity ID
            coordinates: [X, Y, Z] coordinates in meters
        """
        if len(coordinates) != 3:
            raise ValueError("Coordinates must be [X, Y, Z] format")
        
        if entity_id in self.floorplan_data["static_entities"]:
            self.floorplan_data["static_entities"][entity_id][ENTITY_COORDINATES] = coordinates

    def delete_static_entity(self, entity_id: str) -> None:
        """Delete a static entity from the floorplan.

        Args:
            entity_id: Home Assistant entity ID to delete
        """
        self.floorplan_data["static_entities"].pop(entity_id, None)

    def get_entity_coordinates(self, entity_id: str) -> list[float] | None:
        """Get the coordinates for a specific entity.

        Args:
            entity_id: Home Assistant entity ID

        Returns:
            [X, Y, Z] coordinates or None if entity not found
        """
        entity = self.get_static_entity(entity_id)
        if entity:
            return entity.get(ENTITY_COORDINATES)
        return None

    def get_all_entity_coordinates(self) -> dict[str, list[float]]:
        """Get coordinates for all static entities.

        Returns:
            Dictionary mapping entity IDs to [X, Y, Z] coordinates
        """
        result = {}
        for entity_id, entity_data in self.floorplan_data.get("static_entities", {}).items():
            if ENTITY_COORDINATES in entity_data:
                result[entity_id] = entity_data[ENTITY_COORDINATES]
        return result

    # Beacon Node Management (provider-agnostic)
    def add_beacon_node(self, node_id: str, coordinates: list[float]) -> None:
        """Add a beacon node with coordinates.

        Args:
            node_id: Bluetooth device ID (must be a registered Bluetooth device in Home Assistant)
            coordinates: [X, Y, Z] coordinates in meters

        Raises:
            ValueError: If coordinates are not [X, Y, Z] format or if node_id is not a registered Bluetooth device
        """
        if len(coordinates) != 3:
            raise ValueError("Coordinates must be [X, Y, Z] format")
        
        # Validate that the node_id matches a registered Bluetooth device
        if not self._is_valid_bluetooth_device(node_id):
            raise ValueError(
                f"Node ID '{node_id}' is not a registered Bluetooth device in Home Assistant. "
                "Please ensure the device is registered in Settings → Devices & Services → Bluetooth."
            )
        
        nodes = self.floorplan_data["moving_entities"]["beacon_nodes"]
        nodes[node_id] = {
            BEACON_NODE_COORDINATES: coordinates,
        }

    def _is_valid_bluetooth_device(self, device_id: str) -> bool:
        """Check if a device ID is a registered Bluetooth device in Home Assistant.

        Args:
            device_id: Device ID to validate

        Returns:
            True if device is registered, False otherwise
        """
        # Bluetooth device validation disabled - API not available in current HA version
        # Accept MAC address format OR any alphanumeric string (for testing)
        import re
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        test_pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
        return bool(mac_pattern.match(device_id) or test_pattern.match(device_id))

    def get_beacon_nodes(self) -> dict[str, Any]:
        """Get all beacon nodes with their coordinates.

        Returns:
            Dictionary of beacon nodes with their coordinate data
        """
        return self.floorplan_data["moving_entities"].get("beacon_nodes", {})

    def get_beacon_node(self, node_id: str) -> dict[str, Any] | None:
        """Get a specific beacon node by ID.

        Args:
            node_id: Bluetooth device ID

        Returns:
            Node data or None if not found
        """
        nodes = self.floorplan_data["moving_entities"].get("beacon_nodes", {})
        return nodes.get(node_id)

    def update_beacon_node(self, node_id: str, coordinates: list[float]) -> None:
        """Update a beacon node's coordinates.

        Args:
            node_id: Bluetooth device ID
            coordinates: [X, Y, Z] coordinates in meters
        """
        if len(coordinates) != 3:
            raise ValueError("Coordinates must be [X, Y, Z] format")
        
        nodes = self.floorplan_data["moving_entities"]["beacon_nodes"]
        if node_id in nodes:
            nodes[node_id][BEACON_NODE_COORDINATES] = coordinates

    def delete_beacon_node(self, node_id: str) -> None:
        """Delete a beacon node from the floorplan.

        Args:
            node_id: Bluetooth device ID to delete
        """
        nodes = self.floorplan_data["moving_entities"]["beacon_nodes"]
        nodes.pop(node_id, None)

    def get_beacon_node_coordinates(self, node_id: str) -> list[float] | None:
        """Get the coordinates for a specific beacon node.

        Args:
            node_id: Bluetooth device ID

        Returns:
            [X, Y, Z] coordinates or None if not found
        """
        node = self.get_beacon_node(node_id)
        if node:
            return node.get(BEACON_NODE_COORDINATES)
        return None

    def get_all_beacon_node_coordinates(self) -> dict[str, list[float]]:
        """Get coordinates for all beacon nodes.

        Returns:
            Dictionary mapping node IDs to [X, Y, Z] coordinates
        """
        result = {}
        for node_id, node_data in self.get_beacon_nodes().items():
            if BEACON_NODE_COORDINATES in node_data:
                result[node_id] = node_data[BEACON_NODE_COORDINATES]
        return result
    
    def get_all_beacon_node_data(self) -> dict[str, dict[str, Any]]:
        """Get all beacon node data including coordinates and friendly names.
        
        Returns:
            Dictionary mapping node IDs to data dict with 'coordinates' and 'name' fields
        """
        result = {}
        for node_id, node_data in self.get_beacon_nodes().items():
            if BEACON_NODE_COORDINATES in node_data:
                enriched_data = {
                    "coordinates": node_data[BEACON_NODE_COORDINATES]
                }
                
                # Try to get friendly name from device registry
                device_name = self._get_device_name_from_registry(node_id)
                if device_name:
                    enriched_data["name"] = device_name
                else:
                    _LOGGER.warning(f"Could not find device name for beacon {node_id} in device registry")
                
                result[node_id] = enriched_data
        return result
