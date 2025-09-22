"""Sensor platform for Flights OverHead integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Create sensors
    entities = [
        FlightsOverheadCountSensor(coordinator, config_entry),
        FlightsOverheadDetailSensor(coordinator, config_entry),
    ]
    
    async_add_entities(entities)


class FlightsOverheadCountSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing the count of flights overhead."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_name = "Flights Overhead Count"
        self._attr_unique_id = f"{config_entry.entry_id}_count"
        self._attr_icon = "mdi:airplane"
        self._attr_native_unit_of_measurement = "flights"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("count", 0)
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        data = self.coordinator.data
        attributes = {
            "search_center_latitude": data.get("search_center", {}).get("latitude"),
            "search_center_longitude": data.get("search_center", {}).get("longitude"),
            "search_radius_m": data.get("search_radius_m"),
            "last_updated": self.coordinator.last_update_success_time,
        }
        
        # Add error info if available
        if "error" in data:
            attributes["error"] = data["error"]
        
        return attributes


class FlightsOverheadDetailSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing detailed flight information."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_name = "Flights Overhead Details"
        self._attr_unique_id = f"{config_entry.entry_id}_details"
        self._attr_icon = "mdi:airplane-takeoff"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self.coordinator.data:
            count = self.coordinator.data.get("count", 0)
            return f"{count} flights detected"
        return "No data"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return detailed flight information as attributes."""
        if not self.coordinator.data:
            return {}
        
        data = self.coordinator.data
        flights = data.get("flights", {})
        
        attributes = {
            "flight_count": data.get("count", 0),
            "search_radius_m": data.get("search_radius_m"),
            "flights": [],
        }
        
        # Add individual flight details
        for flight_id, flight_info in flights.items():
            flight_details = {
                "flight_id": flight_id,
                "callsign": flight_info.get("callsign", "Unknown"),
                "altitude": flight_info.get("altitude", 0),
                "speed": flight_info.get("speed", 0),
                "heading": flight_info.get("heading", 0),
                "distance_m": flight_info.get("distance_m", 0),
                "aircraft": flight_info.get("aircraft", "Unknown"),
                "origin": flight_info.get("origin", "Unknown"),
                "destination": flight_info.get("destination", "Unknown"),
                "latitude": flight_info.get("latitude"),
                "longitude": flight_info.get("longitude"),
            }
            attributes["flights"].append(flight_details)
        
        # Sort flights by distance (closest first)
        attributes["flights"].sort(key=lambda x: x.get("distance_m", 0))
        
        # Add closest flight info for easy access
        if attributes["flights"]:
            closest_flight = attributes["flights"][0]
            attributes["closest_flight_callsign"] = closest_flight["callsign"]
            attributes["closest_flight_distance_m"] = closest_flight["distance_m"]
            attributes["closest_flight_altitude"] = closest_flight["altitude"]
        
        return attributes