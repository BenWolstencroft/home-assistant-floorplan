# Services Reference

Complete documentation of all available Floorplan integration services.

## Overview

The Floorplan integration provides 20+ services for managing your floorplan data and retrieving entity coordinates for visualization and automation.

Services are organized by category:
- **Room Management** - Query room data
- **Entity Positioning** - Manage static entity coordinates
- **Beacon Node Management** - Register and manage BLE scanner nodes
- **Coordinates Retrieval** - Get entity positions for the Lovelace card
- **Location Tracking** - Get moving entity positions (Bermuda provider)

## Room Management Services

### `floorplan.get_rooms_by_floor`

Get all rooms on a specific floor.

**Service Data:**
```yaml
service: floorplan.get_rooms_by_floor
data:
  floor_id: ground_floor
```

**Parameters:**
- `floor_id` (string, **required**): ID of the floor

**Response:**
```json
{
  "rooms": [
    {
      "id": "living_room",
      "name": "Living Room",
      "floor": "ground_floor",
      "area": "living_room",
      "boundaries": [[0, 0], [10, 0], [10, 8], [0, 8]]
    },
    {
      "id": "kitchen",
      "name": "Kitchen",
      "floor": "ground_floor",
      "area": "kitchen",
      "boundaries": [[10, 0], [15, 0], [15, 5], [10, 5]]
    }
  ],
  "count": 2
}
```

### `floorplan.get_room`

Get a specific room by ID.

**Service Data:**
```yaml
service: floorplan.get_room
data:
  room_id: living_room
```

**Parameters:**
- `room_id` (string, **required**): ID of the room

**Response:**
```json
{
  "id": "living_room",
  "name": "Living Room",
  "floor": "ground_floor",
  "area": "living_room",
  "boundaries": [[0, 0], [10, 0], [10, 8], [0, 8]]
}
```

### `floorplan.get_all_rooms`

Get all rooms across all floors.

**Service Data:**
```yaml
service: floorplan.get_all_rooms
```

**Response:**
```json
{
  "rooms": [
    {
      "id": "living_room",
      "name": "Living Room",
      "floor": "ground_floor",
      "boundaries": [[0, 0], [10, 0], [10, 8], [0, 8]]
    },
    {
      "id": "kitchen",
      "name": "Kitchen",
      "floor": "ground_floor",
      "boundaries": [[10, 0], [15, 0], [15, 5], [10, 5]]
    },
    {
      "id": "master_bedroom",
      "name": "Master Bedroom",
      "floor": "1st_floor",
      "boundaries": [[0, 0], [8, 0], [8, 10], [0, 10]]
    }
  ],
  "count": 3
}
```

## Static Entity Services

### `floorplan.get_static_entities`

Get all static entities with their coordinates.

**Service Data:**
```yaml
service: floorplan.get_static_entities
```

**Response:**
```json
{
  "entity_coordinates": {
    "light.living_room": [5, 4, 1.8],
    "sensor.hallway_temperature": [15, 2, 1.5],
    "camera.front_door": [0, 0, 2.2],
    "light.bedroom_1": [3, 8, 0.9]
  },
  "count": 4
}
```

### `floorplan.get_static_entity`

Get coordinates for a specific static entity.

**Service Data:**
```yaml
service: floorplan.get_static_entity
data:
  entity_id: light.living_room
```

**Parameters:**
- `entity_id` (string, **required**): Home Assistant entity ID

**Response:**
```json
{
  "entity_id": "light.living_room",
  "coordinates": [5, 4, 1.8]
}
```

Returns `null` for coordinates if entity is not in static entities list.

### `floorplan.add_static_entity`

Add a new static entity at specified coordinates.

**Service Data:**
```yaml
service: floorplan.add_static_entity
data:
  entity_id: light.new_fixture
  coordinates: [7.5, 5.2, 1.8]
```

**Parameters:**
- `entity_id` (string, **required**): Home Assistant entity ID
- `coordinates` (list, **required**): [X, Y, Z] in meters

**Response:**
```json
{
  "success": true,
  "entity_id": "light.new_fixture",
  "coordinates": [7.5, 5.2, 1.8]
}
```

**Error Cases:**
- Entity ID already exists (update instead)
- Invalid coordinate values

### `floorplan.update_static_entity`

Update an existing static entity's coordinates.

**Service Data:**
```yaml
service: floorplan.update_static_entity
data:
  entity_id: light.living_room
  coordinates: [5.5, 4.2, 1.9]
```

