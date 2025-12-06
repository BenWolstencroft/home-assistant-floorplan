# Location Providers

Technical documentation for location providers in the Floorplan integration.

## Overview

Location providers are pluggable modules that calculate the position of moving entities (like phones or tags) in your home. Currently, **Bermuda** is the primary provider for BLE-based trilateration.

## Bermuda Location Provider

The Bermuda provider uses BLE signal strength and trilateration to track moving devices in 3D space.

### How It Works

#### 1. Distance Measurement (Bermuda Integration)

The Bermuda integration measures BLE signal strength (RSSI - Received Signal Strength Indicator) from each scanner to each device:

```
Device (Phone) sends BLE advertisement
    ↓
Scanner 1 receives with -65 dBm RSSI
Scanner 2 receives with -72 dBm RSSI
Scanner 3 receives with -78 dBm RSSI
    ↓
Bermuda converts RSSI to distance using path loss model:
    distance = 10^((RSSI - TX_Power) / (-20 * log10(frequency)))
    ↓
Creates distance_to_* sensors with distance values
```

#### 2. Trilateration (Floorplan Integration)

The Floorplan integration takes these distance measurements and calculates 3D coordinates:

```
Scanner 1 at (12, 2.5, 2.0) → distance: 4.2m
Scanner 2 at (5, 4, 2.0) → distance: 2.1m
Scanner 3 at (4, 8, 2.0) → distance: 5.8m
    ↓
Least-Squares Trilateration Algorithm:
    Find point (X, Y, Z) that minimizes:
    Σ[(distance_to_scanner_i - calculated_distance)²]
    ↓
Returns: [7.5, 3.2, 1.1]  (device coordinates)
```

#### 3. Data Flow

```
Home Assistant
├─ Bermuda Integration
│  ├─ BLE Scanner Devices (Bluetooth integration)
│  ├─ Tracked Devices (imported by user)
│  └─ distance_to_* Sensors
│
└─ Floorplan Integration
   ├─ Reads distance_to_* sensors from Bermuda
   ├─ Maps to beacon nodes
   ├─ Performs trilateration
   └─ Returns coordinates → Lovelace Card
```

### Requirements

1. **Bermuda Integration**
   - Installation via HACS or manual
   - Configured with BLE scanners
   - Devices imported for tracking

2. **Home Assistant Bluetooth**
   - BLE scanner devices registered
   - Named or identified by MAC address

3. **Floorplan Configuration**
   - At least 3 beacon nodes configured
   - Beacon nodes positioned in 3D space
   - Beacon node IDs match Bluetooth registry

### Algorithm Details

#### Least-Squares Trilateration

Given:
- N beacon nodes at positions: P₁ = (x₁, y₁, z₁), ..., Pₙ = (xₙ, yₙ, zₙ)
- Distances to each beacon: d₁, d₂, ..., dₙ

Find position P = (x, y, z) that minimizes:

$$\text{Error} = \sum_{i=1}^{n} \left( \sqrt{(x - x_i)^2 + (y - y_i)^2 + (z - z_i)^2} - d_i \right)^2$$

**Solution Method:**
- Iterative Levenberg-Marquardt algorithm
- Starts from centroid of beacon nodes
- Converges to local minimum
- Typical convergence in 5-10 iterations

**Accuracy Factors:**
- Number of beacons (3+ minimum, 4+ recommended)
- Beacon geometry (spread-out triangle/square better than linear)
- Distance accuracy from Bermuda
- Signal environment (obstacles, reflections)

### Configuration

#### Enabling/Disabling

```yaml
# configuration.yaml
floorplan:
  providers:
    bermuda:
      enabled: true  # true to enable, false to disable
```

Or via UI:
1. Settings → Devices & Services → Floorplan → Edit
2. Check/uncheck "Enable Bermuda Location Provider"
3. Submit

#### Beacon Node Setup

Define in `floorplan/floorplan.yaml`:

```yaml
moving_entities:
  beacon_nodes:
    D4:5F:4E:A1:23:45:
      coordinates: [12, 2.5, 2.0]
    A3:2B:1C:F9:87:56:
      coordinates: [5, 4, 2.0]
    F1:E2:D3:C4:B5:A6:
      coordinates: [4, 8, 2.0]
```

**Best Practices for Beacon Placement:**
1. **Mount height**: 1.5-2.5m (typical wall height)
2. **Spread out**: Triangular or rectangular pattern
3. **Coverage**: Overlap across home
4. **Symmetry**: More symmetric = better accuracy
5. **Obstacles**: Minimize walls between scanners

**Good Configuration:**
```
          [Scanner A]
          (12, 2, 2)
              □
         /    |    \
        /     |     \
       /      |      \
      ●       ●       ●
(4, 8)   (5, 4)   (12, 2)
[Scanner C] [Device] [Scanner B]
```

### Services

#### Get Moving Entity Coordinates

```yaml
service: floorplan.get_moving_entity_coordinates
data:
  entity_id: device_tracker.john_phone
```

Response:
```json
{
  "entity_id": "device_tracker.john_phone",
  "coordinates": [7.5, 3.2, 1.1],
  "confidence": 0.85,
  "last_updated": "2024-01-15T10:30:42.123456+00:00"
}
```

#### Get All Moving Entities

