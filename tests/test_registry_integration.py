"""Tests for Home Assistant registry integration."""

from unittest.mock import MagicMock, Mock
import pytest

from custom_components.floorplan.floorplan_manager import FloorplanManager
from custom_components.floorplan.const import (
    ROOM_NAME,
    ROOM_FLOOR,
    ROOM_AREA,
    ROOM_BOUNDARIES,
    FLOOR_HEIGHT,
)


class TestRegistryIntegration:
    """Test Home Assistant registry integration for floor and room names."""

    @pytest.fixture
    def manager_with_registries(self, hass, temp_data_dir):
        """Create a FloorplanManager with mocked registries."""
        manager = FloorplanManager(hass, temp_data_dir)
        
        # Mock floor registry
        floor_registry_mock = Mock()
        floor_entry_ground = Mock()
        floor_entry_ground.name = "Ground Floor"
        floor_entry_first = Mock()
        floor_entry_first.name = "First Floor"
        
        def get_floor(floor_id):
            if floor_id == "ground":
                return floor_entry_ground
            elif floor_id == "first":
                return floor_entry_first
            return None
        
        floor_registry_mock.async_get_floor = get_floor
        
        # Mock area registry
        area_registry_mock = Mock()
        area_entry_living = Mock()
        area_entry_living.name = "Living Room"
        area_entry_kitchen = Mock()
        area_entry_kitchen.name = "Kitchen"
        area_entry_bedroom = Mock()
        area_entry_bedroom.name = "Master Bedroom"
        
        def get_area(area_id):
            if area_id == "living_room":
                return area_entry_living
            elif area_id == "kitchen":
                return area_entry_kitchen
            elif area_id == "bedroom":
                return area_entry_bedroom
            return None
        
        area_registry_mock.async_get_area = get_area
        
        # Patch the registry accessors
        import custom_components.floorplan.floorplan_manager as fm_module
        original_floor_get = fm_module.fr.async_get
        original_area_get = fm_module.ar.async_get
        
        fm_module.fr.async_get = lambda hass: floor_registry_mock
        fm_module.ar.async_get = lambda hass: area_registry_mock
        
        yield manager
        
        # Restore original functions
        fm_module.fr.async_get = original_floor_get
        fm_module.ar.async_get = original_area_get

    def test_room_name_from_area_registry(self, manager_with_registries):
        """Test that room name is fetched from area registry when not in config."""
        manager = manager_with_registries
        
        # Add a room without a name but with an area_id
        manager.floorplan_data["rooms"]["room1"] = {
            ROOM_FLOOR: "ground",
            ROOM_AREA: "living_room",
            ROOM_BOUNDARIES: [[0, 0], [5, 0], [5, 4], [0, 4]],
        }
        
        # Get rooms by floor - should enrich with name from area registry
        rooms = manager.get_rooms_by_floor("ground")
        
        assert "room1" in rooms
        assert rooms["room1"][ROOM_NAME] == "Living Room"
        assert rooms["room1"][ROOM_AREA] == "living_room"

    def test_room_config_name_takes_precedence(self, manager_with_registries):
        """Test that configured room name takes precedence over area registry."""
        manager = manager_with_registries
        
        # Add a room with both a name and an area_id
        manager.floorplan_data["rooms"]["room1"] = {
            ROOM_NAME: "My Custom Living Room",
            ROOM_FLOOR: "ground",
            ROOM_AREA: "living_room",
            ROOM_BOUNDARIES: [[0, 0], [5, 0], [5, 4], [0, 4]],
        }
        
        # Get rooms by floor - should use configured name
        rooms = manager.get_rooms_by_floor("ground")
        
        assert "room1" in rooms
        assert rooms["room1"][ROOM_NAME] == "My Custom Living Room"

    def test_room_without_area_id_has_no_name(self, manager_with_registries):
        """Test that room without name or area_id has no name."""
        manager = manager_with_registries
        
        # Add a room without name or area_id
        manager.floorplan_data["rooms"]["room1"] = {
            ROOM_FLOOR: "ground",
            ROOM_BOUNDARIES: [[0, 0], [5, 0], [5, 4], [0, 4]],
        }
        
        # Get rooms by floor
        rooms = manager.get_rooms_by_floor("ground")
        
        assert "room1" in rooms
        assert ROOM_NAME not in rooms["room1"]

    def test_floor_name_from_registry(self, manager_with_registries):
        """Test that floor name is fetched from floor registry."""
        manager = manager_with_registries
        
        # Add floor
        manager.add_floor("ground", 2.4)
        
        # Get floor - should enrich with name from registry
        floor = manager.get_floor("ground")
        
        assert floor is not None
        assert floor[FLOOR_HEIGHT] == 2.4
        assert floor["name"] == "Ground Floor"

    def test_all_floors_enriched_with_names(self, manager_with_registries):
        """Test that all floors are enriched with names from registry."""
        manager = manager_with_registries
        
        # Add multiple floors
        manager.add_floor("ground", 2.4)
        manager.add_floor("first", 5.2)
        
        # Get all floors
        floors = manager.get_floors()
        
        assert "ground" in floors
        assert floors["ground"]["name"] == "Ground Floor"
        assert "first" in floors
        assert floors["first"]["name"] == "First Floor"

    def test_multiple_rooms_enriched(self, manager_with_registries):
        """Test that multiple rooms on same floor are all enriched."""
        manager = manager_with_registries
        
        # Add multiple rooms without names
        manager.floorplan_data["rooms"]["room1"] = {
            ROOM_FLOOR: "ground",
            ROOM_AREA: "living_room",
            ROOM_BOUNDARIES: [[0, 0], [5, 0], [5, 4], [0, 4]],
        }
        manager.floorplan_data["rooms"]["room2"] = {
            ROOM_FLOOR: "ground",
            ROOM_AREA: "kitchen",
            ROOM_BOUNDARIES: [[5, 0], [10, 0], [10, 4], [5, 4]],
        }
        manager.floorplan_data["rooms"]["room3"] = {
            ROOM_NAME: "Guest Room",  # Has explicit name
            ROOM_FLOOR: "first",
            ROOM_AREA: "bedroom",
            ROOM_BOUNDARIES: [[0, 0], [4, 0], [4, 3], [0, 3]],
        }
        
        # Get rooms by floor
        ground_rooms = manager.get_rooms_by_floor("ground")
        first_rooms = manager.get_rooms_by_floor("first")
        
        # Check ground floor rooms
        assert len(ground_rooms) == 2
        assert ground_rooms["room1"][ROOM_NAME] == "Living Room"
        assert ground_rooms["room2"][ROOM_NAME] == "Kitchen"
        
        # Check first floor room - should keep explicit name
        assert len(first_rooms) == 1
        assert first_rooms["room3"][ROOM_NAME] == "Guest Room"

    def test_registry_error_handling(self, hass, temp_data_dir):
        """Test that registry errors are handled gracefully."""
        manager = FloorplanManager(hass, temp_data_dir)
        
        # Mock registry to raise an error
        import custom_components.floorplan.floorplan_manager as fm_module
        original_floor_get = fm_module.fr.async_get
        original_area_get = fm_module.ar.async_get
        
        def raise_error(hass):
            raise Exception("Registry not available")
        
        fm_module.fr.async_get = raise_error
        fm_module.ar.async_get = raise_error
        
        try:
            # Add floor and room
            manager.add_floor("ground", 2.4)
            manager.floorplan_data["rooms"]["room1"] = {
                ROOM_FLOOR: "ground",
                ROOM_AREA: "living_room",
                ROOM_BOUNDARIES: [[0, 0], [5, 0], [5, 4], [0, 4]],
            }
            
            # Get floor and rooms - should not crash
            floor = manager.get_floor("ground")
            rooms = manager.get_rooms_by_floor("ground")
            
            # Should return data without names from registry
            assert floor is not None
            assert "name" not in floor
            assert "room1" in rooms
            assert ROOM_NAME not in rooms["room1"]
        finally:
            # Restore original functions
            fm_module.fr.async_get = original_floor_get
            fm_module.ar.async_get = original_area_get

    def test_original_config_not_modified(self, manager_with_registries):
        """Test that original floorplan config is not modified by enrichment."""
        manager = manager_with_registries
        
        # Add room without name
        original_room_data = {
            ROOM_FLOOR: "ground",
            ROOM_AREA: "living_room",
            ROOM_BOUNDARIES: [[0, 0], [5, 0], [5, 4], [0, 4]],
        }
        manager.floorplan_data["rooms"]["room1"] = original_room_data.copy()
        
        # Get rooms - should enrich
        rooms = manager.get_rooms_by_floor("ground")
        assert rooms["room1"][ROOM_NAME] == "Living Room"
        
        # Original config should not have the name
        assert ROOM_NAME not in manager.floorplan_data["rooms"]["room1"]