**Parameters:**
- `entity_id` (string, **required**): Home Assistant entity ID
- `coordinates` (list, **required**): [X, Y, Z] in meters

**Response:**
```json
{
  "success": true,
  "entity_id": "light.living_room",
  "old_coordinates": [5, 4, 1.8],
  "new_coordinates": [5.5, 4.2, 1.9]
}
```

### `floorplan.delete_static_entity`

Remove a static entity from the floorplan.

**Service Data:**
```yaml
service: floorplan.delete_static_entity
data:
  entity_id: light.living_room
```

**Parameters:**
- `entity_id` (string, **required**): Home Assistant entity ID

**Response:**
```json
{
  "success": true,
  "entity_id": "light.living_room",
  "coordinates": [5, 4, 1.8]
}
```

## Beacon Node Services

Beacon nodes are BLE scanner reference points used for trilateration. All node IDs must be registered Bluetooth devices in Home Assistant.

### `floorplan.add_beacon_node`

Register a new beacon node at a location.

**Service Data:**
```yaml
service: floorplan.add_beacon_node
data:
  node_id: D4:5F:4E:A1:23:45:
  coordinates: [12, 2.5, 2.0]
```

**Parameters:**
- `node_id` (string, **required**): Bluetooth device ID (from Settings → Devices & Services → Bluetooth)
- `coordinates` (list, **required**): [X, Y, Z] in meters

**Response:**
```json
{
  "success": true,
  "node_id": "D4:5F:4E:A1:23:45:",
  "coordinates": [12, 2.5, 2.0]
}
```

**Error Cases:**
- Node ID not registered in Bluetooth registry
- Device ID already exists (use update)
- Invalid coordinates

### `floorplan.get_beacon_nodes`

Get all registered beacon nodes and their coordinates.

**Service Data:**
```yaml
service: floorplan.get_beacon_nodes
```

**Response:**
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

### `floorplan.update_beacon_node`

Update a beacon node's coordinates.

**Service Data:**
```yaml
service: floorplan.update_beacon_node
data:
  node_id: D4:5F:4E:A1:23:45:
  coordinates: [12.5, 2.3, 2.0]
```

**Parameters:**
- `node_id` (string, **required**): Bluetooth device ID
- `coordinates` (list, **required**): [X, Y, Z] in meters

**Response:**
```json
{
  "success": true,
  "node_id": "D4:5F:4E:A1:23:45:",
  "old_coordinates": [12, 2.5, 2.0],
  "new_coordinates": [12.5, 2.3, 2.0]
}
```

### `floorplan.delete_beacon_node`

Remove a beacon node from the floorplan.

**Service Data:**
```yaml
service: floorplan.delete_beacon_node
data:
  node_id: D4:5F:4E:A1:23:45:
```

**Parameters:**
- `node_id` (string, **required**): Bluetooth device ID

**Response:**
```json
{
  "success": true,
  "node_id": "D4:5F:4E:A1:23:45:",
  "coordinates": [12, 2.5, 2.0]
}
```

## Coordinates Retrieval Services

These services are primarily used by the Lovelace card to render entity positions.

### `floorplan.get_entity_coordinates`

Get coordinates for a single entity (static or moving).

**Service Data:**
```yaml
service: floorplan.get_entity_coordinates
data:
  entity_id: light.living_room
```

**Parameters:**
- `entity_id` (string, **required**): Home Assistant entity ID

**Response (Static Entity):**
```json
{
  "entity_id": "light.living_room",
  "coordinates": [5, 4, 1.8],
  "type": "static"
}
```

**Response (Moving Entity):**
```json
{
  "entity_id": "device_tracker.phone",
  "coordinates": [7.5, 3.2, 1.1],
  "type": "moving"
}
```

**Response (Not Found):**
```json
{
  "entity_id": "light.unknown",
  "coordinates": null,
  "type": "unknown"
}
```

### `floorplan.get_all_entity_coordinates`

Get all static entities and beacon nodes (snapshot for visualization).

**Service Data:**
```yaml
service: floorplan.get_all_entity_coordinates
```

**Response:**
```json
{
  "static_entities": {
    "entity_coordinates": {
      "light.living_room": [5, 4, 1.8],
      "sensor.hallway_temperature": [15, 2, 1.5],
      "camera.front_door": [0, 0, 2.2]
    },
    "entity_count": 3
  },
  "beacon_nodes": {
    "D4:5F:4E:A1:23:45": [12, 2.5, 2.0],
    "A3:2B:1C:F9:87:56": [5, 4, 2.0],
    "F1:E2:D3:C4:B5:A6": [4, 8, 2.0]
  },
  "beacon_count": 3
}
```

