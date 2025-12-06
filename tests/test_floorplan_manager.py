"""Tests for FloorplanManager."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

# Add the custom_components to the path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.floorplan.floorplan_manager import FloorplanManager
from custom_components.floorplan.const import FLOORPLAN_CONFIG_FILE


class TestFloorplanManager:
    """Test FloorplanManager functionality."""

    @pytest.fixture
    def manager(self, hass, temp_data_dir):
        """Create a FloorplanManager instance."""
        return FloorplanManager(hass, temp_data_dir)

    @pytest.mark.asyncio
    async def test_init(self, manager, temp_data_dir):
        """Test manager initialization."""
        assert manager.hass is not None
        assert manager.data_dir == temp_data_dir
        assert manager.config_file == temp_data_dir / FLOORPLAN_CONFIG_FILE
        assert "floors" in manager.floorplan_data
        assert "rooms" in manager.floorplan_data
        assert "static_entities" in manager.floorplan_data
        assert "moving_entities" in manager.floorplan_data

    @pytest.mark.asyncio
    async def test_load_floorplan_creates_empty(self, manager):
        """Test loading creates empty config when file doesn't exist."""
        await manager.async_load_floorplan()
        assert manager.config_file.exists()
        assert manager.floorplan_data["floors"] == {}
        assert manager.floorplan_data["rooms"] == {}

    @pytest.mark.asyncio
    async def test_save_and_load_floorplan(self, manager, sample_floorplan_data):
        """Test saving and loading floorplan configuration."""
        manager.floorplan_data = sample_floorplan_data

        await manager.async_save_floorplan()
        assert manager.config_file.exists()

        # Create new manager and load
        new_manager = FloorplanManager(manager.hass, manager.data_dir)
        await new_manager.async_load_floorplan()

        assert new_manager.floorplan_data["floors"] == sample_floorplan_data["floors"]
        assert new_manager.floorplan_data["rooms"] == sample_floorplan_data["rooms"]

    def test_add_floor(self, manager):
        """Test adding a floor."""
        manager.add_floor("ground_floor", 0)
        manager.add_floor("1st_floor", 3.2)

        assert "ground_floor" in manager.floorplan_data["floors"]
        assert "1st_floor" in manager.floorplan_data["floors"]
        assert manager.floorplan_data["floors"]["ground_floor"]["height"] == 0
        assert manager.floorplan_data["floors"]["1st_floor"]["height"] == 3.2

    def test_add_room(self, manager):
        """Test adding a room."""
        manager.add_floor("ground_floor", 0)
        manager.add_room(
            "living_room",
            "Living Room",
            "ground_floor",
            [[0, 0], [10, 0], [10, 8], [0, 8]],
            "living_room",
        )

        assert "living_room" in manager.floorplan_data["rooms"]
        room = manager.floorplan_data["rooms"]["living_room"]
        assert room["name"] == "Living Room"
        assert room["floor"] == "ground_floor"
        assert room["area"] == "living_room"
        assert len(room["boundaries"]) == 4

    def test_add_static_entity(self, manager):
        """Test adding a static entity."""
        manager.add_static_entity("light.living_room", [5, 4, 1.8])
        manager.add_static_entity("camera.front_door", [0, 0, 2.2])

        assert "light.living_room" in manager.floorplan_data["static_entities"]
        assert "camera.front_door" in manager.floorplan_data["static_entities"]
        assert manager.floorplan_data["static_entities"]["light.living_room"]["coordinates"] == [5, 4, 1.8]

    def test_update_static_entity(self, manager):
        """Test updating a static entity."""
        manager.add_static_entity("light.living_room", [5, 4, 1.8])
        manager.update_static_entity("light.living_room", [5.5, 4.2, 1.9])

        assert manager.floorplan_data["static_entities"]["light.living_room"]["coordinates"] == [5.5, 4.2, 1.9]

    def test_delete_static_entity(self, manager):
        """Test deleting a static entity."""
        manager.add_static_entity("light.living_room", [5, 4, 1.8])
        assert "light.living_room" in manager.floorplan_data["static_entities"]

        manager.delete_static_entity("light.living_room")
        assert "light.living_room" not in manager.floorplan_data["static_entities"]

    def test_get_static_entity(self, manager):
        """Test getting a static entity."""
        manager.add_static_entity("light.living_room", [5, 4, 1.8])
        entity = manager.get_static_entity("light.living_room")

        assert entity == {"coordinates": [5, 4, 1.8]}
        assert entity["coordinates"] == [5, 4, 1.8]

    def test_get_static_entity_not_found(self, manager):
        """Test getting a non-existent static entity."""
        coordinates = manager.get_static_entity("light.unknown")
        assert coordinates is None

    def test_get_all_static_entities(self, manager):
        """Test getting all static entities."""
        manager.add_static_entity("light.living_room", [5, 4, 1.8])
        manager.add_static_entity("camera.front_door", [0, 0, 2.2])

        all_entities = manager.get_all_static_entities()
        assert len(all_entities) == 2
        assert all_entities["light.living_room"]["coordinates"] == [5, 4, 1.8]
        assert all_entities["camera.front_door"]["coordinates"] == [0, 0, 2.2]

    def test_add_beacon_node(self, manager):
        """Test adding a beacon node."""
        manager.add_beacon_node("D4:5F:4E:A1:23:45", [12, 2.5, 2.0])
        manager.add_beacon_node("A3:2B:1C:F9:87:56", [5, 4, 2.0])

        nodes = manager.get_beacon_nodes()
        assert len(nodes) == 2
        assert nodes["D4:5F:4E:A1:23:45"]["coordinates"] == [12, 2.5, 2.0]

    def test_update_beacon_node(self, manager):
        """Test updating a beacon node."""
        manager.add_beacon_node("D4:5F:4E:A1:23:45", [12, 2.5, 2.0])
        manager.update_beacon_node("D4:5F:4E:A1:23:45", [12.5, 2.3, 2.0])

        nodes = manager.get_beacon_nodes()
        assert nodes["D4:5F:4E:A1:23:45"]["coordinates"] == [12.5, 2.3, 2.0]

    def test_delete_beacon_node(self, manager):
        """Test deleting a beacon node."""
        manager.add_beacon_node("D4:5F:4E:A1:23:45", [12, 2.5, 2.0])
        assert len(manager.get_beacon_nodes()) == 1

        manager.delete_beacon_node("D4:5F:4E:A1:23:45")
        assert len(manager.get_beacon_nodes()) == 0

    def test_get_rooms_by_floor(self, manager, sample_floorplan_data):
        """Test getting rooms by floor."""
        manager.floorplan_data = sample_floorplan_data

        rooms = manager.get_rooms_by_floor("ground_floor")
        assert len(rooms) == 2
        assert "living_room" in rooms
        assert "kitchen" in rooms

    def test_get_room(self, manager, sample_floorplan_data):
        """Test getting a specific room."""
        manager.floorplan_data = sample_floorplan_data

        room = manager.get_room("living_room")
        assert room is not None
        assert room["name"] == "Living Room"
        assert room["floor"] == "ground_floor"

    def test_get_room_not_found(self, manager):
        """Test getting a non-existent room."""
        room = manager.get_room("unknown_room")
        assert room is None

    def test_get_all_floors(self, manager, sample_floorplan_data):
        """Test getting all floors."""
        manager.floorplan_data = sample_floorplan_data

        floors = manager.get_all_floors()
        assert len(floors) == 2
        assert "ground_floor" in floors
        assert "1st_floor" in floors

    @pytest.mark.asyncio
    async def test_corrupted_yaml_file(self, manager):
        """Test handling of corrupted YAML file."""
        # Write invalid YAML
        manager.config_file.write_text("invalid: yaml: content:")

        # Should handle gracefully
        await manager.async_load_floorplan()
        # Should still have empty template
        assert "floors" in manager.floorplan_data

    def test_coordinate_validation(self, manager):
        """Test that coordinates are properly stored and retrieved."""
        coordinates = [5.5, 4.2, 1.8]
        manager.add_static_entity("light.test", coordinates)

        retrieved = manager.get_static_entity("light.test")
        assert retrieved == {"coordinates": coordinates}
        assert retrieved["coordinates"] == coordinates
        assert len(retrieved["coordinates"]) == 3
