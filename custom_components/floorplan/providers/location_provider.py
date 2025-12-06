"""Base location provider interface for floorplan."""

from abc import ABC, abstractmethod
from typing import Any


class LocationProvider(ABC):
    """Base class for location providers."""

    def __init__(self, hass, floorplan_manager):
        """Initialize the location provider."""
        self.hass = hass
        self.manager = floorplan_manager

    @abstractmethod
    async def get_moving_entity_coordinates(
        self, entity_id: str
    ) -> dict[str, Any] | None:
        """Get coordinates for a moving entity.
        
        Returns:
            Dictionary with 'entity_id' and 'coordinates' [X, Y, Z], or None if not found.
        """
        pass

    @abstractmethod
    async def get_all_moving_entity_coordinates(self) -> dict[str, Any]:
        """Get coordinates for all tracked moving entities.
        
        Returns:
            Dictionary with entity_id -> [X, Y, Z] coordinates.
        """
        pass