## Moving Entity Services (Bermuda Provider)

Available only when Bermuda location provider is enabled.

### `floorplan.get_moving_entity_coordinates`

Get calculated coordinates for a device tracked by Bermuda.

**Service Data:**
```yaml
service: floorplan.get_moving_entity_coordinates
data:
  entity_id: device_tracker.john_phone
```

**Parameters:**
- `entity_id` (string, **required**): Home Assistant entity ID of tracked device

**Response (Success):**
```json
{
  "entity_id": "device_tracker.john_phone",
  "coordinates": [7.5, 3.2, 1.1],
  "confidence": 0.85,
  "last_updated": "2024-01-15T10:30:42.123456+00:00"
}
```

**Response (Not Tracked):**
```json
{
  "entity_id": "device_tracker.john_phone",
  "coordinates": null,
  "error": "Device not tracked by Bermuda"
}
```

**Response (Insufficient Data):**
```json
{
  "entity_id": "device_tracker.john_phone",
  "coordinates": null,
  "error": "Insufficient distance measurements (need 3+)"
}
```

**Error Cases:**
- Device not tracked by Bermuda
- Less than 3 distance sensors available
- Distance measurements unknown or unavailable
- Bermuda provider not enabled

### `floorplan.get_all_moving_entity_coordinates`

Get calculated coordinates for all devices tracked by Bermuda.

**Service Data:**
```yaml
service: floorplan.get_all_moving_entity_coordinates
```

**Response:**
```json
{
  "moving_entities": {
    "device_tracker.john_phone": {
      "coordinates": [7.5, 3.2, 1.1],
      "confidence": 0.85,
      "last_updated": "2024-01-15T10:30:42.123456+00:00"
    },
    "device_tracker.jane_phone": {
      "coordinates": [4.2, 5.8, 1.5],
      "confidence": 0.92,
      "last_updated": "2024-01-15T10:30:41.654321+00:00"
    },
    "person.dog": {
      "coordinates": [2.1, 6.5, 0.9],
      "confidence": 0.78,
      "last_updated": "2024-01-15T10:30:40.987654+00:00"
    }
  },
  "count": 3,
  "timestamp": "2024-01-15T10:30:42.987654+00:00"
}
```

Only devices with valid calculated coordinates are included in the response.

## Lovelace Card Integration

The Lovelace card uses these services to retrieve entity positions:

**Typical Card Flow:**
1. Call `floorplan.get_all_entity_coordinates` for static entities and beacon nodes
2. Call `floorplan.get_all_moving_entity_coordinates` for moving entities
3. Render static entities as fixed UI elements
4. Render beacon nodes as reference points
5. Render moving entities with updated positions

**Example Automation Using Services:**

```yaml
automation:
  - alias: Display entity on load
    trigger:
      platform: homeassistant
      event: start
    action:
      - service: floorplan.get_all_entity_coordinates
        response_variable: floorplan_data
      - service: notify.notify
        data:
          message: "Floorplan loaded with {{ floorplan_data.static_entities.entity_count }} entities"
```

## Service Error Handling

All services return appropriate error codes and messages:

**Common Error Responses:**

```json
{
  "success": false,
  "error": "Entity ID required",
  "error_code": "MISSING_PARAMETER"
}
```

```json
{
  "success": false,
  "error": "Device D4:5F:4E:A1:23:45 not registered in Bluetooth registry",
  "error_code": "INVALID_DEVICE_ID"
}
```

```json
{
  "success": false,
  "error": "Entity light.unknown not found",
  "error_code": "NOT_FOUND"
}
```

## Performance Considerations

- **`get_all_entity_coordinates`**: Fast, returns cached data
- **`get_all_moving_entity_coordinates`**: Performs calculations, slightly slower
- **Trilateration**: Runs on demand, 3D least-squares algorithm
- **Caching**: Static entities cached, moving entities calculated on each call

For real-time applications, call `get_all_moving_entity_coordinates` at regular intervals (typically 1-5 seconds).

## Development

For custom implementations using these services, refer to:
- [Architecture & Design](./ARCHITECTURE.md) - Internal data structures
- [Location Providers](./PROVIDERS.md) - How coordinates are calculated
