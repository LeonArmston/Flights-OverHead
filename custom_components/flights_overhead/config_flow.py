"""Config flow for Flights OverHead integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_DISTANCE_METRES, DEFAULT_DISTANCE_METRES

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_LATITUDE): cv.latitude,
        vol.Required(CONF_LONGITUDE): cv.longitude,
        vol.Optional(CONF_DISTANCE_METRES, default=DEFAULT_DISTANCE_METRES): vol.All(
            vol.Coerce(int), vol.Range(min=100, max=100000)
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # For this integration, we just need to validate that the coordinates are reasonable
    # The distance is already validated by the schema
    return {"title": f"Flights OverHead ({data[CONF_DISTANCE_METRES]}m radius)"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Flights OverHead."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            # Pre-fill with Home Assistant's configured location if available
            default_data = {}
            if self.hass.config.latitude:
                default_data[CONF_LATITUDE] = self.hass.config.latitude
            if self.hass.config.longitude:
                default_data[CONF_LONGITUDE] = self.hass.config.longitude
            
            schema = STEP_USER_DATA_SCHEMA
            if default_data:
                schema = vol.Schema(
                    {
                        vol.Required(CONF_LATITUDE, default=default_data.get(CONF_LATITUDE)): cv.latitude,
                        vol.Required(CONF_LONGITUDE, default=default_data.get(CONF_LONGITUDE)): cv.longitude,
                        vol.Optional(CONF_DISTANCE_METRES, default=DEFAULT_DISTANCE_METRES): vol.All(
                            vol.Coerce(int), vol.Range(min=100, max=100000)
                        ),
                    }
                )
            
            return self.async_show_form(
                step_id="user", data_schema=schema
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )