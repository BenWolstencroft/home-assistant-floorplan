"""Config flow for Floorplan integration."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_PROVIDERS, CONF_ENABLE_BERMUDA

_LOGGER = logging.getLogger(__name__)


class FloorplanConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Floorplan."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Floorplan",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional(CONF_ENABLE_BERMUDA, default=True): bool,
            }),
            description_placeholders={
                "setup_hint": "Configure your floorplan via YAML in the Floorplan data directory. "
                "Select which location providers to enable below."
            },
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> FlowResult:
        """Handle import from YAML."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        # Extract provider settings from YAML config if present
        providers_config = import_data.get(CONF_PROVIDERS, {})
        enable_bermuda = providers_config.get(CONF_ENABLE_BERMUDA, True)

        return self.async_create_entry(
            title="Floorplan",
            data={
                CONF_ENABLE_BERMUDA: enable_bermuda,
            },
        )
