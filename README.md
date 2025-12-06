# Home Assistant Floorplan Integration

A Home Assistant integration for managing and storing 3D floorplans with room boundaries and floor levels.

## Features

- Define room boundaries as X/Y coordinates
- Manage multiple floors with Z height values
- Associate rooms with Home Assistant Areas
- Store configuration in YAML format in the custom component's data directory

## Installation

### Via HACS (Recommended)

1. Go to **HACS → Integrations**
2. Click "Explore & Download Repositories"
3. Search for "Floorplan"
4. Click "Download"
5. Restart Home Assistant
6. Go to **Settings → Devices & Services → Create Integration** and select "Floorplan"

### Manual Installation

1. Copy the `custom_components/floorplan` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Create Integration** and select "Floorplan"

## Configuration

### Setup

Once installed, configure your floorplan by creating a YAML file.

### Floorplan Configuration

Create a `floorplan/floorplan.yaml` file in your Home Assistant configuration directory to define your floorplan.

#### Example Configuration

```yaml
floors:
  ground_floor:
    name: Ground Floor
    z: 0
  first_floor:
    name: First Floor
    z: 3

rooms:
  living_room:
    name: Living Room
    floor: ground_floor
    area: living_room  # Optional: Home Assistant area ID
    boundaries:
      - x: 0
        y: 0
      - x: 10
        y: 0
      - x: 10
        y: 8
      - x: 0
        y: 8
  
  kitchen:
    name: Kitchen
    floor: ground_floor
    area: kitchen
    boundaries:
      - x: 10
        y: 0
      - x: 15
        y: 0
      - x: 15
        y: 5
      - x: 10
        y: 5
```

### Room Boundaries

Boundaries are defined as a list of coordinate points in clockwise or counter-clockwise order. Points define the polygon that represents the room:

```yaml
boundaries:
  - x: 0
    y: 0
  - x: 10
    y: 0
  - x: 10
    y: 8
  - x: 0
    y: 8
```

## Services

### `floorplan.get_rooms_by_floor`

Get all rooms on a specific floor.

**Service data:**
- `floor_id` (string): ID of the floor

**Returns:** List of rooms on the floor

### `floorplan.get_room`

Get a specific room by ID.

**Service data:**
- `room_id` (string): ID of the room

**Returns:** Room data

## Development

### Directory Structure

```
custom_components/floorplan/
  __init__.py              # Integration setup
  config_flow.py           # UI configuration
  const.py                 # Constants
  floorplan_manager.py     # Floorplan data management
  manifest.json            # Integration manifest
  translations/
    en.json               # English translations
```

## License

MIT