```yaml
service: floorplan.get_all_moving_entity_coordinates
```

Response:
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
    }
  },
  "count": 2,
  "timestamp": "2024-01-15T10:30:42.987654+00:00"
}
```

### Limitations

1. **Minimum 3 Scanners Required**
   - 3 scanners: 3D calculation possible but limited accuracy
   - 4+ scanners: Overdetermined system, better accuracy through least-squares fitting

2. **Distance Accuracy**
   - RSSI-to-distance conversion has inherent variance
   - Environment-dependent (walls, reflections, interference)
   - Typical accuracy: ±1-3 meters indoors
   - Better accuracy with clear line-of-sight

3. **Z-Coordinate Limitations**
   - Height estimation relies on distance variations
   - Multi-floor determination limited without vertical beacon separation
   - Best suited for primary use case: X/Y localization within a floor

4. **Real-Time Limitations**
   - Update frequency depends on BLE advertisement rate
   - Typical: 1-5 second updates
   - Latency from RSSI → distance → coordinates calculation

5. **Coverage Limitations**
   - Devices must be in range of at least 3 beacons
   - BLE range typically 10-50m depending on device and environment
   - Dead zones possible in large homes or with obstacles

### Troubleshooting

#### No Coordinates Returned

**Check 1: Beacon nodes registered**
```yaml
service: floorplan.get_beacon_nodes
```
Should return at least 3 nodes.

**Check 2: Bermuda tracking active**
- Go to Developer Tools → States
- Search for `distance_to_*` sensors
- Should exist and have numeric values (not unknown)

**Check 3: Device is being tracked**
```yaml
service: floorplan.get_all_moving_entity_coordinates
```
Should include the device in response.

**Common Issues:**

| Issue | Cause | Solution |
|-------|-------|----------|
| "Need 3+ beacons" | Less than 3 beacon nodes configured | Add more beacon nodes to floorplan config |
| "Device not tracked" | Device not imported in Bermuda | Import device in Bermuda integration settings |
| "Distance sensor unknown" | Bermuda not receiving signal | Move device closer, check Bluetooth range |
| "Invalid device ID" | Beacon node ID not in Bluetooth registry | Verify device ID in Settings → Bluetooth |

#### Inaccurate Coordinates

**Causes & Solutions:**
1. **Poor beacon placement**
   - Current: Linear arrangement (bad)
   - Better: Triangular/rectangular spread (good)
   
2. **Too few beacons**
   - Current: 3 beacons (minimum, limited accuracy)
   - Better: 4-6 beacons (good overdetermined system)
   
3. **Beacons too close together**
   - Current: All clustered in one area
   - Better: Spread across home perimeter
   
4. **Bermuda distance accuracy issues**
   - Check Bermuda configuration
   - Verify calibration/TX power settings
   - Consider environment obstacles

#### Intermittent Tracking

**Causes & Solutions:**
1. **Device going out of range**
   - Check BLE range of scanners (~50m typical)
   - Consider adding more beacons
   
2. **Temporary signal interference**
   - 2.4 GHz interference (Wi-Fi, microwaves)
   - Solution: Varies by environment, may be temporary
   
3. **Scanner devices offline**
   - Verify scanners are powered and connected
   - Check in Settings → Devices & Services → Bluetooth

### Performance Considerations

- **Calculation Time**: ~5-50ms per device per call
- **Memory Usage**: Minimal, no state storage
- **Update Frequency**: Call service at 1-5 second intervals for smooth tracking
- **Scalability**: Tested with 10+ tracked devices, linear performance

### Future Providers

The system is designed to support additional providers:

1. **ESPresense** - Micro-HTTP for ESP32-based scanners
2. **Bluetooth LE Mesh** - Native mesh networking
3. **WiFi Triangulation** - Using WiFi signal strength
4. **Ultra-Wideband (UWB)** - High-accuracy positioning

All providers implement the same interface and return [X, Y, Z] coordinates.

## Provider Architecture

### Base Class Interface

```python
class LocationProvider:
    """Abstract base for location providers."""
    
    async def init(self, hass, config) -> bool:
        """Initialize provider."""
    
    async def get_moving_entity_coordinates(self, entity_id: str) -> tuple[float, float, float]:
        """Get [X, Y, Z] coordinates for entity."""
    
    async def get_all_moving_entities(self) -> dict[str, tuple[float, float, float]]:
        """Get coordinates for all tracked entities."""
    
    async def shutdown(self) -> None:
        """Cleanup on shutdown."""
```

### Adding Custom Providers

1. **Create Provider Class**: Inherit from `LocationProvider`
2. **Implement Methods**: `init()`, `get_moving_entity_coordinates()`, `get_all_moving_entities()`
3. **Register in Integration**: Add to provider registry
4. **Test**: Verify coordinate calculation

See [Architecture & Design](./ARCHITECTURE.md) for integration points.

## References

- **Trilateration Algorithm**: https://en.wikipedia.org/wiki/Trilateration
- **RSSI to Distance**: IEEE 802.11-2016 path loss model
- **Least Squares**: https://en.wikipedia.org/wiki/Least_squares
- **Levenberg-Marquardt**: https://en.wikipedia.org/wiki/Levenberg%E2%80%93Marquardt_algorithm
