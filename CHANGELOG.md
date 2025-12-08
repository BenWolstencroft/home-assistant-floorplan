# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
