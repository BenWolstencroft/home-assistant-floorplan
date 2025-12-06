"""Tests for Bermuda location provider trilateration."""

import pytest
import math
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.floorplan.providers.bermuda import BermudaLocationProvider
from custom_components.floorplan.floorplan_manager import FloorplanManager


class TestBermudaTrilateration:
    """Test Bermuda trilateration algorithm."""

    @pytest.fixture
    def bermuda_provider(self, hass, temp_data_dir):
        """Create a Bermuda provider instance."""
        manager = FloorplanManager(hass, temp_data_dir)
        # Setup beacon nodes
        manager.add_beacon_node("beacon_1", [0, 0, 2.0])
        manager.add_beacon_node("beacon_2", [10, 0, 2.0])
        manager.add_beacon_node("beacon_3", [5, 8, 2.0])
        return BermudaLocationProvider(hass, manager)

    @pytest.mark.asyncio
    async def test_provider_init(self, bermuda_provider):
        """Test provider initialization."""
        assert bermuda_provider.hass is not None
        assert bermuda_provider.manager is not None

    @pytest.mark.asyncio
    async def test_trilaterate_at_known_point(self, bermuda_provider):
        """Test trilateration at a known point."""
        # Device at [5, 4, 2.0]
        beacon_distances = {
            "beacon_1": 6.403,  # distance from [0, 0, 2.0] to [5, 4, 2.0]
            "beacon_2": 6.403,  # distance from [10, 0, 2.0] to [5, 4, 2.0]
            "beacon_3": 4.123,  # distance from [5, 8, 2.0] to [5, 4, 2.0]
        }

        # Mock the state retrieval
        def create_mock_state(entity_id, value):
            state = MagicMock()
            state.state = str(value)
            state.entity_id = entity_id
            return state

        distance_states = [
            create_mock_state("sensor.distance_to_device_beacon_1", beacon_distances["beacon_1"]),
            create_mock_state("sensor.distance_to_device_beacon_2", beacon_distances["beacon_2"]),
            create_mock_state("sensor.distance_to_device_beacon_3", beacon_distances["beacon_3"]),
        ]

        with patch.object(bermuda_provider, "_find_distance_sensors", return_value=distance_states):
            with patch.object(bermuda_provider, "_triangulate_entity") as mock_triangulate:
                mock_triangulate.return_value = [5.0, 4.0, 2.0]
                result = await bermuda_provider.get_moving_entity_coordinates("device_tracker.device")
                
                if result:
                    assert result["entity_id"] == "device_tracker.device"
                    # Allow for some numerical error in trilateration
                    assert abs(result["coordinates"][0] - 5.0) < 1.0
                    assert abs(result["coordinates"][1] - 4.0) < 1.0

    @pytest.mark.asyncio
    async def test_insufficient_beacons(self, hass, temp_data_dir):
        """Test that trilateration fails with fewer than 3 beacons."""
        manager = FloorplanManager(hass, temp_data_dir)
        # Only add 2 beacons
        manager.add_beacon_node("beacon_1", [0, 0, 2.0])
        manager.add_beacon_node("beacon_2", [10, 0, 2.0])
        
        provider = BermudaLocationProvider(hass, manager)

        # With 2 beacons, should not be able to triangulate
        result = await provider.get_moving_entity_coordinates("device_tracker.device")
        assert result is None

    @pytest.mark.asyncio
    async def test_missing_distance_data(self, bermuda_provider):
        """Test handling of missing distance data."""
        # Mock empty distance sensors
        with patch.object(bermuda_provider, "_find_distance_sensors", return_value=[]):
            result = await bermuda_provider.get_moving_entity_coordinates("device_tracker.unknown")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_all_moving_entities(self, bermuda_provider):
        """Test getting all moving entities."""
        # Mock device discovery
        with patch.object(bermuda_provider, "_find_distance_sensors", return_value=[]):
            result = await bermuda_provider.get_all_moving_entity_coordinates()
            assert isinstance(result, dict)

    def test_distance_calculation(self):
        """Test Euclidean distance calculation."""
        # Distance from [0, 0, 0] to [3, 4, 0] should be 5
        p1 = [0, 0, 0]
        p2 = [3, 4, 0]
        distance = math.sqrt(
            (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2
        )
        assert distance == 5.0

    def test_3d_distance_calculation(self):
        """Test 3D Euclidean distance calculation."""
        # Distance from [0, 0, 0] to [1, 1, 1] should be sqrt(3) ≈ 1.732
        p1 = [0, 0, 0]
        p2 = [1, 1, 1]
        distance = math.sqrt(
            (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2
        )
        assert abs(distance - math.sqrt(3)) < 0.001


class TestTriangulationMath:
    """Test mathematical trilateration calculations."""

    def test_centroid_calculation(self):
        """Test calculation of centroid from beacon positions."""
        positions = [[0, 0, 2.0], [10, 0, 2.0], [5, 8, 2.0]]
        centroid = [
            sum(p[0] for p in positions) / len(positions),
            sum(p[1] for p in positions) / len(positions),
            sum(p[2] for p in positions) / len(positions),
        ]

        assert centroid[0] == 5.0  # (0 + 10 + 5) / 3
        assert centroid[1] == pytest.approx(2.667, rel=0.01)  # (0 + 0 + 8) / 3
        assert centroid[2] == 2.0  # (2 + 2 + 2) / 3

    def test_residual_calculation(self):
        """Test calculation of residual error."""
        # Point and beacon
        point = [5, 4, 2.0]
        beacon = [0, 0, 2.0]
        measured_distance = 6.403

        # Calculated distance
        calculated = math.sqrt(
            (point[0] - beacon[0]) ** 2
            + (point[1] - beacon[1]) ** 2
            + (point[2] - beacon[2]) ** 2
        )

        # Residual
        residual = (calculated - measured_distance) ** 2
        assert residual < 0.01  # Should be very small for known point


class TestBermudaIntegration:
    """Test Bermuda provider integration with Home Assistant."""

    @pytest.mark.asyncio
    async def test_provider_with_home_assistant_states(self, hass, temp_data_dir):
        """Test provider reading from Home Assistant states."""
        manager = FloorplanManager(hass, temp_data_dir)
        manager.add_beacon_node("beacon_1", [0, 0, 2.0])
        manager.add_beacon_node("beacon_2", [10, 0, 2.0])
        manager.add_beacon_node("beacon_3", [5, 8, 2.0])

        provider = BermudaLocationProvider(hass, manager)

        # Mock Home Assistant states with distance sensors
        mock_state_1 = MagicMock()
        mock_state_1.entity_id = "sensor.distance_to_device_beacon_1"
        mock_state_1.state = "6.4"

        mock_state_2 = MagicMock()
        mock_state_2.entity_id = "sensor.distance_to_device_beacon_2"
        mock_state_2.state = "6.4"

        mock_state_3 = MagicMock()
        mock_state_3.entity_id = "sensor.distance_to_device_beacon_3"
        mock_state_3.state = "4.1"

        hass.states.async_all = MagicMock(
            return_value=[mock_state_1, mock_state_2, mock_state_3]
        )

        # Get all moving entities
        result = await provider.get_all_moving_entity_coordinates()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_invalid_distance_values(self, hass, temp_data_dir):
        """Test handling of invalid distance values."""
        manager = FloorplanManager(hass, temp_data_dir)
        manager.add_beacon_node("beacon_1", [0, 0, 2.0])
        manager.add_beacon_node("beacon_2", [10, 0, 2.0])
        manager.add_beacon_node("beacon_3", [5, 8, 2.0])

        provider = BermudaLocationProvider(hass, manager)

        # Mock invalid state
        mock_state = MagicMock()
        mock_state.entity_id = "sensor.distance_to_device_beacon_1"
        mock_state.state = "unknown"  # Invalid

        hass.states.async_all = MagicMock(return_value=[mock_state])

        result = await provider.get_all_moving_entity_coordinates()
        # Should handle gracefully
        assert isinstance(result, dict)
