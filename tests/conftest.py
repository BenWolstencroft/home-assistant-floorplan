"""Pytest configuration and fixtures for floorplan tests."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Note: HomeAssistant is mocked for testing without requiring full HA installation
# Uncomment if you have homeassistant package installed for integration tests
# from homeassistant.core import HomeAssistant


@pytest.fixture
def hass():
    """Create a mock Home Assistant instance.
    
    Note: Bluetooth devices are mocked in root conftest.py via sys.modules.
    """
    hass = MagicMock()
    hass.states = MagicMock()
    hass.states.async_all = MagicMock(return_value=[])
    hass.states.get = MagicMock(return_value=None)
    hass.data = {}
    hass.services = MagicMock()
    hass.services.async_register = MagicMock()
    hass.services.async_call = MagicMock()
    
    # Mock async_add_executor_job to run synchronously for tests
    async def mock_executor_job(func, *args):
        return func(*args) if args else func()
    hass.async_add_executor_job = AsyncMock(side_effect=mock_executor_job)
    
    return hass


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for tests."""
    data_dir = tmp_path / "floorplan"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def sample_floorplan_data():
    """Sample floorplan configuration for testing."""
    return {
        "floors": {
            "ground_floor": {"height": 0},
            "1st_floor": {"height": 3.2},
        },
        "rooms": {
            "living_room": {
                "name": "Living Room",
                "floor": "ground_floor",
                "area": "living_room",
                "boundaries": [[0, 0], [10, 0], [10, 8], [0, 8]],
            },
            "kitchen": {
                "name": "Kitchen",
                "floor": "ground_floor",
                "area": "kitchen",
                "boundaries": [[10, 0], [15, 0], [15, 5], [10, 5]],
            },
        },
        "static_entities": {
            "light.living_room": [5, 4, 1.8],
            "camera.front_door": [0, 0, 2.2],
        },
        "moving_entities": {
            "beacon_nodes": {
                "D4:5F:4E:A1:23:45": [12, 2.5, 2.0],
                "A3:2B:1C:F9:87:56": [5, 4, 2.0],
                "F1:E2:D3:C4:B5:A6": [4, 8, 2.0],
            },
        },
    }


@pytest.fixture
def beacon_positions():
    """Standard beacon positions for trilateration tests."""
    return {
        "beacon_1": {"position": [0, 0, 2.0], "distance": 5.0},
        "beacon_2": {"position": [10, 0, 2.0], "distance": 3.0},
        "beacon_3": {"position": [5, 8, 2.0], "distance": 4.0},
    }

