"""Constants for the Floorplan integration."""

DOMAIN = "floorplan"
DATA_FLOORPLAN = "floorplan"

# Config keys
CONF_ROOMS = "rooms"
CONF_FLOORS = "floors"
CONF_STATIC_ENTITIES = "static_entities"
CONF_MOVING_ENTITIES = "moving_entities"
CONF_PROVIDERS = "providers"

# Provider configuration keys
CONF_BERMUDA = "bermuda"
CONF_ENABLED = "enabled"

# Moving entities config keys
CONF_MOVING_BEACON_NODES = "beacon_nodes"

# Beacon node config keys
BEACON_NODE_COORDINATES = "coordinates"

# Room configuration keys
ROOM_NAME = "name"
ROOM_AREA = "area"
ROOM_BOUNDARIES = "boundaries"
ROOM_FLOOR = "floor"

# Floor configuration keys
FLOOR_HEIGHT = "height"

# Static entity configuration keys
ENTITY_ID = "entity_id"
ENTITY_COORDINATES = "coordinates"

# Default paths
DEFAULT_DATA_DIR = "floorplan"
FLOORPLAN_CONFIG_FILE = "floorplan.yaml"

# Units: all coordinates and dimensions are in meters
UNIT_METERS = "m"
