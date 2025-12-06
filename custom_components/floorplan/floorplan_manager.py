"""Floorplan data manager."""

import logging
from pathlib import Path
from typing import Any

import yaml
from homeassistant.core import HomeAssistant
from homeassistant.helpers.floor_registry import FloorRegistry

from .const import FLOORPLAN_CONFIG_FILE, ROOM_NAME, ROOM_AREA, ROOM_BOUNDARIES, ROOM_FLOOR, FLOOR_HEIGHT

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
        }

    async def async_load_floorplan(self) -> None:
        """Load floorplan configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    data = yaml.safe_load(f)
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
            with open(self.config_file, "w") as f:
                yaml.dump(self.floorplan_data, f, default_flow_style=False, sort_keys=False)
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
            Dictionary of floors with their metadata
        """
        return self.floorplan_data.get("floors", {})

    def get_rooms(self) -> dict[str, Any]:
        """Get all rooms."""
        return self.floorplan_data.get("rooms", {})

    def get_rooms_by_floor(self, floor_id: str) -> dict[str, Any]:
        """Get all rooms on a specific floor.

        Args:
            floor_id: ID of the floor

        Returns:
            Dictionary of rooms on the floor
        """
        rooms = self.floorplan_data.get("rooms", {})
        return {rid: r for rid, r in rooms.items() if r.get(ROOM_FLOOR) == floor_id}

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
            Floor data or None if not found
        """
        return self.floorplan_data.get("floors", {}).get(floor_id)

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
