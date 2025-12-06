"""Root conftest for mocking Home Assistant imports in tests."""

import sys
from unittest.mock import MagicMock, AsyncMock

# CRITICAL: Mock Home Assistant modules BEFORE any other imports
# This must run first, before pytest discovers any test modules

def _create_mock_module(name):
    """Create a mock module with __getattr__ to handle sub-module access."""
    mock = MagicMock()
    sys.modules[name] = mock
    return mock

# Create all the HA module mocks
ha_modules = [
    "homeassistant",
    "homeassistant.const",
    "homeassistant.core",
    "homeassistant.helpers",
    "homeassistant.helpers.config_validation",
    "homeassistant.helpers.entity_registry",
    "homeassistant.helpers.floor_registry",
    "homeassistant.helpers.typing",
    "homeassistant.components",
    "homeassistant.components.bluetooth",
    "homeassistant.setup",
    "homeassistant.config_entries",
    "homeassistant.data_entry_flow",
    "homeassistant.loader",
]

for module_name in ha_modules:
    _create_mock_module(module_name)

# Set up commonly accessed attributes
sys.modules["homeassistant.const"].Platform = MagicMock()
sys.modules["homeassistant.const"].CONF_ENTITY_ID = "entity_id"
sys.modules["homeassistant.const"].CONF_NAME = "name"

sys.modules["homeassistant.core"].HomeAssistant = MagicMock
sys.modules["homeassistant.core"].State = MagicMock
sys.modules["homeassistant.core"].Context = MagicMock
sys.modules["homeassistant.core"].EVENT_STATE_CHANGED = "state_changed"

sys.modules["homeassistant.helpers"].ConfigType = dict
sys.modules["homeassistant.helpers"].HomeAssistantType = MagicMock
sys.modules["homeassistant.helpers.config_validation"].Required = MagicMock
sys.modules["homeassistant.helpers.config_validation"].Optional = MagicMock
sys.modules["homeassistant.helpers.config_validation"].All = MagicMock
sys.modules["homeassistant.helpers.config_validation"].schema_with_slug_keys = lambda x: x

sys.modules["homeassistant.helpers.floor_registry"].FloorRegistry = MagicMock
sys.modules["homeassistant.helpers.entity_registry"].EntityRegistry = MagicMock
sys.modules["homeassistant.helpers.typing"].HomeAssistantType = MagicMock

# Mock Bluetooth device retrieval function with test devices
def mock_async_get_bluetooth_devices(hass):
    """Mock function to return test Bluetooth devices."""
    return {
        "D4:5F:4E:A1:23:45": MagicMock(address="D4:5F:4E:A1:23:45"),
        "A3:2B:1C:F9:87:56": MagicMock(address="A3:2B:1C:F9:87:56"),
        "F1:E2:D3:C4:B5:A6": MagicMock(address="F1:E2:D3:C4:B5:A6"),
        "beacon_1": MagicMock(address="beacon_1"),
        "beacon_2": MagicMock(address="beacon_2"),
        "beacon_3": MagicMock(address="beacon_3"),
    }

sys.modules["homeassistant.components.bluetooth"].async_get_bluetooth_devices = \
    mock_async_get_bluetooth_devices

sys.modules["homeassistant.config_entries"].ConfigEntry = MagicMock
sys.modules["homeassistant.config_entries"].OptionsFlow = MagicMock
sys.modules["homeassistant.config_entries"].ConfigFlowContext = MagicMock

# Create a proper base class for ConfigFlow that can be inherited
class MockConfigFlow:
    """Mock base ConfigFlow class."""
    def __init__(self):
        pass
    
    async def async_set_unique_id(self, unique_id):
        """Mock async_set_unique_id."""
        pass
    
    def _abort_if_unique_id_configured(self):
        """Mock _abort_if_unique_id_configured."""
        pass
    
    def async_create_entry(self, title, data):
        """Mock async_create_entry."""
        return {"type": "create_entry", "title": title, "data": data}
    
    def async_show_form(self, step_id, data_schema, description_placeholders=None):
        """Mock async_show_form."""
        return {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
            "description_placeholders": description_placeholders,
        }

sys.modules["homeassistant.config_entries"].ConfigFlow = MockConfigFlow

sys.modules["homeassistant.data_entry_flow"].FlowHandler = MagicMock
