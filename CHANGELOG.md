# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Provider configuration UI in config_flow
- Ability to enable/disable Bermuda location provider
- Config translations for provider settings

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
