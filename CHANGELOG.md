# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2025-12-09

### Fixed
- **Bermuda beacon matching** now correctly matches against device friendly names by normalizing them (lowercase with underscores)
- Bermuda sensors like `sensor.phone_distance_to_kitchen_bluetooth_proxy` now match beacons with friendly name "Kitchen Bluetooth Proxy"
- Added name normalization helper function for flexible matching
- Supports both new dict format `{coordinates, name}` and legacy list format for backward compatibility

### Changed
- Removed excessive debug/warning logging from Bermuda provider that was flooding logs (200+ messages)
- Silent handling of expected conditions: missing beacon matches, insufficient measurements, out-of-range devices
- Only critical trilateration errors are now logged (excluding common singular matrix errors)
- Dramatically reduced log verbosity for normal operation

## [0.3.0] - 2025-12-08

### Changed
- **BREAKING:** `get_all_moving_entity_coordinates` now returns entities with metadata structure: `{coordinates: [x,y,z], confidence: float, last_updated: str}`
- Previously returned simple coordinate arrays, now returns full entity tracking data

### Added
- Debug logging for Bermuda distance sensor discovery and device grouping
- Confidence scores for triangulated positions (currently fixed at 0.85, TODO: calculate from triangulation error)
- ISO 8601 timestamps for last position update

### Fixed
- Bermuda provider now returns documented API format matching service specification

## [0.2.9] - 2025-12-08

### Added
- Bluetooth beacon device friendly name enrichment from Home Assistant device registry
- New `get_all_beacon_node_data()` method returning beacon coordinates and names
- `_get_device_name_from_registry()` helper method to fetch device names by MAC address

### Changed
- `get_all_entity_coordinates` service now returns beacon nodes with structure `{coordinates: [x,y,z], name: "Device Name"}` instead of just coordinates
- Beacon names automatically fetched from device registry (uses `name_by_user` if set, otherwise `name`)
- Graceful fallback when device not found in registry

## [0.2.8] - 2025-12-08

### Added
- Automatic floor friendly name enrichment from Home Assistant floor registry
- Automatic room name enrichment from Home Assistant area registry when not specified in config
- 8 comprehensive tests for registry integration (`test_registry_integration.py`)
- Graceful error handling when registries are unavailable

### Changed
- Room names are now optional in config - will use area name from HA if available
- Floor data now includes friendly "name" field from floor registry
- `get_rooms_by_floor()`, `get_floor()`, and `get_floors()` automatically enrich data with registry names
- Original YAML config remains unchanged - enrichment happens at read-time only

## [0.2.7] - 2025-12-08

### Added
- Integration import validation tests to prevent missing constant imports (`test_init.py`)
- Floor range calculation logic tests with multi-floor scenarios
- Beacon filtering tests with boundary condition validation (tests beacons at exact ceiling heights)

### Changed
- `get_rooms_by_floor` service now includes `floor_height` (ceiling) and `floor_min_height` (floor below's ceiling) for proper beacon filtering
- Service calculates floor range by finding the highest floor below the current floor

### Fixed
- Floor height semantics: `height` represents the ceiling height of each floor, not the floor level
- Missing `FLOOR_HEIGHT` import in `__init__.py` causing runtime errors

## [0.2.5] - 2025-12-08

### Added
- Automatic file watching for `floorplan.yaml` changes with 2-second polling interval
- `floorplan.reload` service to manually reload configuration
- Configuration automatically reloads when file is modified (no restart needed)
- Example `floorplan.yaml.example` with complete configuration reference

### Changed
- File watcher task properly cleaned up on integration unload

## [0.2.4] - 2025-12-08

### Fixed
- Use `SupportsResponse.ONLY` enum instead of deprecated boolean for service response declarations
- Services now correctly return data payloads to frontend (was only returning context wrapper)

## [0.2.3] - 2025-12-07

### Fixed
- Added `supports_response=True` to all data-returning services to enable frontend data access
- Fixed blocking import by using direct import instead of `import_module()` in event loop
- Services now properly return data to Lovelace cards and frontend integrations

## [0.2.2] - 2025-12-07

### Fixed
- Import room constants in service handler
- Added debug logging for get_rooms_by_floor service

## [0.2.1] - 2025-12-07

### Added
- `get_rooms_by_floor` service for card integration
- Room data API for frontend visualization
- Provider configuration UI in config_flow
- Ability to enable/disable Bermuda location provider
- Config translations for provider settings

### Fixed
- Missing services.yaml documentation
- CONFIG_SCHEMA requirement for Home Assistant validation

## [0.2.0] - 2025-12-06

### Added
- Beacon node infrastructure for location tracking
- Bermuda location provider with 3D trilateration algorithm
- Provider-agnostic architecture for future location providers
- Moving entity coordinate calculation services
- Automatic Bermuda distance sensor discovery and mapping
- Least-squares trilateration for accurate 3D positioning

### Changed
- Refactored moving_entities config: moved from `providers.bermuda.nodes` to `beacon_nodes` hierarchy
- Renamed internal terminology from Bermuda-specific to generic beacon nodes

## [0.1.0] - 2025-12-06

### Added
- Initial release
- Floorplan configuration management
- Room and floor definitions with X/Y/Z coordinates
- Area association capability
- YAML-based configuration storage
- Config flow for Home Assistant integration setup
