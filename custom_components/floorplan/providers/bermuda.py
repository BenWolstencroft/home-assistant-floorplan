"""Bermuda location provider for trilateration-based positioning."""

import logging
import math
from typing import Any

from homeassistant.core import HomeAssistant, State

from .location_provider import LocationProvider

_LOGGER = logging.getLogger(__name__)


class BermudaLocationProvider(LocationProvider):
    """Location provider using Bermuda distance sensors for trilateration."""

    def __init__(self, hass: HomeAssistant, floorplan_manager):
        """Initialize Bermuda location provider."""
        super().__init__(hass, floorplan_manager)
        self.hass = hass
        self.manager = floorplan_manager

    async def get_moving_entity_coordinates(
        self, entity_id: str
    ) -> dict[str, Any] | None:
        """Get coordinates for a moving entity using Bermuda distance sensors.
        
        Args:
            entity_id: The moving entity ID to locate
            
        Returns:
            Dictionary with 'entity_id' and 'coordinates' [X, Y, Z], or None if not trackable.
        """
        coordinates = await self._triangulate_entity(entity_id)
        if coordinates:
            return {
                "entity_id": entity_id,
                "coordinates": coordinates,
            }
        return None

    async def get_all_moving_entity_coordinates(self) -> dict[str, Any]:
        """Get coordinates for all entities tracked by Bermuda.
        
        Discovers all distance sensors and triangulates their positions.
        
        Returns:
            Dictionary mapping entity_id -> {coordinates, confidence, last_updated}.
        """
        from datetime import datetime, timezone
        
        coordinates = {}

        # Find all Bermuda distance sensors
        distance_sensors = self._find_distance_sensors()
        
        # Group sensors by device (extract device prefix from sensor name)
        devices = self._group_sensors_by_device(distance_sensors)
        _LOGGER.debug(f"Found {len(distance_sensors)} Bermuda distance sensors, grouped into {len(devices)} devices: {list(devices.keys())}")

        # Triangulate each device
        for device_id, sensors in devices.items():
            try:
                coord = await self._triangulate_from_sensors(sensors)
                if coord:
                    _LOGGER.debug(f"Triangulation successful for {device_id}: {coord}")
                    # Map back to original entity IDs if they exist in HA
                    matched = False
                    for state in self.hass.states.async_all():
                        if state.entity_id.startswith("person.") or state.entity_id.startswith(
                            "device_tracker."
                        ):
                            if self._entity_matches_device(state.entity_id, device_id):
                                _LOGGER.debug(f"Matched device {device_id} to entity {state.entity_id}")
                                # Return in documented format with metadata
                                coordinates[state.entity_id] = {
                                    "coordinates": coord,
                                    "confidence": 0.85,  # TODO: Calculate actual confidence from triangulation error
                                    "last_updated": datetime.now(timezone.utc).isoformat(),
                                }
                                matched = True
                                break
                    if not matched:
                        _LOGGER.debug(f"No person/device_tracker entity matched device {device_id}")
                else:
                    _LOGGER.warning(f"Triangulation failed for {device_id} - insufficient data")
            except Exception as err:
                _LOGGER.warning(f"Error triangulating device {device_id}: {err}")

        _LOGGER.debug(f"Returning {len(coordinates)} triangulated entities")
        return coordinates

    def _find_distance_sensors(self) -> list[State]:
        """Find all Bermuda distance sensors in Home Assistant.
        
        Returns:
            List of sensor states with device_class='distance'.
        """
        sensors = []
        for state in self.hass.states.async_all():
            if state.entity_id.startswith("sensor."):
                if (
                    state.attributes.get("device_class") == "distance"
                    and "distance_to_" in state.entity_id
                ):
                    # Check if it's a valid numeric distance (not unknown/unavailable)
                    try:
                        float(state.state)
                        sensors.append(state)
                    except (ValueError, TypeError):
                        pass
        return sensors

    def _group_sensors_by_device(self, sensors: list[State]) -> dict[str, list[State]]:
        """Group distance sensors by device.
        
        Extracts device ID prefix from sensor entity_id.
        Example: sensor.bwzugdvi_distance_to_lounge -> device_id = 'bwzugdvi'
        
        Args:
            sensors: List of distance sensor states
            
        Returns:
            Dictionary mapping device_id -> list of sensor states for that device.
        """
        devices = {}
        for sensor in sensors:
            # Extract device ID from sensor name
            # Format: sensor.<device_id>_distance_to_<node_name>
            parts = sensor.entity_id.replace("sensor.", "").split("_distance_to_")
            if len(parts) == 2:
                device_id = parts[0]
                if device_id not in devices:
                    devices[device_id] = []
                devices[device_id].append(sensor)

        return devices

    async def _triangulate_entity(self, entity_id: str) -> list[float] | None:
        """Triangulate a specific entity's position.
        
        Args:
            entity_id: The entity to triangulate
            
        Returns:
            [X, Y, Z] coordinates or None if not enough distance data.
        """
        # Find distance sensors for this entity
        sensors = []
        for state in self.hass.states.async_all():
            if (
                state.entity_id.startswith("sensor.")
                and state.attributes.get("device_class") == "distance"
                and "distance_to_" in state.entity_id
            ):
                # Try to match entity to device in sensor name
                if self._entity_matches_device(entity_id, state.entity_id):
                    try:
                        float(state.state)
                        sensors.append(state)
                    except (ValueError, TypeError):
                        pass

        if not sensors:
            return None

        return await self._triangulate_from_sensors(sensors)

    async def _triangulate_from_sensors(
        self, sensors: list[State]
    ) -> list[float] | None:
        """Triangulate position from distance sensors using trilateration.
        
        Uses 3D trilateration algorithm to find the point that minimizes
        the sum of squared differences between measured and calculated distances.
        
        Args:
            sensors: List of distance sensor states
            
        Returns:
            [X, Y, Z] coordinates or None if trilateration fails.
        """
        # Get beacon nodes with friendly names enriched from device registry
        beacon_nodes = self.manager.get_all_beacon_node_data()
        if not beacon_nodes:
            _LOGGER.debug("No beacon nodes configured")
            return None

        _LOGGER.debug(f"Available beacon nodes: {list(beacon_nodes.keys())}")
        # Log friendly names for debugging
        for node_id, data in beacon_nodes.items():
            friendly_name = data.get("name", "N/A") if isinstance(data, dict) else "N/A"
            _LOGGER.debug(f"  {node_id}: friendly_name='{friendly_name}'")
        
        _LOGGER.debug(f"Processing {len(sensors)} sensors")

        # Build distance measurements and beacon node positions
        distances = {}
        node_positions = {}

        for sensor in sensors:
            _LOGGER.debug(f"  Sensor: {sensor.entity_id} = {sensor.state}m")
            
            # Extract node name from sensor
            node_name = self._extract_node_name_from_sensor(sensor.entity_id)
            if not node_name:
                _LOGGER.debug(f"    Could not extract node name from {sensor.entity_id}")
                continue
            
            _LOGGER.debug(f"    Extracted node name: {node_name}")

            # Find matching beacon node
            matching_node = self._find_beacon_node_by_name(node_name, beacon_nodes)
            if not matching_node:
                _LOGGER.debug(f"    No matching beacon node found for '{node_name}'")
                continue
            
            node_id, coordinates = matching_node
            _LOGGER.debug(f"    Matched to beacon node: {node_id} at {coordinates}")

            try:
                distance = float(sensor.state)
                distances[node_id] = distance
                node_positions[node_id] = coordinates
            except (ValueError, TypeError):
                _LOGGER.debug(f"    Could not parse distance value: {sensor.state}")
                pass

        _LOGGER.debug(f"Matched {len(distances)} beacons: {list(distances.keys())}")
        
        if len(distances) < 3:
            _LOGGER.debug(f"Insufficient beacons matched ({len(distances)}/3 required)")
            return None

        # Filter out outlier distances that are geometrically impossible
        # Calculate max theoretical distance between any two beacons
        beacon_positions = list(node_positions.values())
        max_beacon_separation = 0
        for i in range(len(beacon_positions)):
            for j in range(i + 1, len(beacon_positions)):
                sep = math.sqrt(
                    sum((beacon_positions[i][k] - beacon_positions[j][k]) ** 2 for k in range(3))
                )
                max_beacon_separation = max(max_beacon_separation, sep)
        
        # Filter distances: any distance > 2x max beacon separation is likely bad
        outlier_threshold = max_beacon_separation * 2
        filtered_distances = {}
        filtered_positions = {}
        
        for node_id in list(distances.keys()):
            if distances[node_id] > outlier_threshold:
                _LOGGER.debug(f"    Filtering outlier: {node_id} distance {distances[node_id]:.2f}m > threshold {outlier_threshold:.2f}m")
            else:
                filtered_distances[node_id] = distances[node_id]
                filtered_positions[node_id] = node_positions[node_id]
        
        if len(filtered_distances) < 3:
            _LOGGER.debug(f"Insufficient beacons after filtering ({len(filtered_distances)}/3 required)")
            return None
        
        _LOGGER.debug(f"Using {len(filtered_distances)} beacons after outlier filtering")

        # Perform 3D trilateration
        try:
            result = self._trilaterate_3d(filtered_positions, filtered_distances)
            return result
        except Exception as err:
            # Only log actual errors, not expected calculation issues
            if "singular matrix" not in str(err).lower():
                _LOGGER.error("Trilateration failed: %s", err)
            return None

    def _extract_node_name_from_sensor(self, entity_id: str) -> str | None:
        """Extract beacon node name from sensor entity_id.
        
        Example: sensor.device_distance_to_lounge_bluetooth_proxy
                 -> 'lounge_bluetooth_proxy'
        
        Args:
            entity_id: The sensor entity ID
            
        Returns:
            Node name or None if not parseable.
        """
        if "_distance_to_" not in entity_id:
            return None

        # Split on 'distance_to_' and take the part after
        parts = entity_id.split("_distance_to_")
        if len(parts) == 2:
            return parts[1]
        return None

    def _find_beacon_node_by_name(
        self, node_name: str, beacon_nodes: dict[str, Any]
    ) -> tuple[str, list[float]] | None:
        """Find a beacon node by name or name pattern.
        
        Matches node names flexibly since Bermuda sensor names might not
        exactly match beacon node IDs. Also matches against friendly names
        by normalizing them (lowercase with underscores).
        
        Args:
            node_name: Name extracted from sensor (e.g., 'lounge_bluetooth_proxy')
            beacon_nodes: Dictionary of node_id -> {coordinates, name} or [coordinates]
            
        Returns:
            Tuple of (node_id, coordinates) or None if no match found.
        """
        def normalize_name(name: str) -> str:
            """Normalize name to lowercase with underscores."""
            return name.lower().replace(" ", "_").replace("-", "_")
        
        # Normalize for comparison
        node_name_normalized = normalize_name(node_name)

        # Check each beacon node
        for node_id, data in beacon_nodes.items():
            # Extract coordinates based on format (new dict format or old list format)
            if isinstance(data, dict):
                coords = data.get("coordinates", [])
                friendly_name = data.get("name", "")
            else:
                coords = data
                friendly_name = ""
            
            # Match 1: Exact match on node ID
            if normalize_name(node_id) == node_name_normalized:
                return (node_id, coords)
            
            # Match 2: Friendly name normalized matches sensor name
            if friendly_name and normalize_name(friendly_name) == node_name_normalized:
                return (node_id, coords)
            
            # Match 3: Partial match - node name contains beacon node ID
            if normalize_name(node_id) in node_name_normalized:
                return (node_id, coords)
            
            # Match 4: Reverse partial match - beacon node ID contains sensor name
            if node_name_normalized in normalize_name(node_id):
                return (node_id, coords)
            
            # Match 5: Friendly name partial match
            if friendly_name and normalize_name(friendly_name) in node_name_normalized:
                return (node_id, coords)

        return None

    def _trilaterate_3d(
        self,
        node_positions: dict[str, list[float]],
        distances: dict[str, float],
    ) -> list[float]:
        """Perform 3D trilateration using least squares method.
        
        Uses iterative least squares approach to find the position that
        minimizes the sum of squared errors between measured and calculated distances.
        
        Args:
            node_positions: Dictionary mapping node_id -> [X, Y, Z]
            distances: Dictionary mapping node_id -> distance in meters
            
        Returns:
            [X, Y, Z] coordinates
            
        Raises:
            ValueError: If trilateration fails to converge.
        """
        # Convert to lists for processing
        nodes = list(node_positions.values())
        measured_distances = [distances[nid] for nid in node_positions.keys()]

        if len(nodes) < 3:
            raise ValueError("Need at least 3 beacon nodes for trilateration")

        # Initial guess: centroid of beacon nodes
        x = sum(n[0] for n in nodes) / len(nodes)
        y = sum(n[1] for n in nodes) / len(nodes)
        z = sum(n[2] for n in nodes) / len(nodes)

        # Iterative Gauss-Newton refinement
        _LOGGER.debug(f"Trilateration starting from centroid: [{x:.2f}, {y:.2f}, {z:.2f}]")
        _LOGGER.debug(f"Beacon positions: {nodes}")
        _LOGGER.debug(f"Measured distances: {measured_distances}")
        
        # Validate measured distances against beacon positions
        for i, node in enumerate(nodes):
            for j in range(i + 1, len(nodes)):
                beacon_distance = math.sqrt(
                    sum((nodes[i][k] - nodes[j][k]) ** 2 for k in range(3))
                )
                measured_sum = measured_distances[i] + measured_distances[j]
                measured_diff = abs(measured_distances[i] - measured_distances[j])
                
                # Triangle inequality check: |d1 - d2| <= beacon_distance <= d1 + d2
                if beacon_distance > measured_sum or beacon_distance < measured_diff:
                    _LOGGER.warning(
                        f"Triangle inequality violated: beacons {i},{j} are {beacon_distance:.2f}m apart, "
                        f"but measured distances {measured_distances[i]:.2f}m and {measured_distances[j]:.2f}m "
                        f"imply range [{measured_diff:.2f}m, {measured_sum:.2f}m]"
                    )
        
        max_iterations = 50
        convergence_threshold = 0.1  # 10cm
        
        for iteration in range(max_iterations):
            # Calculate current distances from estimated position
            calculated_distances = [
                math.sqrt((n[0] - x) ** 2 + (n[1] - y) ** 2 + (n[2] - z) ** 2)
                for n in nodes
            ]

            # Calculate error
            errors = [
                measured_distances[i] - calculated_distances[i]
                for i in range(len(nodes))
            ]
            rms_error = math.sqrt(sum(e ** 2 for e in errors) / len(errors))
            
            if iteration < 5 or iteration % 10 == 0:
                _LOGGER.debug(f"Iteration {iteration}: pos=[{x:.2f}, {y:.2f}, {z:.2f}], rms_error={rms_error:.2f}m, errors={[f'{e:.2f}' for e in errors]}")

            # Check convergence
            if rms_error < convergence_threshold:
                _LOGGER.debug(f"Converged at iteration {iteration}: pos=[{x:.2f}, {y:.2f}, {z:.2f}], rms_error={rms_error:.2f}m")
                break

            # Build Jacobian matrix and compute update using Gauss-Newton
            # J[i] = [-2(x_i - x), -2(y_i - y), -2(z_i - z)] / (2 * d_calc_i)
            #      = [-(x_i - x)/d_calc_i, -(y_i - y)/d_calc_i, -(z_i - z)/d_calc_i]
            dx = 0
            dy = 0
            dz = 0
            
            for i, node in enumerate(nodes):
                if calculated_distances[i] > 0.001:  # Avoid division by zero
                    # Gradient of distance function
                    grad_x = (x - node[0]) / calculated_distances[i]
                    grad_y = (y - node[1]) / calculated_distances[i]
                    grad_z = (z - node[2]) / calculated_distances[i]
                    
                    # Update based on error (simplified Gauss-Newton)
                    dx -= errors[i] * grad_x
                    dy -= errors[i] * grad_y
                    dz -= errors[i] * grad_z

            # Normalize update and apply with damping
            update_magnitude = math.sqrt(dx**2 + dy**2 + dz**2)
            if update_magnitude > 5.0:  # Limit step size to 5 meters
                scale = 5.0 / update_magnitude
                dx *= scale
                dy *= scale
                dz *= scale
            
            # Apply update
            x += dx
            y += dy
            z += dz
            
            # Sanity check for divergence
            if abs(x) > 100 or abs(y) > 100 or abs(z) > 100:
                _LOGGER.warning(f"Trilateration diverging at iteration {iteration}: pos=[{x:.2f}, {y:.2f}, {z:.2f}], rms_error={rms_error:.2f}m")
                raise ValueError("Trilateration diverged - position outside reasonable bounds")

        # Final sanity check
        if abs(x) > 100 or abs(y) > 100 or abs(z) > 100:
            raise ValueError(f"Trilateration result unreasonable: [{x:.2f}, {y:.2f}, {z:.2f}]")

        # Clamp Z to beacon node floor (shouldn't go below lowest beacon)
        min_z = min(n[2] for n in nodes)
        max_z = max(n[2] for n in nodes)
        z = max(min(z, max_z + 5.0), min_z - 0.5)  # Within beacon Z range + margin

        _LOGGER.debug(f"Final position: [{x:.2f}, {y:.2f}, {z:.2f}]")
        return [x, y, z]

    def _entity_matches_device(self, entity_id: str, device_id: str) -> bool:
        """Check if an entity matches a device ID.
        
        This is a heuristic match based on entity name similarity.
        
        Args:
            entity_id: Home Assistant entity ID (e.g., 'person.john')
            device_id: Device ID from sensor name (e.g., 'bwzugdvi')
            
        Returns:
            True if entity likely represents the device.
        """
        # Get entity friendly name
        state = self.hass.states.get(entity_id)
        if not state:
            return False

        friendly_name = state.attributes.get("friendly_name", "").lower()
        entity_name = entity_id.split(".")[-1].lower()
        device_id_lower = device_id.lower()

        # Check if device_id is in friendly name or entity name
        return device_id_lower in friendly_name or device_id_lower in entity_name
