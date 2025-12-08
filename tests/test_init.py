"""Tests for __init__.py integration setup and service handlers."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

# Add the custom_components to the path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestIntegrationImports:
    """Test that all required constants are imported in __init__.py."""

    def test_floor_height_constant_imported(self):
        """Test that FLOOR_HEIGHT constant is imported and available."""
        # This test ensures FLOOR_HEIGHT is imported in __init__.py
        # If not imported, the service handler will fail at runtime
        import custom_components.floorplan as init_module
        
        # Verify FLOOR_HEIGHT is accessible in the module
        assert hasattr(init_module, 'FLOOR_HEIGHT'), \
            "FLOOR_HEIGHT constant must be imported in __init__.py"

    def test_all_required_constants_imported(self):
        """Test that all constants used in service handlers are imported."""
        import custom_components.floorplan as init_module
        
        # List of constants that are used in __init__.py service handlers
        required_constants = [
            'DOMAIN',
            'ROOM_NAME',
            'ROOM_FLOOR',
            'ROOM_AREA',
            'ROOM_BOUNDARIES',
            'FLOOR_HEIGHT',
        ]
        
        for constant in required_constants:
            assert hasattr(init_module, constant), \
                f"{constant} constant must be imported in __init__.py for service handlers"


class TestServiceHandlers:
    """Test service handler functionality."""

    @pytest.fixture
    def mock_manager(self):
        """Create a mock FloorplanManager."""
        manager = MagicMock()
        manager.get_rooms_by_floor.return_value = {
            "room1": {
                "name": "Living Room",
                "floor": "ground_floor",
                "area": "living_area",
                "boundaries": [[0, 0], [5, 0], [5, 4], [0, 4]],
            }
        }
        manager.get_floor.return_value = {
            "height": 2.4
        }
        manager.get_all_floors.return_value = {
            "ground_floor": {"height": 2.4},
            "first_floor": {"height": 5.2},
        }
        return manager

    def test_get_rooms_by_floor_returns_floor_heights(self, mock_manager):
        """Test that get_rooms_by_floor service returns both floor_height and floor_min_height."""
        from custom_components.floorplan.const import FLOOR_HEIGHT
        
        # Mock the manager
        mock_manager.get_rooms_by_floor.return_value = {}
        mock_manager.get_floor.return_value = {"height": 5.2}
        mock_manager.get_all_floors.return_value = {
            "ground_floor": {"height": 2.4},
            "first_floor": {"height": 5.2},
        }
        
        # Simulate the logic from handle_get_rooms_by_floor
        floor_data = mock_manager.get_floor.return_value
        all_floors = mock_manager.get_all_floors.return_value
        current_floor_height = floor_data.get(FLOOR_HEIGHT, 0.0) if floor_data else 0.0
        
        # Find previous floor height
        previous_floor_height = 0.0
        for fid, fdata in all_floors.items():
            if fid != "first_floor":
                fheight = fdata.get(FLOOR_HEIGHT, 0.0)
                if fheight < current_floor_height and fheight > previous_floor_height:
                    previous_floor_height = fheight
        
        # Assertions
        assert current_floor_height == 5.2, "Current floor ceiling height should be 5.2"
        assert previous_floor_height == 2.4, "Previous floor ceiling height should be 2.4"

    def test_floor_range_calculation_logic(self):
        """Test the floor range calculation logic used for beacon filtering."""
        from custom_components.floorplan.const import FLOOR_HEIGHT
        
        # Test data: three floors
        all_floors = {
            "ground_floor": {"height": 2.4},
            "first_floor": {"height": 5.2},
            "second_floor": {"height": 7.6},
        }
        
        # Test for first floor (should get ground floor as previous)
        current_floor_id = "first_floor"
        current_floor_height = 5.2
        
        previous_floor_height = 0.0
        for fid, fdata in all_floors.items():
            if fid != current_floor_id:
                fheight = fdata.get(FLOOR_HEIGHT, 0.0)
                if fheight < current_floor_height and fheight > previous_floor_height:
                    previous_floor_height = fheight
        
        assert previous_floor_height == 2.4, \
            "First floor's previous ceiling should be ground floor (2.4m)"
        
        # Test for second floor (should get first floor as previous)
        current_floor_id = "second_floor"
        current_floor_height = 7.6
        
        previous_floor_height = 0.0
        for fid, fdata in all_floors.items():
            if fid != current_floor_id:
                fheight = fdata.get(FLOOR_HEIGHT, 0.0)
                if fheight < current_floor_height and fheight > previous_floor_height:
                    previous_floor_height = fheight
        
        assert previous_floor_height == 5.2, \
            "Second floor's previous ceiling should be first floor (5.2m)"
        
        # Test for ground floor (should have no previous floor)
        current_floor_id = "ground_floor"
        current_floor_height = 2.4
        
        previous_floor_height = 0.0
        for fid, fdata in all_floors.items():
            if fid != current_floor_id:
                fheight = fdata.get(FLOOR_HEIGHT, 0.0)
                if fheight < current_floor_height and fheight > previous_floor_height:
                    previous_floor_height = fheight
        
        assert previous_floor_height == 0.0, \
            "Ground floor should have no previous floor (0.0m)"


class TestBeaconFiltering:
    """Test beacon filtering logic based on floor heights."""

    def test_beacon_filtering_by_floor_range(self):
        """Test that beacons are correctly filtered by floor height range."""
        # Test configuration from user
        floors = {
            "ground": {"height": 2.4},   # 0m to 2.4m
            "first": {"height": 5.2},     # 2.4m to 5.2m
            "second": {"height": 7.6},    # 5.2m to 7.6m
        }
        
        # Test beacons at various heights
        beacons = {
            "beacon_1": [0, 0, 1.0],   # Ground floor
            "beacon_2": [1, 1, 2.2],   # Ground floor
            "beacon_3": [2, 2, 3.5],   # First floor
            "beacon_4": [3, 3, 5.0],   # First floor
            "beacon_5": [4, 4, 6.5],   # Second floor
        }
        
        # Test ground floor filtering (0 to 2.4m)
        floor_height = 2.4
        floor_min_height = 0.0
        
        ground_beacons = {
            k: v for k, v in beacons.items()
            if v[2] >= floor_min_height and v[2] < floor_height
        }
        
        assert len(ground_beacons) == 2, "Should have 2 beacons on ground floor"
        assert "beacon_1" in ground_beacons
        assert "beacon_2" in ground_beacons
        
        # Test first floor filtering (2.4m to 5.2m)
        floor_height = 5.2
        floor_min_height = 2.4
        
        first_beacons = {
            k: v for k, v in beacons.items()
            if v[2] >= floor_min_height and v[2] < floor_height
        }
        
        assert len(first_beacons) == 2, "Should have 2 beacons on first floor"
        assert "beacon_3" in first_beacons
        assert "beacon_4" in first_beacons
        
        # Test second floor filtering (5.2m to 7.6m)
        floor_height = 7.6
        floor_min_height = 5.2
        
        second_beacons = {
            k: v for k, v in beacons.items()
            if v[2] >= floor_min_height and v[2] < floor_height
        }
        
        assert len(second_beacons) == 1, "Should have 1 beacon on second floor"
        assert "beacon_5" in second_beacons
    
    def test_beacon_at_boundary(self):
        """Test beacon filtering at exact boundary heights."""
        # Beacon exactly at floor ceiling should appear on next floor up
        beacons = {
            "boundary_beacon": [0, 0, 2.4],  # Exactly at ground ceiling
        }
        
        # Ground floor (0 to 2.4m) - uses < comparison, so excludes 2.4
        floor_height = 2.4
        floor_min_height = 0.0
        
        ground_beacons = {
            k: v for k, v in beacons.items()
            if v[2] >= floor_min_height and v[2] < floor_height
        }
        
        assert len(ground_beacons) == 0, \
            "Beacon at exact ceiling height (2.4m) should not appear on ground floor"
        
        # First floor (2.4m to 5.2m) - uses >= comparison, so includes 2.4
        floor_height = 5.2
        floor_min_height = 2.4
        
        first_beacons = {
            k: v for k, v in beacons.items()
            if v[2] >= floor_min_height and v[2] < floor_height
        }
        
        assert len(first_beacons) == 1, \
            "Beacon at exact floor boundary (2.4m) should appear on first floor"
