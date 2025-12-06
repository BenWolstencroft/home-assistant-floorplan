# Home Assistant Floorplan Integration

A Home Assistant integration for managing and storing 3D floorplans with room boundaries and floor levels.

## Features

- Define room boundaries as X/Y coordinates
- Manage multiple floors with height values in meters
- Associate rooms with Home Assistant Areas
- Position any Home Assistant entity at specific 3D coordinates (lights, sensors, cameras, etc.)
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

### Integration Setup

1. Go to **Settings → Devices & Services**
2. Click **Create Integration**
3. Search for "Floorplan"
4. Enable/disable location providers as desired:
   - **Bermuda Location Provider**: Enable BLE-based trilateration for moving entity tracking (default: enabled)

### Provider Configuration

The integration supports pluggable location providers for tracking moving entities:

#### Bermuda Provider (Default)

Automatically enabled by default. To disable:

1. Go to **Settings → Devices & Services → Floorplan**
2. Click **Edit** on the Floorplan entry
3. Uncheck "Enable Bermuda Location Provider (BLE Trilateration)"
4. Save

Or configure via YAML (if using YAML configuration):

```yaml
# configuration.yaml
floorplan:
  providers:
    enable_bermuda: true  # Set to false to disable Bermuda provider
```

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

### Static Entities

You can position any Home Assistant entity in 3D space within your floorplan. This is useful for displaying sensors, lights, cameras, and other devices at their physical locations in your home.

Add a `static_entities` section to your configuration:

```yaml
static_entities:
  light.living_room:
    coordinates: [5, 4, 1.8]       # [X, Y, Z] in meters
  sensor.hallway_temperature:
    coordinates: [15, 2, 1.5]
  camera.front_door:
    coordinates: [0, 0, 2.2]
  light.bedroom_1:
    coordinates: [3, 8, 0.9]
```

- **Entity ID**: The full Home Assistant entity ID (e.g., `light.living_room`)
- **Coordinates**: `[X, Y, Z]` position in meters
  - `X`: Horizontal position (meters)
  - `Y`: Depth position (meters)
  - `Z`: Height above ground (meters)

### Moving Entities - Beacon Nodes

Beacon nodes are reference points (like BLE scanners) used to track the position of moving devices in your home through trilateration/triangulation.

Add a `moving_entities` section with `beacon_nodes`:

```yaml
moving_entities:
  beacon_nodes:
    # BLE scanner nodes - must be registered Bluetooth devices in Home Assistant
    # Find device IDs in Settings → Devices & Services → Bluetooth
    D4:5F:4E:A1:23:45:  # Device address or ID from Bluetooth registry
      coordinates: [12, 2.5, 2.0]     # [X, Y, Z] in meters
    A3:2B:1C:F9:87:56:
      coordinates: [5, 4, 2.0]
    F1:E2:D3:C4:B5:A6:
      coordinates: [4, 8, 2.0]
```

**Important:** Node IDs must match the Bluetooth device IDs registered in Home Assistant:
1. Go to **Settings → Devices & Services → Bluetooth**
2. Identify the BLE scanner devices you want to use for location tracking
3. Use their device IDs (MAC addresses or device identifiers) as node IDs
4. Position each scanner node at its physical location in your home

These node positions are used by location providers (like the Bermuda integration) to calculate the location of tracked devices (phones, tags, etc.) through BLE signal triangulation.

## Location Providers

### Bermuda Location Provider

The Bermuda location provider converts Bermuda's distance-to-beacon measurements into 3D coordinates using trilateration.

#### How It Works

Bermuda tracks devices by measuring the signal strength (RSSI) from each device to each BLE scanner node, then calculates the distance. The Floorplan integration uses these distances to perform 3D trilateration:

1. **Discovery**: Automatically finds all `distance_to_*` sensors created by Bermuda for tracked devices
2. **Matching**: Maps sensor names to beacon nodes in your floorplan configuration
3. **Triangulation**: Uses least-squares 3D trilateration to calculate the most likely position
4. **Coordinates**: Returns [X, Y, Z] coordinates that can be displayed on your Lovelace card

#### Requirements

- Bermuda integration installed and configured in Home Assistant
- At least 3 beacon nodes configured in the floorplan with valid coordinates
- Distance sensors from Bermuda must be available (not unknown/unavailable)

#### Configuration

No special configuration needed! Just:
1. Set up your beacon nodes as described above
2. Install and configure the Bermuda integration
3. Use the location provider services to get coordinates

#### Limitations

- Requires **at least 3 distance measurements** to triangulate (ideally 4+ for better accuracy)
- Accuracy depends on beacon node placement and Bermuda's distance accuracy
- Z-coordinate accuracy is limited - primarily useful for X/Y localization within a floor
- Devices must be in range of at least 3 beacons to calculate position

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

### `floorplan.get_static_entities`

Get all static entities with their coordinates.

**Returns:** Dictionary of entities with their [X, Y, Z] coordinates

### `floorplan.get_static_entity`

Get a specific static entity by entity ID.

**Service data:**
- `entity_id` (string): Home Assistant entity ID (e.g., `light.living_room`)

**Returns:** Entity coordinates [X, Y, Z] or null if not found

### `floorplan.add_static_entity`

Add a static entity at specified coordinates.

**Service data:**
- `entity_id` (string): Home Assistant entity ID
- `coordinates` (list): [X, Y, Z] coordinates in meters

