# Testing Guide

Complete guide to testing the Floorplan integration.

## Quick Start

### Run All Tests
```bash
cd home-assistant-floorplan
pytest
```

### Run with Coverage
```bash
pytest --cov=custom_components/floorplan --cov-report=html
```

### Run Specific Test
```bash
pytest tests/test_floorplan_manager.py::TestFloorplanManager::test_add_floor -v
```

## Test Structure

```
tests/
├── conftest.py                 # Pytest fixtures
├── test_floorplan_manager.py   # FloorplanManager tests (38 tests)
├── test_bermuda_provider.py    # Bermuda provider tests (15 tests)
├── test_config_flow.py         # Config flow tests (12 tests)
├── test_constants.py           # Constants tests (15 tests)
├── test_helpers.py             # Test utilities
└── README.md                   # Detailed testing documentation
```

**Total: 80+ unit and integration tests**

## Test Coverage

### 1. FloorplanManager (`test_floorplan_manager.py`)

**Purpose**: Validate data persistence and registry management

**Test Categories**:
- **Initialization**: Manager setup and default state
- **YAML I/O**: Loading and saving configuration files
- **Floor Management**: Add, retrieve, get by ID
- **Room Management**: Add, retrieve, get by floor, validate boundaries
- **Static Entity Management**: CRUD operations, coordinate validation
- **Beacon Node Management**: Add, update, delete, retrieve
- **Error Handling**: Corrupted YAML, invalid coordinates
- **Data Structure**: Coordinate format validation

**Example Test**:
```python
def test_add_static_entity(self, manager):
    """Test adding a static entity."""
    manager.add_static_entity("light.living_room", [5, 4, 1.8])
    assert manager.get_static_entity("light.living_room") == [5, 4, 1.8]
```

### 2. Bermuda Provider (`test_bermuda_provider.py`)

**Purpose**: Validate BLE trilateration algorithm

**Test Categories**:
- **Provider Initialization**: Setup and configuration
- **Trilateration Algorithm**: 
  - 2D and 3D distance calculations
  - Least-squares fitting
  - Centroid calculations
  - Residual error computation
- **Edge Cases**:
  - Insufficient beacons (< 3)
  - Missing distance data
  - Invalid state values
- **Integration**: Home Assistant state reading
- **Mathematical Accuracy**: Validates calculations within tolerance

**Example Test**:
```python
def test_trilaterate_at_known_point(self, bermuda_provider):
    """Test trilateration at a known point."""
    # Device at [5, 4, 2.0]
    beacon_distances = {
        "beacon_1": 6.403,
        "beacon_2": 6.403,
        "beacon_3": 4.123,
    }
    # ... calculate coordinates and verify
```

### 3. Config Flow (`test_config_flow.py`)

**Purpose**: Validate configuration UI and data handling

**Test Categories**:
- **User Step**: Initial configuration form
- **Provider Configuration**: Enable/disable providers
- **Data Structure**: Entry data layout
- **Unique ID**: Duplicate prevention
- **Import Step**: YAML configuration import
- **Schema Validation**: Data type and structure validation
- **Extensibility**: Support for multiple providers

**Example Test**:
```python
async def test_async_step_user_with_bermuda_enabled(self, config_flow):
    """Test user step with Bermuda enabled."""
    user_input = {
        CONF_BERMUDA: {CONF_ENABLED: True}
    }
    result = await config_flow.async_step_user(user_input)
    assert result["type"] == "create_entry"
```

### 4. Constants (`test_constants.py`)

**Purpose**: Validate configuration constants and data structures

**Test Categories**:
- **Constant Definitions**: All required constants exist
- **Naming Conventions**: Consistent uppercase naming
- **Data Structure Keys**: Room, floor, entity constants
- **Provider Configuration**: Bermuda provider structure
- **Uniqueness**: No conflicting constant values
- **Future Extensibility**: Multi-provider support readiness

**Example Test**:
```python
def test_config_keys(self):
    """Test configuration keys are defined."""
    assert CONF_PROVIDERS == "providers"
    assert CONF_BERMUDA == "bermuda"
    assert CONF_ENABLED == "enabled"
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_floorplan_manager.py

# Run specific test class
pytest tests/test_floorplan_manager.py::TestFloorplanManager

# Run specific test
pytest tests/test_floorplan_manager.py::TestFloorplanManager::test_add_floor

# Run with verbose output
pytest -v

# Run with print statements visible
pytest -s
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=custom_components/floorplan --cov-report=html

# Display coverage in terminal
pytest --cov=custom_components/floorplan --cov-report=term-missing

# Coverage for specific file
pytest --cov=custom_components/floorplan/floorplan_manager.py
```

### Advanced Options

```bash
# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Run only failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff

# Show slowest tests
pytest --durations=10

# Run with debugger on failure
pytest --pdb

# Parallel testing (requires pytest-xdist)
pytest -n auto
```

## Test Fixtures

Fixtures provide reusable test setup. Defined in `conftest.py`:

### Mock Home Assistant
```python
@pytest.fixture
def hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    hass.states.async_all = MagicMock(return_value=[])
    return hass
```

### Temporary Data Directory
```python
@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for tests."""
    data_dir = tmp_path / "floorplan"
    data_dir.mkdir()
    return data_dir
```

