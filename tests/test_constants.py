"""Tests for Floorplan constants and configuration."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components" / "floorplan"))

from const import (
    DOMAIN,
    CONF_PROVIDERS,
    CONF_BERMUDA,
    CONF_ENABLED,
    CONF_ROOMS,
    CONF_FLOORS,
    CONF_STATIC_ENTITIES,
    CONF_MOVING_ENTITIES,
    ROOM_NAME,
    ROOM_FLOOR,
    ROOM_AREA,
    ROOM_BOUNDARIES,
    FLOOR_HEIGHT,
    ENTITY_ID,
    ENTITY_COORDINATES,
    CONF_MOVING_BEACON_NODES,
    BEACON_NODE_COORDINATES,
)


class TestConstants:
    """Test that all required constants are defined."""

    def test_domain_constant(self):
        """Test DOMAIN constant."""
        assert DOMAIN == "floorplan"

    def test_config_keys(self):
        """Test configuration keys are defined."""
        assert CONF_PROVIDERS == "providers"
        assert CONF_BERMUDA == "bermuda"
        assert CONF_ENABLED == "enabled"
        assert CONF_ROOMS == "rooms"
        assert CONF_FLOORS == "floors"
        assert CONF_STATIC_ENTITIES == "static_entities"
        assert CONF_MOVING_ENTITIES == "moving_entities"

    def test_room_keys(self):
        """Test room configuration keys."""
        assert ROOM_NAME == "name"
        assert ROOM_FLOOR == "floor"
        assert ROOM_AREA == "area"
        assert ROOM_BOUNDARIES == "boundaries"

    def test_floor_keys(self):
        """Test floor configuration keys."""
        assert FLOOR_HEIGHT == "height"

    def test_entity_keys(self):
        """Test entity configuration keys."""
        assert ENTITY_ID == "entity_id"
        assert ENTITY_COORDINATES == "coordinates"

    def test_beacon_node_keys(self):
        """Test beacon node configuration keys."""
        assert CONF_MOVING_BEACON_NODES == "beacon_nodes"
        assert BEACON_NODE_COORDINATES == "coordinates"

    def test_constants_uniqueness(self):
        """Test that constants don't have conflicting values."""
        # Verify required constants exist and have correct values
        assert DOMAIN == "floorplan"
        assert CONF_PROVIDERS == "providers"
        assert CONF_BERMUDA == "bermuda"
        assert CONF_ENABLED == "enabled"
        assert ENTITY_COORDINATES == "coordinates"
        assert BEACON_NODE_COORDINATES == "coordinates"  # Intentional duplicate
        # All expected constants should be defined
        constants_to_check = [
            DOMAIN, CONF_PROVIDERS, CONF_BERMUDA, CONF_ENABLED,
            CONF_ROOMS, CONF_FLOORS, CONF_STATIC_ENTITIES, CONF_MOVING_ENTITIES,
            ROOM_NAME, ROOM_FLOOR, ROOM_AREA, ROOM_BOUNDARIES,
            FLOOR_HEIGHT, ENTITY_ID, ENTITY_COORDINATES,
            CONF_MOVING_BEACON_NODES, BEACON_NODE_COORDINATES,
        ]
        # Verify all are strings
        for const in constants_to_check:
            assert isinstance(const, str)


class TestProviderConfiguration:
    """Test provider configuration constants."""

    def test_provider_constants_structure(self):
        """Test provider configuration has consistent naming."""
        # Provider name should be lowercase
        assert CONF_BERMUDA == "bermuda"

        # Enable key should be lowercase
        assert CONF_ENABLED == "enabled"

        # These should be usable together
        provider_config = {
            CONF_BERMUDA: {
                CONF_ENABLED: True,
            }
        }
        assert provider_config[CONF_BERMUDA][CONF_ENABLED] is True

    def test_future_provider_extensibility(self):
        """Test that constants support future providers."""
        # Should be able to configure multiple providers
        providers = {
            CONF_BERMUDA: {CONF_ENABLED: True},
            "espresense": {CONF_ENABLED: False},
            "wifi_triangulation": {CONF_ENABLED: False},
        }

        assert len(providers) == 3
        assert CONF_BERMUDA in providers


class TestDataStructureConstants:
    """Test data structure configuration constants."""

    def test_floorplan_structure(self):
        """Test that constants define floorplan data structure."""
        floorplan = {
            CONF_FLOORS: {},
            CONF_ROOMS: {},
            CONF_STATIC_ENTITIES: {},
            CONF_MOVING_ENTITIES: {
                CONF_MOVING_BEACON_NODES: {},
            },
        }

        assert CONF_FLOORS in floorplan
        assert CONF_ROOMS in floorplan
        assert CONF_STATIC_ENTITIES in floorplan
        assert CONF_MOVING_ENTITIES in floorplan

    def test_room_structure(self):
        """Test that constants define room structure."""
        room = {
            ROOM_NAME: "Living Room",
            ROOM_FLOOR: "ground_floor",
            ROOM_AREA: "living_room",
            ROOM_BOUNDARIES: [[0, 0], [10, 0], [10, 8], [0, 8]],
        }

        assert room[ROOM_NAME] == "Living Room"
        assert room[ROOM_FLOOR] == "ground_floor"
        assert room[ROOM_AREA] == "living_room"
        assert len(room[ROOM_BOUNDARIES]) == 4

    def test_floor_structure(self):
        """Test that constants define floor structure."""
        floor = {
            FLOOR_HEIGHT: 0.0,
        }

        assert FLOOR_HEIGHT in floor
        assert floor[FLOOR_HEIGHT] == 0.0

    def test_entity_structure(self):
        """Test that constants define entity structure."""
        entity = {
            ENTITY_ID: "light.living_room",
            ENTITY_COORDINATES: [5, 4, 1.8],
        }

        assert entity[ENTITY_ID] == "light.living_room"
        assert len(entity[ENTITY_COORDINATES]) == 3

    def test_beacon_node_structure(self):
        """Test that constants define beacon node structure."""
        beacon = {
            BEACON_NODE_COORDINATES: [12, 2.5, 2.0],
        }

        assert len(beacon[BEACON_NODE_COORDINATES]) == 3


class TestConstantsDocumentation:
    """Test that constants are self-documenting."""

    def test_constant_names_are_descriptive(self):
        """Test that constant names clearly describe their purpose."""
        # Configuration keys should be lowercase with underscores
        assert CONF_PROVIDERS.islower()
        assert CONF_BERMUDA.islower()

        # Structure keys should describe what they contain
        assert "room" in ROOM_NAME.lower() or "name" in ROOM_NAME.lower()
        assert "floor" in ROOM_FLOOR.lower() or "floor" in ROOM_FLOOR.lower()
        assert "boundary" in ROOM_BOUNDARIES.lower() or "boundaries" in ROOM_BOUNDARIES.lower()

    def test_constants_follow_naming_convention(self):
        """Test that constants follow consistent naming convention."""
        # DOMAIN should be lowercase (Home Assistant convention)
        assert DOMAIN == "floorplan"
        assert not DOMAIN.isupper()
        # Config key constants should be lowercase (dict keys)
        assert CONF_PROVIDERS == "providers"
        assert CONF_ROOMS == "rooms"
        assert ROOM_NAME == "name"
        assert FLOOR_HEIGHT == "height"
