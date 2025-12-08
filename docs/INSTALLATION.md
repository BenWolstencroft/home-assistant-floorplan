# Installation & Configuration Guide

Complete setup instructions for the Home Assistant Floorplan integration.

## Installation Methods

### Option 1: Via HACS (Recommended)

HACS (Home Assistant Community Store) makes installation and updates simple.

1. Ensure HACS is installed. If not, follow [HACS installation](https://hacs.xyz/docs/setup/prerequisites)
2. Go to **HACS → Integrations**
3. Click **Explore & Download Repositories**
4. Search for **"Floorplan"**
5. Click the result to open the integration
6. Click **Download**
7. Select the version and confirm
8. **Restart Home Assistant** (Settings → System → Restart)
9. Go to **Settings → Devices & Services → Create Integration**
10. Search for and select **"Floorplan"**
11. Follow the setup wizard

### Option 2: Manual Installation

For manual installation or development:

1. Download or clone the repository
2. Copy the `custom_components/floorplan` directory to your Home Assistant `custom_components` directory:
   ```
   ~/.homeassistant/custom_components/floorplan/
   ```
3. **Restart Home Assistant** (Settings → System → Restart)
4. Go to **Settings → Devices & Services → Create Integration**
5. Search for and select **"Floorplan"**
6. Follow the setup wizard

## Initial Setup

### Configuration Flow (UI)

After installation, you'll see a configuration dialog:

1. **Floorplan Integration Setup**
   - **Provider Configuration**: Choose whether to enable the Bermuda location provider
     - ✅ **Enable Bermuda Location Provider (BLE Trilateration)** - for tracking moving devices
     - ⬜ Uncheck to disable if you only need static entity positioning

2. Click **Submit** to complete setup

Your floorplan integration is now registered, but you need to configure your actual floorplan layout and entities.

## Floorplan Configuration

### Configuration File

Create `floorplan/floorplan.yaml` in your Home Assistant configuration directory (typically `~/.homeassistant/floorplan/floorplan.yaml`).

**Note:** The directory is created automatically after the integration setup, or you can create it manually.

### Complete YAML Reference

#### Floors

Define the physical floors in your home with their **ceiling heights**:

```yaml
floors:
  ground_floor:
    height: 2.4         # Ceiling height in meters (ground floor ceiling)
  1st_floor:
    height: 5.2         # First floor ceiling (2.4m ground + 2.8m floor height)
  2nd_floor:
    height: 7.6         # Second floor ceiling (5.2m + 2.4m floor height)
  basement:
    height: -2.5        # Basement ceiling (below ground level)
```

**Important Semantics:**
- **Floor ID**: Unique identifier (alphanumeric with underscores) - friendly names auto-fetched from HA floor registry
- **height**: **Ceiling height** in meters (not floor level!)
  - Used for filtering beacons and entities by floor
  - Ground floor range: 0m to its ceiling height (e.g., 0-2.4m)
  - First floor range: ground ceiling to first ceiling (e.g., 2.4-5.2m)
  - Beacons/entities assigned to floor based on their Z coordinate falling in range

#### Rooms

Define room boundaries and properties:

```yaml
rooms:
  living_room:
    name: Living Room                    # Display name
    floor: ground_floor                  # Floor ID from above
    area: living_room                    # Optional: Home Assistant area ID
    boundaries:
      - [0, 0]                           # Point 1: X=0m, Y=0m
      - [10, 0]                          # Point 2: X=10m, Y=0m
      - [10, 8]                          # Point 3: X=10m, Y=8m
      - [0, 8]                           # Point 4: X=0m, Y=8m
  
  kitchen:
    name: Kitchen
    floor: ground_floor
    area: kitchen
    boundaries:
      - [10, 0]
      - [15, 0]
      - [15, 5]
      - [10, 5]
  
  hallway:
    name: Hallway
    floor: ground_floor
    boundaries:
      - [8, 0]
      - [10, 0]
      - [10, 2]
      - [8, 2]
```

**Properties:**
- **name**: Display name for the room (OPTIONAL - if omitted, uses name from Home Assistant area registry)
- **floor**: Floor ID where this room is located
- **area**: Optional link to Home Assistant area (for automation/grouping AND name lookup if name not specified)
- **boundaries**: List of `[X, Y]` coordinates defining the room polygon
  - Points should form a closed polygon (first and last point should be adjacent)
  - Order (clockwise/counter-clockwise) doesn't matter
  - At least 3 points required for a valid polygon

**Coordinate System:**
- Origin `[0, 0]` is typically at one corner of your home
- X increases to the right
- Y increases forward/away
- All measurements in **meters**
- Keep values simple for easier mental mapping (use whole numbers where possible)

#### Static Entities

Position any Home Assistant entity at a fixed location:

```yaml
static_entities:
  light.living_room:
    coordinates: [5, 4, 1.8]           # [X, Y, Z] in meters
  
  sensor.hallway_temperature:
    coordinates: [9, 1, 1.5]
  
  camera.front_door:
    coordinates: [0, 0, 2.2]
  
  light.bedroom_1:
    coordinates: [3, 8, 0.9]
  
  switch.office_power:
    coordinates: [12, 5, 0.8]
```

**Entity ID Format:** Use the full Home Assistant entity ID as shown in Developer Tools

**Coordinates:** `[X, Y, Z]`
- **X**: Horizontal position (left/right) in meters
- **Y**: Depth position (forward/back) in meters
- **Z**: Height above ground in meters
  - Typical heights:
    - Lights: 1.8-2.4m (ceiling height)
    - Outlets/switches: 0.8-1.2m
    - Cameras: 1.5-2.2m
    - Floor sensors: 0.0-0.2m

#### Moving Entities - Beacon Nodes

Define BLE scanner nodes used for trilateration of moving devices:

```yaml
moving_entities:
  beacon_nodes:
    D4:5F:4E:A1:23:45:                 # Bluetooth device ID
      coordinates: [12, 2.5, 2.0]      # [X, Y, Z] in meters
    
    A3:2B:1C:F9:87:56:
      coordinates: [5, 4, 2.0]
    
    F1:E2:D3:C4:B5:A6:
      coordinates: [4, 8, 2.0]
```

**Finding Device IDs:**
1. Go to **Settings → Devices & Services → Bluetooth**
2. Look for your BLE scanner devices (typically named with MAC addresses)
3. The device ID is shown under each device

**Device Friendly Names:**
- Device friendly names are automatically fetched from Home Assistant device registry
- Displayed on the floorplan card instead of MAC addresses
- Uses custom name if set, otherwise device name
- Falls back to MAC address if device not found in registry

**Positioning Guidelines:**
- Mount scanners 1.5-2.5m high (typical wall height)
- Spread them throughout your home for better coverage
- At least 3 scanners required for 3D trilateration
- 4+ scanners recommended for better accuracy
- Form a rough triangle or square around your tracking area
- Z coordinate should match actual mounting height for accurate tracking

### Complete Example Configuration

```yaml
# floorplan/floorplan.yaml

floors:
  ground_floor:
    height: 2.4    # Ground floor ceiling height
  1st_floor:
    height: 5.2    # First floor ceiling height (2.4m + 2.8m)

rooms:
  # Ground Floor
  living_room:
    name: Living Room
    floor: ground_floor
    area: living_room
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
  
  hallway:
    name: Hallway
    floor: ground_floor
    boundaries:
      - [8, 0]
      - [10, 0]
      - [10, 8]
      - [8, 8]
  
  # First Floor
  master_bedroom:
    name: Master Bedroom
    floor: 1st_floor
    area: master_bedroom
    boundaries:
      - [0, 0]
      - [8, 0]
      - [8, 10]
      - [0, 10]
  
  guest_bedroom:
    name: Guest Bedroom
    floor: 1st_floor
    area: guest_bedroom
    boundaries:
      - [8, 0]
      - [13, 0]
      - [13, 8]
      - [8, 8]
  
  bathroom:
    name: Bathroom
    floor: 1st_floor
    boundaries:
      - [13, 0]
      - [15, 0]
      - [15, 5]
      - [13, 5]

static_entities:
  # Ground Floor Lighting
  light.living_room:
    coordinates: [5, 4, 2.3]
  
  light.kitchen:
    coordinates: [12.5, 2.5, 2.3]
  
  light.hallway:
    coordinates: [9, 4, 2.3]
  
  # Cameras
  camera.front_door:
    coordinates: [0, 0, 2.1]
  
  camera.living_room:
    coordinates: [8.5, 7.5, 2.4]
  
  # Sensors
  sensor.living_room_temp:
    coordinates: [5, 4, 1.5]
  
  sensor.kitchen_motion:
    coordinates: [14, 3, 2.0]

moving_entities:
  beacon_nodes:
    D4:5F:4E:A1:23:45:
      coordinates: [12, 2.5, 2.0]
    
    A3:2B:1C:F9:87:56:
      coordinates: [5, 4, 2.0]
    
    F1:E2:D3:C4:B5:A6:
      coordinates: [4, 8, 2.0]
```

## Provider Configuration

### Bermuda Location Provider

The Bermuda provider is optional and enables BLE-based trilateration for tracking moving devices.

#### Enabling/Disabling

**Via UI:**
1. Go to **Settings → Devices & Services**
2. Find the "Floorplan" integration entry
3. Click **Edit** (gear icon)
4. Check/uncheck "Enable Bermuda Location Provider"
5. Click **Submit**

**Via YAML (if using YAML configuration):**
```yaml
# configuration.yaml
floorplan:
  providers:
    bermuda:
      enabled: true  # false to disable
```

#### Requirements

To use Bermuda provider for location tracking:

1. **Bermuda integration installed** - Install via HACS or manually
2. **Beacon nodes configured** - At least 3 BLE scanners with known positions (see above)
3. **Bermuda configured** - Set up device tracking in Bermuda (import devices to track)
4. **Distance sensors available** - Bermuda creates `distance_to_*` sensors for each device

#### How Bermuda Works

1. **Discovery Phase**: System finds all `distance_to_*` sensors created by Bermuda
2. **Matching Phase**: Matches sensor names to beacon nodes in your floorplan
3. **Triangulation**: Uses 3D least-squares trilateration with distance measurements
4. **Calculation**: Returns [X, Y, Z] coordinates for tracked devices

#### Limitations

- **Minimum 3 scanners required** - At least 3 distance measurements needed for 3D calculation
- **Distance accuracy** - Accuracy depends on Bermuda's RSSI-to-distance conversion
- **Z-coordinate accuracy** - Primary use is X/Y positioning (Z less precise)
- **Range dependent** - Devices must be in BLE range of at least 3 scanners
- **Real-time**: Updates as frequently as Bermuda provides new distance measurements

See [Location Providers](./PROVIDERS.md) for more details.

## Configuration File Location

The floorplan configuration file should be at:

```
~/.homeassistant/floorplan/floorplan.yaml
```

Or relative to your Home Assistant configuration directory:

```
<ha_config>/floorplan/floorplan.yaml
```

Home Assistant creates this directory automatically after you run the integration for the first time, or you can create it manually.

## Verification

After creating your configuration file:

1. Go to **Settings → System → Logs** (if Home Assistant 2024.1+)
2. Or check the terminal output for any errors
3. Restart Home Assistant if configuration changed
4. Test by calling a service: **Developer Tools → Services**
5. Search for `floorplan.*` services
6. Call `floorplan.get_rooms_by_floor` to verify configuration loaded

If you see no services, check logs for errors in loading the configuration file.

## Troubleshooting

### Configuration File Not Loading

**Symptom:** Services don't appear, no rooms visible

**Solutions:**
1. Verify file is at `floorplan/floorplan.yaml` (check capitalization)
2. Validate YAML syntax using an online YAML validator
3. Check Home Assistant logs for parsing errors
4. Ensure proper indentation (YAML is whitespace-sensitive)
5. Restart Home Assistant after making changes

### Invalid Device IDs

**Symptom:** "Device not registered" error when adding beacon nodes

**Solutions:**
1. Verify device ID in **Settings → Devices & Services → Bluetooth**
2. Copy the exact ID (watch for special characters)
3. Ensure device is registered in Home Assistant Bluetooth registry
4. Some devices may use different formats (MAC or UUID)

### Rooms Not Appearing

**Symptom:** Services return empty room list

**Solutions:**
1. Verify floorplan.yaml exists and is readable
2. Check that `floors` section is defined
3. Ensure rooms reference valid floor IDs
4. Restart integration or Home Assistant
5. Check logs for parsing errors

### Trilateration Not Working

**Symptom:** Bermuda provider enabled but no coordinates returned

**Solutions:**
1. Verify at least 3 beacon nodes configured
2. Check that beacon node IDs match Bluetooth registry exactly
3. Ensure Bermuda is tracking target devices (has distance_to_* sensors)
4. Verify distance sensors are not in "unknown" state
5. Try calling `floorplan.get_beacon_nodes` to verify node registration

## Next Steps

- [Services Reference](./SERVICES.md) - API documentation for all available services
- [Architecture & Design](./ARCHITECTURE.md) - How the system works internally
- [Location Providers](./PROVIDERS.md) - Details on Bermuda and future providers
