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

**Note:** Floor IDs are automatically synced from Home Assistant's floor registry. You reference floors by their Home Assistant floor ID.

#### Example Configuration

```yaml
floors:
  ground_floor:
    height: 0          # Height in meters (ground reference)
  1st_floor:
    height: 3.2        # Height in meters above ground
  basement:
    height: -2.5       # Height in meters below ground

rooms:
  # Ground Floor Rooms
  living_room:
    name: Living Room
    floor: ground_floor  # Home Assistant floor ID
    area: living_room    # Optional: Home Assistant area ID
    boundaries:
      - [0, 0]
      - [10, 0]
      - [10, 8]
      - [0, 8]
  
  kitchen:
    name: Kitchen
    floor: ground_floor
    area: kitchen
    boundaries:
      - [10, 0]
      - [15, 0]
      - [15, 5]
      - [10, 5]

  # First Floor Rooms
  master_bedroom:
    name: Master Bedroom
    floor: 1st_floor     # Home Assistant floor ID
    area: master_bedroom
    boundaries:
      - [0, 0]
      - [8, 0]
      - [8, 10]
      - [0, 10]
  
  bathroom:
    name: Bathroom
    floor: 1st_floor
    area: bathroom
    boundaries:
      - [8, 0]
      - [10, 0]
      - [10, 5]
      - [8, 5]
```

### Room Boundaries and Coordinates

All coordinates and dimensions in the floorplan configuration are in **meters**.

Boundaries are defined as a list of coordinate points in clockwise or counter-clockwise order. Points define the polygon that represents the room. Each point is an array of `[X, Y]` coordinates in meters:

```yaml
boundaries:
  - [0, 0]       # 0m x 0m
  - [10, 0]      # 10m x 0m
  - [10, 8]      # 10m x 8m
  - [0, 8]       # 0m x 8m
```

### Floor Heights

Each floor has a physical height in meters stored in the floorplan configuration. This represents the Z-axis elevation of that floor:

- **`height`** (float): Height in meters above/below ground reference
  - Ground floor: `0` (reference level)
  - First floor: `3.2` (3.2 meters above ground)
  - Basement: `-2.5` (2.5 meters below ground)

**To define floor heights:**
1. Edit `floorplan/floorplan.yaml` in your Home Assistant configuration directory
2. Add a `floors` section with each floor ID and its `height` value
3. Restart Home Assistant or reload the floorplan integration

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
