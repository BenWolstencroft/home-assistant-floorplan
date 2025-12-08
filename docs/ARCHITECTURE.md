# Architecture & Design

Technical overview of the Home Assistant Floorplan integration architecture.

## System Architecture

### High-Level Overview

```
Home Assistant Core
│
├─ Floorplan Integration
│  ├─ Config Flow (UI Configuration)
│  ├─ Service Handler (20+ services)
│  ├─ Floorplan Manager (Data persistence)
│  │  ├─ Floors Registry
│  │  ├─ Rooms Registry
│  │  ├─ Static Entities Registry
│  │  └─ Beacon Nodes Registry
│  │
│  ├─ Location Provider System
│  │  ├─ Provider Base Class
│  │  ├─ Bermuda Provider (Trilateration)
│  │  └─ Provider Registry
│  │
│  └─ Services API
│
└─ Lovelace Card
   ├─ Calls floorplan.* services
   ├─ Receives entity coordinates
   └─ Renders 2D floorplan visualization
```

### Component Responsibilities

| Component | Responsibility | Language |
|-----------|-----------------|----------|
| `__init__.py` | Integration setup, service registration, provider lifecycle | Python |
| `config_flow.py` | UI configuration wizard, provider selection | Python |
| `floorplan_manager.py` | YAML file I/O, data persistence, registry management | Python |
| `location_provider.py` | Abstract base class for providers | Python |
| `providers/bermuda.py` | BLE trilateration calculations | Python |
| `const.py` | Constants, configuration keys | Python |
| Lovelace Card | Visualization, service calls | TypeScript/Lit |

## Data Model

### Floorplan Structure

```yaml
Floorplan (root)
├─ Floors
│  ├─ floor_id
│  │  ├─ height: float (meters)
│  │  └─ ...
│  └─ ...
│
├─ Rooms
│  ├─ room_id
│  │  ├─ name: string
│  │  ├─ floor: floor_id reference
│  │  ├─ area: area_id reference (optional)
│  │  └─ boundaries: [[x, y], ...]
│  └─ ...
│
├─ Static Entities
│  ├─ entity_id
│  │  └─ coordinates: [x, y, z]
│  └─ ...
│
└─ Moving Entities
   ├─ Beacon Nodes
   │  ├─ node_id
   │  │  └─ coordinates: [x, y, z]
   │  └─ ...
   └─ ...
```

### Coordinate System

**3D Cartesian Coordinates:**
- **X**: Horizontal left/right (meters, positive right)
- **Y**: Horizontal forward/back (meters, positive forward)
- **Z**: Vertical up/down (meters, positive up)

**Origin Convention:**
- Typically placed at corner of home
- All coordinates relative to this origin
- Floor height defines **ceiling height** of that floor (used for beacon/entity filtering by floor)

**Examples:**
```yaml
light.living_room: [5, 4, 1.8]
# 5m right, 4m forward, 1.8m up (typical ceiling light height)

camera.front_door: [0, 0, 2.2]
# At origin corner, 2.2m high (porch overhang)

beacon_node_1: [12, 2.5, 2.0]
# 12m right, 2.5m forward, 2.0m up (wall-mounted)
```

## Data Persistence

### File-Based Storage

```
~/.homeassistant/
└─ floorplan/
   └─ floorplan.yaml          # User-edited configuration
```

**Format**: YAML with sections for floors, rooms, static entities, moving entities

**Lifecycle:**
1. User creates/edits `floorplan.yaml`
2. Integration loads on startup or reload
3. Floorplan Manager parses YAML → in-memory registries
4. Services query registries
5. User updates → restart to reload (or hot-reload planned)

### In-Memory Registries

```python
# Floorplan Manager
floors: dict[str, FloorData]              # floor_id → floor data
rooms: dict[str, RoomData]                # room_id → room data
static_entities: dict[str, list[float]]   # entity_id → [x, y, z]
beacon_nodes: dict[str, list[float]]      # node_id → [x, y, z]
```

All registries loaded from YAML on initialization.

## Service Architecture

### Service Registration

Services registered during integration setup (`async_setup`):

```python
async def async_setup(hass, config):
    # Register all services
    hass.services.async_register(
        DOMAIN,
        "get_rooms_by_floor",
        handle_get_rooms_by_floor,
        ...
    )
    # ... more services
```

### Service Handler Pattern

```python
async def handle_service_call(hass, service_call):
    """Handle service call."""
    # 1. Extract data
    data = service_call.data
    
    # 2. Validate
    if not data.get("entity_id"):
        raise ServiceValidationError("entity_id required")
    
    # 3. Execute business logic
    result = manager.get_static_entity(data["entity_id"])
    
    # 4. Return response
    return {
        "entity_id": data["entity_id"],
        "coordinates": result
    }
```

