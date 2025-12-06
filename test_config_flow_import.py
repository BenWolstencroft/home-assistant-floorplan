"""Quick test to verify config flow can be imported."""
import sys
from pathlib import Path

# Add custom_components to path
sys.path.insert(0, str(Path(__file__).parent / "custom_components"))

try:
    from floorplan.config_flow import FloorplanConfigFlow
    from floorplan.const import DOMAIN
    
    print("✓ Import successful")
    print(f"✓ Domain constant: {DOMAIN}")
    print(f"✓ Config flow class: {FloorplanConfigFlow}")
    print(f"✓ Config flow domain attribute: {FloorplanConfigFlow.__dict__.get('domain', 'NOT FOUND')}")
    print(f"✓ Config flow VERSION: {FloorplanConfigFlow.VERSION}")
    
    # Check if it's a proper ConfigFlow subclass
    from homeassistant import config_entries
    print(f"✓ Is ConfigFlow subclass: {issubclass(FloorplanConfigFlow, config_entries.ConfigFlow)}")
    
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
