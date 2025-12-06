"""Test utilities and helpers for Floorplan integration tests."""

import math
from typing import Any
from unittest.mock import MagicMock


def create_mock_home_assistant():
    """Create a mock Home Assistant instance for testing."""
    hass = MagicMock()
    hass.states = MagicMock()
    hass.states.async_all = MagicMock(return_value=[])
    hass.states.get = MagicMock(return_value=None)
    hass.data = {}
    hass.services = MagicMock()
    hass.services.async_register = MagicMock()
    hass.services.async_call = MagicMock()
    return hass


def create_mock_state(entity_id: str, state: str, attributes: dict[str, Any] = None):
    """Create a mock Home Assistant state object."""
    mock_state = MagicMock()
    mock_state.entity_id = entity_id
    mock_state.state = state
    mock_state.attributes = attributes or {}
    return mock_state


def create_mock_distance_sensor(device_name: str, beacon_name: str, distance: float):
    """Create a mock Bermuda distance sensor state."""
    entity_id = f"sensor.distance_to_{device_name}_{beacon_name}"
    return create_mock_state(entity_id, str(distance))


def calculate_euclidean_distance(point1: list[float], point2: list[float]) -> float:
    """Calculate Euclidean distance between two points."""
    if len(point1) != len(point2):
        raise ValueError("Points must have the same dimension")

    sum_squared_diff = sum((p2 - p1) ** 2 for p1, p2 in zip(point1, point2))
    return math.sqrt(sum_squared_diff)


def calculate_residual_error(
    calculated_distance: float, measured_distance: float
) -> float:
    """Calculate residual error between calculated and measured distances."""
    return (calculated_distance - measured_distance) ** 2


def calculate_total_error(
    beacons: list[list[float]], point: list[float], distances: list[float]
) -> float:
    """Calculate total least-squares error for a point and set of beacons."""
    total_error = 0
    for beacon, measured_dist in zip(beacons, distances):
        calculated_dist = calculate_euclidean_distance(beacon, point)
        total_error += calculate_residual_error(calculated_dist, measured_dist)
    return total_error


def generate_test_beacon_network(
    width: float = 10, height: float = 10, depth: float = 2.0, num_beacons: int = 3
) -> list[list[float]]:
    """Generate a test beacon network positioned in 3D space.

    Args:
        width: Width of the network (X dimension)
        height: Depth of the network (Y dimension)
        depth: Height of mounting (Z dimension)
        num_beacons: Number of beacons to generate

    Returns:
        List of beacon positions [X, Y, Z]
    """
    if num_beacons < 3:
        raise ValueError("At least 3 beacons required for trilateration")

    beacons = []

    if num_beacons == 3:
        # Triangle formation
        beacons = [
            [0, 0, depth],
            [width, 0, depth],
            [width / 2, height, depth],
        ]
    elif num_beacons == 4:
        # Square formation
        beacons = [
            [0, 0, depth],
            [width, 0, depth],
            [width, height, depth],
            [0, height, depth],
        ]
    else:
        # Circular formation
        import math

        for i in range(num_beacons):
            angle = (2 * math.pi * i) / num_beacons
            x = (width / 2) + (width / 2) * math.cos(angle)
            y = (height / 2) + (height / 2) * math.sin(angle)
            beacons.append([x, y, depth])

    return beacons


def calculate_distances_from_point(
    point: list[float], beacons: list[list[float]]
) -> list[float]:
    """Calculate distances from a point to a list of beacons.

    Args:
        point: Point coordinates [X, Y, Z]
        beacons: List of beacon positions

    Returns:
        List of distances to each beacon
    """
    return [calculate_euclidean_distance(point, beacon) for beacon in beacons]


def validate_floorplan_structure(data: dict[str, Any]) -> bool:
    """Validate that floorplan data has correct structure.

    Args:
        data: Floorplan data dictionary

    Returns:
        True if structure is valid, False otherwise
    """
    required_keys = ["floors", "rooms", "static_entities", "moving_entities"]

    for key in required_keys:
        if key not in data:
            return False

    if not isinstance(data["floors"], dict):
        return False
    if not isinstance(data["rooms"], dict):
        return False
    if not isinstance(data["static_entities"], dict):
        return False
    if not isinstance(data["moving_entities"], dict):
        return False

    # Check moving_entities has beacon_nodes
    if "beacon_nodes" not in data["moving_entities"]:
        return False

    return True


def validate_room_structure(room: dict[str, Any]) -> bool:
    """Validate that room data has correct structure.

    Args:
        room: Room data dictionary

    Returns:
        True if structure is valid, False otherwise
    """
    required_keys = ["name", "floor", "boundaries"]

    for key in required_keys:
        if key not in room:
            return False

    # Validate name is string
    if not isinstance(room["name"], str):
        return False

    # Validate floor is string
    if not isinstance(room["floor"], str):
        return False

    # Validate boundaries is list of coordinate pairs
    if not isinstance(room["boundaries"], list):
        return False

    for boundary in room["boundaries"]:
        if not isinstance(boundary, list) or len(boundary) != 2:
            return False

    return True


def validate_entity_coordinates(coordinates: list[float]) -> bool:
    """Validate that entity coordinates are valid.

    Args:
        coordinates: [X, Y, Z] coordinates

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(coordinates, list):
        return False

    if len(coordinates) != 3:
        return False

    # All should be numbers (int or float)
    for coord in coordinates:
        if not isinstance(coord, (int, float)):
            return False

        # Should be finite (not inf or nan)
        if math.isnan(coord) or math.isinf(coord):
            return False

    return True


class MockConfigEntry:
    """Mock Home Assistant ConfigEntry for testing."""

    def __init__(self, data: dict[str, Any] = None, version: int = 1):
        """Initialize mock config entry."""
        self.data = data or {}
        self.version = version
        self.title = "Floorplan"
        self.unique_id = "floorplan"

    def __repr__(self):
        return f"MockConfigEntry(data={self.data}, version={self.version})"
