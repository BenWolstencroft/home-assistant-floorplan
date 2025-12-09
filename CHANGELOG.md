# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.6] - 2025-12-09

### Added
- **Outlier distance filtering** to improve trilateration accuracy
- Automatically calculates maximum theoretical distance between beacon nodes
- Filters out distance measurements > 2x max beacon separation as outliers
- Prevents bad distance readings (interference, out-of-range) from skewing position calculations
- Logs which beacons are filtered and why

### Technical Details
- Example: If beacons are max 15m apart, any 30m+ distance reading is filtered
- Requires 3+ valid beacons after filtering to proceed with trilateration
- Significantly improves accuracy when some beacons have poor signal quality
- Prevents calculated positions from appearing outside floorplan bounds

## [0.3.5] - 2025-12-09

### Fixed
- **Trilateration numerical stability** - Added gradient clamping to prevent explosive coordinate values
- Gradients now clamped to ±10.0 to prevent runaway calculations that produced e+53 coordinates
- Added divergence detection that aborts if position exceeds 1000m from origin
- Prevents astronomical coordinate values that cause entities to render off-canvas

### Added
- **Enhanced trilateration debugging** with detailed convergence logging
- Shows starting centroid position and measured distances
- Logs convergence iteration, final position, and RMS error
- Warns when numerical instability detected with position and error details

## [0.3.4] - 2025-12-09

### Fixed
- **CRITICAL: Bermuda triangulation now works!** Fixed beacon node matching to use friendly names from device registry
- Triangulation now uses `get_all_beacon_node_data()` which enriches beacon nodes with friendly names
- Sensor names like `sensor.phone_distance_to_kitchen_bluetooth_proxy` now correctly match beacon nodes stored by MAC address
- Friendly names from device registry (e.g., "Kitchen Bluetooth Proxy") are normalized and matched against sensor suffixes
- Debug logs now show friendly names for each beacon node to verify matching

### Technical Details
- Beacon nodes stored as MAC addresses (e.g., `F8:B3:B7:21:B1:32`) in floorplan.yaml
- Device registry provides friendly names which get normalized for matching
- Bermuda sensor naming: `sensor.<device>_distance_to_<normalized_beacon_name>`
- Matching now works: `kitchen_bluetooth_proxy` ↔ "Kitchen Bluetooth Proxy" ↔ MAC address

## [0.3.3] - 2025-12-09

### Fixed
- **Config flow options** now properly updates integration configuration without 500 errors
- Options flow correctly transforms user input into nested provider configuration structure
- Config entry data properly updated using `async_update_entry()` method

### Added
- **Enhanced Bermuda triangulation debugging** with detailed sensor processing logs
- Shows each sensor being processed with distance values
- Logs node name extraction from sensor entity IDs
- Shows beacon node matching attempts and results
- Reports why triangulation fails (insufficient beacons, matching failures, etc.)
- Lists all available beacon nodes and matched beacons for troubleshooting

## [0.3.2] - 2025-12-09

### Changed
- **Logging philosophy refined**: Success operations now silent, warnings only for actionable failures
- Removed debug logs for successful beacon, floor, and room enrichment (previously fired on every service call)
- Floor enrichment now only logs warning when friendly name NOT found in registry
- Room enrichment now only logs warning when area name NOT found for rooms without explicit names
- Beacon enrichment now only logs warning when device name NOT found in device registry
- Service calls no longer log room counts or floor queries during normal operation

### Added
- **Debug logging for Bermuda triangulation troubleshooting** (temporary diagnostic logs)
- Service handler logs moving entity count and entity IDs when coordinates requested
- Bermuda provider logs sensor discovery, device grouping, triangulation attempts, and entity matching
- Detailed logging shows why moving entities may not appear (no sensors, triangulation failures, no matching entities)

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
