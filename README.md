# Home Assistant Floorplan Integration

A flexible 3D floorplan system for Home Assistant with room management, entity positioning, and location tracking via Bermuda BLE trilateration.

## Quick Start

### Installation

1. **Via HACS** (recommended):
   - Go to HACS → Integrations
   - Search for "Floorplan"
   - Install and restart Home Assistant

2. **Manual**:
   - Copy `custom_components/floorplan` to your custom_components folder
   - Restart Home Assistant

### Setup

1. Go to **Settings → Devices & Services → Create Integration**
2. Search for and select "Floorplan"
3. Choose whether to enable Bermuda location provider
4. Done! Now configure your floorplan in YAML

### Basic Configuration

Create `floorplan/floorplan.yaml` in your Home Assistant configuration directory (see `floorplan.yaml.example` for a complete example):

> **Auto-reload enabled**: The integration automatically watches for changes to `floorplan.yaml` and reloads every 2 seconds. You can also manually reload using the `floorplan.reload` service.

```yaml
floors:
  ground_floor:
    height: 0
  1st_floor:
    height: 3.2

rooms:
  living_room:
    name: Living Room
    floor: ground_floor
    area: living_room
    boundaries:
      - [0, 0]
      - [10, 0]
      - [10, 8]
      - [0, 8]

static_entities:
  light.living_room:
    coordinates: [5, 4, 1.8]
  camera.front_door:
    coordinates: [0, 0, 2.2]

moving_entities:
  beacon_nodes:
    "D4:5F:4E:A1:23:45":
      coordinates: [12, 2.5, 2.0]
    "A3:2B:1C:F9:87:56":
      coordinates: [5, 4, 2.0]
```

**Coordinate Format**: `[X, Y, Z]` all in meters
- **X/Y**: Horizontal position in your home
- **Z**: Height above ground

## Features

- 📐 **Room Management** - Define room boundaries with 3D coordinates
- 🏠 **Multi-Floor Support** - Manage multiple floors with different heights
- 📍 **Entity Positioning** - Position any Home Assistant entity in 3D space
- 📡 **Location Tracking** - Track moving entities using Bermuda BLE trilateration
- 🎨 **Lovelace Card** - Render your floorplan as an interactive 2D view

## Documentation

- **[📖 Installation & Configuration](./docs/INSTALLATION.md)** - Detailed setup and YAML reference
- **[🔌 Services Reference](./docs/SERVICES.md)** - Complete list of available services
- **[🧠 Architecture & Design](./docs/ARCHITECTURE.md)** - How the system works internally
- **[📡 Location Providers](./docs/PROVIDERS.md)** - Bermuda and future providers

## Lovelace Card

Display your floorplan on the dashboard:

1. Install via HACS → Frontend → search "Floorplan Card"
2. Add to your dashboard:

```yaml
type: custom:floorplan-card
floor_id: ground_floor
title: My Floorplan
```

See [home-assistant-floorplan-card](../home-assistant-floorplan-card/) for details.

## Support

- 🐛 [Report Issues](https://github.com/BenWolstencroft/home-assistant-floorplan/issues)
- 💬 [Join Discussions](https://github.com/BenWolstencroft/home-assistant-floorplan/discussions)
- 📚 [View Docs](./docs/)

## License

MIT