### Sample Floorplan Data
```python
@pytest.fixture
def sample_floorplan_data():
    """Sample floorplan configuration for testing."""
    return {
        "floors": {...},
        "rooms": {...},
        "static_entities": {...},
        "moving_entities": {...}
    }
```

## Test Patterns

### AAA Pattern (Arrange, Act, Assert)

```python
def test_add_floor(self, manager):
    """Test adding a floor."""
    # Arrange - setup initial state
    floor_id = "ground_floor"
    height = 0
    
    # Act - execute the code being tested
    manager.add_floor(floor_id, height)
    
    # Assert - verify results
    assert floor_id in manager.floorplan_data["floors"]
```

### Async Test Pattern

```python
@pytest.mark.asyncio
async def test_load_floorplan(self, manager):
    """Test loading floorplan configuration."""
    await manager.async_load_floorplan()
    assert manager.config_file.exists()
```

### Mocking External Dependencies

```python
def test_with_mocked_state(self, manager):
    """Test with mocked Home Assistant state."""
    with patch.object(manager, 'hass') as mock_hass:
        mock_hass.states.get.return_value = MagicMock(state="on")
        # Test code
```

## Test Utilities

Helper functions in `test_helpers.py`:

```python
# Create mock Home Assistant
hass = create_mock_home_assistant()

# Create mock state
state = create_mock_state("light.living_room", "on")

# Calculate distance
distance = calculate_euclidean_distance([0, 0, 0], [3, 4, 0])
# Returns: 5.0

# Generate test beacon network
beacons = generate_test_beacon_network(width=10, height=10, num_beacons=3)

# Validate floorplan structure
is_valid = validate_floorplan_structure(data)

# Validate entity coordinates
is_valid = validate_entity_coordinates([5, 4, 1.8])
```

## CI/CD Integration

Tests run automatically in GitHub Actions:

### Workflows
- `.github/workflows/validate.yml` - Runs on every push/PR
  - Pytest execution
  - Coverage report
  - Lint and type checking

### Coverage Requirements
- Minimum: 80% coverage
- Target: 90%+ coverage

### Running Locally Like CI

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
pytest --cov=custom_components/floorplan --cov-report=term-missing

# Run linting
pylint custom_components/floorplan

# Run type checking
mypy custom_components/floorplan
```

## Debugging Tests

### View Test Output
```bash
# Show all output (including print statements)
pytest -s tests/test_floorplan_manager.py::TestFloorplanManager::test_add_floor

# Show more verbose output
pytest -vv

# Show assertion details
pytest -l
```

### Interactive Debugging
```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start
pytest --trace
```

### Understanding Test Failures

```python
# Assertion with message
assert manager.config_file.exists(), "Config file should be created"

# Use pytest.raises for exception testing
with pytest.raises(ValueError, match="Invalid coordinates"):
    manager.add_static_entity("light.test", [1, 2])  # Missing Z
```

## Performance Testing

### Identify Slow Tests
```bash
pytest --durations=10
```

### Profile Test Execution
```bash
pytest --profile
```

## Coverage Analysis

### HTML Coverage Report
```bash
pytest --cov=custom_components/floorplan --cov-report=html
# Open htmlcov/index.html in browser
```

### Missing Coverage
```bash
pytest --cov=custom_components/floorplan --cov-report=term-missing
# Shows lines not covered by tests
```

## Adding New Tests

### Test File Structure
```python
"""Tests for [component]."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components" / "floorplan"))

from [module] import [Class]


class Test[Feature]:
    """Test [feature] functionality."""

    @pytest.fixture
    def setup(self):
        """Setup test fixtures."""
        # Create test objects
        return test_object

    def test_something(self, setup):
        """Test description."""
        # Arrange
        
        # Act
        
        # Assert
```

### Checklist for New Tests
- [ ] Use descriptive test name: `test_<what>_<condition>_<result>`
- [ ] Add docstring explaining what is tested
- [ ] Use AAA pattern (Arrange, Act, Assert)
- [ ] Mock external dependencies
- [ ] Test both happy path and error cases
- [ ] Use fixtures for common setup
- [ ] Add to appropriate test class
- [ ] Update test count in documentation
- [ ] Verify test passes locally
- [ ] Check coverage impact

## Troubleshooting

### Import Errors
```python
# Ensure path is correct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components" / "floorplan"))
```

### Async Test Issues
```python
# Use @pytest.mark.asyncio decorator
# Ensure pytest-asyncio installed
# Set asyncio_mode = auto in pytest.ini
```

### Mock Issues
```python
# Use correct spec
hass = MagicMock(spec=HomeAssistant)

# Return values for mocks
mock.return_value = expected_value

# Side effects for complex behavior
mock.side_effect = [1, 2, 3]  # Returns 1, 2, 3 on successive calls
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Home Assistant Testing Guide](https://developers.home-assistant.io/docs/testing/)
- [Trilateration Algorithm](https://en.wikipedia.org/wiki/Trilateration)

## Test Metrics

Current test suite:
- **Total Tests**: 80+
- **Coverage**: Target 85%+
- **Test Files**: 5
- **Execution Time**: <10 seconds

Test breakdown:
- Unit tests: ~75 (FloorplanManager, constants, utilities)
- Integration tests: ~5 (Config flow, provider integration)
- Algorithm tests: ~15 (Trilateration, distance calculations)
