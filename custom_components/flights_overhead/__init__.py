"""The Flights OverHead integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .api import FlightRadar24API

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Flights OverHead from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Create API instance
    api = FlightRadar24API()
    
    # Create coordinator
    coordinator = FlightsOverheadCoordinator(hass, api, entry.data)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


class FlightsOverheadCoordinator(DataUpdateCoordinator):
    """Class to manage fetching flights data from the API."""

    def __init__(self, hass: HomeAssistant, api: FlightRadar24API, config: dict) -> None:
        """Initialize."""
        self.api = api
        self.config = config
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self) -> dict:
        """Update data via library."""
        latitude = self.config.get("latitude")
        longitude = self.config.get("longitude")
        distance_m = self.config.get("distance_metres", 10000)  # Default 10km
        
        return await self.hass.async_add_executor_job(
            self.api.get_flights_overhead,
            latitude,
            longitude,
            distance_m
        )