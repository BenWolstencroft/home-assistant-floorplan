# Floorplan Integration Tests

Comprehensive test suite for the Home Assistant Floorplan integration.

## Test Organization

```
tests/
├── conftest.py                 # Pytest fixtures and configuration
├── test_floorplan_manager.py   # FloorplanManager unit tests
├── test_bermuda_provider.py    # Bermuda trilateration provider tests
├── test_config_flow.py         # Configuration flow tests
└── test_constants.py           # Constants and configuration tests
```

## Test Coverage

### FloorplanManager Tests (`test_floorplan_manager.py`)
- Configuration loading/saving (YAML I/O)
- Floor management (add, retrieve)
- Room management (add, get by floor, get all)
- Static entity management (add, update, delete, get)
- Beacon node management (add, update, delete, get)
- Data persistence
- Error handling (corrupted YAML)

### Bermuda Provider Tests (`test_bermuda_provider.py`)
- Trilateration algorithm validation
- Distance calculations (2D, 3D)
- Centroid calculation
- Provider initialization
- Home Assistant state integration
- Error handling (insufficient beacons, invalid data)
- Mathematical correctness

### Config Flow Tests (`test_config_flow.py`)
- User configuration step
- Import step
- Provider configuration (enable/disable)
- Entry data structure
- Unique ID handling
- Schema validation

### Constants Tests (`test_constants.py`)
- Constant definitions
- Data structure validation
- Future extensibility (multi-provider support)
- Naming conventions
- Configuration structure

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_floorplan_manager.py
```

### Run specific test
```bash
pytest tests/test_floorplan_manager.py::TestFloorplanManager::test_add_floor
```

### Run with coverage report
```bash
pytest --cov=custom_components/floorplan --cov-report=html
```

### Run with verbose output
```bash
pytest -v
```

### Run async tests
```bash
pytest -m asyncio
```

## Test Fixtures

Common fixtures defined in `conftest.py`:

- **`hass`** - Mock Home Assistant instance
- **`temp_data_dir`** - Temporary directory for test data
- **`sample_floorplan_data`** - Sample floorplan configuration
- **`beacon_positions`** - Standard beacon positions for trilateration tests

## Mocking Home Assistant

Tests use `unittest.mock` to mock Home Assistant components:

```python
# Mock Home Assistant instance
@pytest.fixture
def hass():
    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    return hass
```

## Async Test Pattern

Async functions use `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_load_floorplan(self, manager):
    await manager.async_load_floorplan()
    assert manager.config_file.exists()
```

## Testing Trilateration

Trilateration tests validate:
- Correct distance calculations using Euclidean distance formula
- Least-squares algorithm convergence
- Centroid calculations
- Residual error computation
- Handling of edge cases (insufficient beacons, invalid data)

Example test:
```python
def test_distance_calculation(self):
    """Test Euclidean distance calculation."""
    p1 = [0, 0, 0]
    p2 = [3, 4, 0]
    distance = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)
    assert distance == 5.0
```

## Configuration Testing

Configuration tests validate:
- YAML parsing and serialization
- Configuration structure
- Provider configuration
- Default values
- Future extensibility

## CI/CD Integration

Tests are run automatically by GitHub Actions:
- **On push**: All tests run
- **On PR**: All tests run with coverage report
- **Coverage**: Minimum 80% required

See `.github/workflows/validate.yml` for CI configuration.

## Adding New Tests

1. Create test file following naming convention: `test_*.py`
2. Use fixtures from `conftest.py`
3. Follow AAA pattern (Arrange, Act, Assert)
4. Use descriptive test names
5. Add docstrings explaining what is tested

Example:
```python
def test_add_floor(self, manager):
    """Test adding a floor."""
    # Arrange
    floor_id = "ground_floor"
    height = 0
    
    # Act
    manager.add_floor(floor_id, height)
    
    # Assert
    assert floor_id in manager.floorplan_data["floors"]
```

## Debugging Tests

### Run with print output
```bash
pytest -s
```

### Run with debugger
```bash
pytest --pdb
```

### Run with detailed traceback
```bash
pytest --tb=long
```

## Test Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should clearly describe what they test
3. **Speed**: Keep tests fast (mock I/O, use fixtures)
4. **Completeness**: Test both happy path and error cases
5. **Maintainability**: Keep tests simple and focused

## Known Limitations

- Some Home Assistant integrations are complex to mock
- Trilateration algorithm convergence is numerical (allow small tolerances)
- Async/await patterns require special pytest configuration

## Future Test Improvements

- [ ] Integration tests with real Home Assistant instance
- [ ] Performance benchmarks for trilateration
- [ ] Flaky test detection
- [ ] Test coverage dashboard
- [ ] Mutation testing