### Service Categories

#### Query Services (Read-Only)
- `get_rooms_by_floor`
- `get_room`
- `get_static_entities`
- `get_entity_coordinates`
- `get_beacon_nodes`

**Characteristics:**
- No state changes
- Fast execution
- Queryable any time

#### Modification Services (Stateful)
- `add_static_entity`
- `update_static_entity`
- `delete_static_entity`
- `add_beacon_node`
- `update_beacon_node`
- `delete_beacon_node`

**Characteristics:**
- Modify registries
- May save to YAML (planned)
- Require validation

#### Location Services (Provider-Dependent)
- `get_moving_entity_coordinates`
- `get_all_moving_entity_coordinates`

**Characteristics:**
- Delegate to active provider
- Dynamic calculation
- Real-time data

## Location Provider System

### Provider Abstraction

```python
class LocationProvider:
    """Base class for location providers."""
    
    async def init(self, hass, config) -> bool:
        """Initialize provider. Return True if ready."""
    
    async def get_moving_entity_coordinates(
        self, entity_id: str
    ) -> Optional[tuple[float, float, float]]:
        """Get [X, Y, Z] for entity or None."""
    
    async def get_all_moving_entities(
        self
    ) -> dict[str, tuple[float, float, float]]:
        """Get all tracked entities."""
    
    async def shutdown(self) -> None:
        """Cleanup on disable."""
```

### Bermuda Provider Implementation

```python
class BermudaProvider(LocationProvider):
    """BLE trilateration via Bermuda integration."""
    
    def __init__(self, hass, manager, config):
        self.hass = hass
        self.manager = manager        # Access beacon nodes
        self.config = config
    
    async def init(self):
        # Check if Bermuda available
        # Setup listeners
        # Verify beacon nodes >= 3
        return True
    
    async def get_moving_entity_coordinates(self, entity_id):
        # Get distance_to_* sensors from Bermuda
        # Extract distances from state
        # Perform trilateration
        # Return [x, y, z]
```

### Provider Lifecycle

```
Integration Startup
    ↓
Read provider config (bermuda.enabled: true)
    ↓
Instantiate active providers
    ↓
Call provider.init() for each
    ↓
Providers ready → services available
    ↓
Service calls delegate to providers
    ↓
Integration Shutdown
    ↓
Call provider.shutdown() for cleanup
```

### Provider Discovery

```python
# Load enabled providers from configuration
ACTIVE_PROVIDERS = {}

providers_config = config.get("providers", {})
bermuda_config = providers_config.get("bermuda", {})
if bermuda_config.get("enabled", True):
    provider = BermudaProvider(hass, manager, config)
    if await provider.init(hass):
        ACTIVE_PROVIDERS["bermuda"] = provider
```

## Trilateration Algorithm

### Mathematical Foundation

Given:
- N beacon nodes at positions: $P_i = (x_i, y_i, z_i)$
- Measured distances: $d_i$

Find: Position $P = (x, y, z)$ minimizing:

$$E = \sum_{i=1}^{n} (||P - P_i|| - d_i)^2$$

### Implementation

```python
def trilaterate(beacon_positions, distances):
    """
    Calculate position from beacon positions and distances.
    
    Args:
        beacon_positions: list of [x, y, z] coordinates
        distances: list of distances to each beacon
    
    Returns:
        [x, y, z] position or None if failed
    """
    # Setup least-squares problem
    # Use Levenberg-Marquardt algorithm
    # Iterate until convergence
    # Return best fit position
```

### Convergence Criteria

- Maximum iterations: 100
- Tolerance: 1e-6 meters
- Typical convergence: 5-10 iterations

### Accuracy Factors

| Factor | Impact | Improvement |
|--------|--------|-------------|
| Number of beacons | >3 minimum, 4+ better | Add more beacons |
| Beacon geometry | Linear (bad) → triangular (good) | Optimize placement |
| Distance accuracy | RSSI variance | Stable environment |
| Z-coordinate | Limited by geometry | Use with caution |

## Configuration Flow

### UI Configuration (First Run)

```
User installs integration
    ↓
Settings → Devices & Services → Create Integration
    ↓
Config Flow Step 1: Provider Selection
    Checkbox: "Enable Bermuda Location Provider"
    [Submit]
    ↓
Config saved to Home Assistant
```

### YAML Configuration (Floorplan)

```
User creates floorplan/floorplan.yaml
    ↓
Integration loads on startup
    ↓
Floorplan Manager parses YAML
    ↓
Registries populated
    ↓
Services available
```