### `floorplan.update_static_entity`

Update a static entity's coordinates.

**Service data:**
- `entity_id` (string): Home Assistant entity ID
- `coordinates` (list): [X, Y, Z] coordinates in meters

### `floorplan.delete_static_entity`

Delete a static entity from the floorplan.

**Service data:**
- `entity_id` (string): Home Assistant entity ID

### Beacon Node Services

#### `floorplan.add_beacon_node`

Register a beacon node (BLE scanner) at a specific location.

**Service data:**
- `node_id` (string): Bluetooth device ID from Home Assistant's Bluetooth registry (must be registered in Settings → Devices & Services → Bluetooth)
- `coordinates` (list): [X, Y, Z] coordinates in meters

**Note:** If the device ID is not registered as a Bluetooth device in Home Assistant, this service will fail with an error message.

#### `floorplan.get_beacon_nodes`

Get all registered beacon nodes and their coordinates.

**Returns:**
```json
{
  "nodes": {
    "D4:5F:4E:A1:23:45": [12, 2.5, 2.0],
    "A3:2B:1C:F9:87:56": [5, 4, 2.0],
    "F1:E2:D3:C4:B5:A6": [4, 8, 2.0]
  },
  "count": 3
}
```

#### `floorplan.update_beacon_node`

Update a beacon node's coordinates.

**Service data:**
- `node_id` (string): Bluetooth device ID (must be a registered device)
- `coordinates` (list): [X, Y, Z] coordinates in meters

#### `floorplan.delete_beacon_node`

Remove a beacon node from the configuration.

**Service data:**
- `node_id` (string): Bluetooth device ID (must be registered in Home Assistant)

### `floorplan.get_entity_coordinates`

Get the coordinates for a specific entity (useful for the Lovelace card).

**Service data:**
- `entity_id` (string): Home Assistant entity ID

**Returns:** 
```json
{
  "entity_id": "light.living_room",
  "coordinates": [5, 4, 1.8]
}
```

### `floorplan.get_all_entity_coordinates`

Get coordinates for all static entities at once (useful for the Lovelace card). Also includes beacon node locations.

**Returns:**
```json
{
  "entity_coordinates": {
    "light.living_room": [5, 4, 1.8],
    "sensor.hallway_temperature": [15, 2, 1.5],
    "camera.front_door": [0, 0, 2.2]
  },
  "count": 3,
  "beacon_nodes": {
    "D4:5F:4E:A1:23:45": [12, 2.5, 2.0],
    "A3:2B:1C:F9:87:56": [5, 4, 2.0],
    "F1:E2:D3:C4:B5:A6": [4, 8, 2.0]
  },
  "beacon_nodes_count": 3
}
```

### Moving Entity Services (Bermuda Provider)

#### `floorplan.get_moving_entity_coordinates`

Get calculated coordinates for a device tracked by Bermuda using trilateration.

**Service data:**
- `entity_id` (string): Home Assistant entity ID of the device being tracked

**Returns:**
```json
{
  "entity_id": "device_tracker.john_phone",
  "coordinates": [7.5, 3.2, 1.1]
}
```

Returns `null` for coordinates if:
- Device is not being tracked by Bermuda
- Not enough distance sensors are available (need 3+)
- Distance measurements are unknown/unavailable

#### `floorplan.get_all_moving_entity_coordinates`

Get calculated coordinates for all devices currently being tracked by Bermuda.

**Returns:**
```json
{
  "moving_entities": {
    "device_tracker.john_phone": [7.5, 3.2, 1.1],
    "device_tracker.jane_phone": [4.2, 5.8, 1.5],
    "person.dog": [2.1, 6.5, 0.9]
  },
  "count": 3
}
```

The count includes only devices with valid calculated coordinates.

## Using with the Lovelace Card

When developing the Lovelace card, you can retrieve entity coordinates using these services:

1. **`floorplan.get_all_entity_coordinates`** - Returns static entities and beacon nodes
2. **`floorplan.get_all_moving_entity_coordinates`** - Returns tracked devices (via Bermuda)

Combined response example:
```json
{
  "static": {
    "entity_coordinates": {
      "light.living_room": [5, 4, 1.8],
      "sensor.hallway_temperature": [15, 2, 1.5]
    },
    "beacon_nodes": {
      "D4:5F:4E:A1:23:45": [12, 2.5, 2.0],
      "A3:2B:1C:F9:87:56": [5, 4, 2.0]
    }
  },
  "moving": {
    "device_tracker.john_phone": [7.5, 3.2, 1.1],
    "device_tracker.jane_phone": [4.2, 5.8, 1.5],
    "person.dog": [2.1, 6.5, 0.9]
  }
}
```

The card can render:
- **Static entities** - Fixed UI elements (lights, cameras, sensors)
- **Beacon nodes** - Reference points showing localization infrastructure
- **Moving entities** - Tracked devices with dynamically calculated positions from Bermuda

## Development

### Directory Structure

```
custom_components/floorplan/
  __init__.py              # Integration setup, service handlers
  config_flow.py           # UI configuration
  const.py                 # Constants
  floorplan_manager.py     # Floorplan data management
  location_provider.py     # Location provider base class
  entity.py                # Entity helpers
  manifest.json            # Integration manifest
  providers/
    __init__.py            # Providers module
    bermuda.py             # Bermuda trilateration provider
  translations/
    en.json               # English translations
```

## License

MIT