### Configuration Precedence

1. YAML `floorplan/floorplan.yaml` (primary)
2. Integration config (provider enable/disable)
3. Default values (if missing)

## Integration Lifecycle

### Startup

```python
async def async_setup(hass, config):
    # 1. Create coordinator/manager
    manager = FloorplanManager(hass)
    
    # 2. Load configuration
    loaded = await manager.async_load_config()
    
    # 3. Initialize providers
    providers = await init_providers(hass, manager, config)
    
    # 4. Register services
    register_services(hass, manager, providers)
    
    # 5. Store for later access
    hass.data[DOMAIN] = {
        "manager": manager,
        "providers": providers
    }
    
    return True
```

### Configuration Update

```
User edits configuration.yaml
    ↓
Settings → Developer Tools → YAML → Reload Floorplan
    ↓
Integration reloads
    ↓
New configuration applied
```

### Shutdown

```python
async def async_unload_platform(hass, platform):
    # 1. Shutdown providers
    for provider in providers.values():
        await provider.shutdown()
    
    # 2. Unregister services
    # (automatic by Home Assistant)
    
    # 3. Cleanup
    del hass.data[DOMAIN]
    
    return True
```

## Error Handling

### Configuration Validation

```yaml
# YAML validation
- Floors section: required, at least 1
- Rooms: optional, required fields: name, floor, boundaries
- Static entities: optional, required fields: coordinates
- Beacon nodes: optional, required fields: coordinates
```

### Runtime Validation

```python
# Service call validation
- entity_id: must exist in Home Assistant (optional check)
- coordinates: must be [float, float, float]
- node_id: must be registered in Bluetooth registry
```

### Error Response Pattern

```json
{
  "success": false,
  "error": "Device ID not registered",
  "error_code": "INVALID_DEVICE_ID"
}
```

## Performance Characteristics

### Operation Complexity

| Operation | Complexity | Typical Time |
|-----------|-----------|--------------|
| Get room by ID | O(1) | <1ms |
| Get all rooms | O(n) | 1-5ms |
| Get static entity | O(1) | <1ms |
| Get all entities | O(m) | 1-10ms |
| Trilaterate position | O(k²) | 5-50ms |
| Get all moving entities | O(m×k²) | 50-500ms |

- n = number of rooms
- m = number of moving entities
- k = number of beacons (iterations)

### Memory Usage

```
Static data:
  - Floors: ~100 bytes each
  - Rooms: ~500 bytes each (including boundaries)
  - Static entities: ~50 bytes each
  - Beacon nodes: ~50 bytes each

Total for typical home:
  - 4 floors, 15 rooms, 30 entities, 4 beacons
  - ~25 KB total
```

### Scalability

- Tested with: 50 rooms, 100 entities, 20 beacons, 10 moving devices
- Performance: Linear with entity count
- Bottleneck: Trilateration calculation (scales with devices × beacons)

## Extension Points

### Adding a New Location Provider

1. **Create Provider Class**
   ```python
   class ESPresenseProvider(LocationProvider):
       async def init(self, hass, config):
           # Initialize
       
       async def get_moving_entity_coordinates(self, entity_id):
           # Calculate position
   ```

2. **Register Provider**
   ```python
   if config.get("enable_espresense"):
       provider = ESPresenseProvider(...)
       await provider.init(hass)
   ```

3. **Add UI Option**
   - Update `config_flow.py` with new toggle
   - Add translation

### Adding New Services

1. **Implement Handler**
   ```python
   async def handle_custom_service(hass, call):
       # Logic here
       return result
   ```

2. **Register Service**
   ```python
   hass.services.async_register(
       DOMAIN,
       "custom_service",
       handle_custom_service,
       schema=vol.Schema({...})
   )
   ```

## Testing Strategy

### Unit Tests
- Config parsing
- Trilateration calculations
- Registry operations

### Integration Tests
- Service calls
- Provider initialization
- Data persistence

### E2E Tests
- Full workflow: setup → config → service calls
- Lovelace card interaction

## Security Considerations

### Configuration Privacy
- No sensitive data stored (positions are relative)
- Local-only by default
- Can be exposed via public integrations

### Service Access Control
- Services callable by any user with permission
- No built-in access control
- Relies on Home Assistant service call permissions

### Data Validation
- Validate all service inputs
- Prevent injection attacks
- Sanitize device IDs

## Future Improvements

1. **Hot Reload**: Update floorplan without restart
2. **Multiple Providers**: Run Bermuda + ESPresense simultaneously
3. **Advanced Confidence**: Return confidence scores
4. **Geofencing**: Determine which room entity is in
5. **Web UI**: Visual floorplan editor
