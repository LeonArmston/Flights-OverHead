# Flights OverHead - Home Assistant Integration

A Home Assistant integration that uses the unofficial FlightRadar24 API to track flights overhead within a configurable distance radius in metres.

## Features

- 🛩️ Track flights within a specified radius (100m to 100km)
- 📍 Uses your Home Assistant location or custom coordinates  
- 🔢 Two sensors: flight count and detailed flight information
- 📊 Rich attributes including callsign, altitude, speed, distance, aircraft type, origin/destination
- ⚡ Updates every minute
- 🎯 Distance-based filtering with precise Haversine distance calculation

## Installation

### Manual Installation

1. Create a `custom_components` directory in your Home Assistant configuration directory if it doesn't exist
2. Copy the `flights_overhead` folder to `custom_components/flights_overhead`
3. Restart Home Assistant
4. Go to Configuration → Integrations → Add Integration
5. Search for "Flights OverHead" and configure it

### Configuration

During setup, you'll need to provide:

- **Latitude**: Your search center latitude (defaults to HA location)
- **Longitude**: Your search center longitude (defaults to HA location) 
- **Distance (metres)**: Search radius from 100m to 100km (default: 10km)

## Sensors

The integration creates two sensors:

### 1. Flights Overhead Count
- **Entity ID**: `sensor.flights_overhead_count`
- **State**: Number of flights detected
- **Unit**: flights
- **Icon**: mdi:airplane

**Attributes:**
- `search_center_latitude`: Search center latitude
- `search_center_longitude`: Search center longitude  
- `search_radius_m`: Search radius in metres
- `last_updated`: Last successful update time

### 2. Flights Overhead Details  
- **Entity ID**: `sensor.flights_overhead_details`
- **State**: Text summary (e.g., "3 flights detected")
- **Icon**: mdi:airplane-takeoff

**Attributes:**
- `flight_count`: Total number of flights
- `search_radius_m`: Search radius in metres
- `flights`: Array of flight objects with detailed information
- `closest_flight_callsign`: Callsign of the closest flight
- `closest_flight_distance_m`: Distance to closest flight in metres
- `closest_flight_altitude`: Altitude of closest flight

**Flight Object Structure:**
```yaml
flight_id: "ABC123"
callsign: "UAL123" 
altitude: 35000 # feet
speed: 450 # knots
heading: 180 # degrees
distance_m: 5432.1 # metres from search center
aircraft: "B738" # aircraft type
origin: "KJFK" # departure airport
destination: "KLAX" # arrival airport  
latitude: 40.7128
longitude: -74.0060
```

## Example Automations

### Flight Notification
```yaml
automation:
  - alias: "Notify when flights overhead"
    trigger:
      - platform: numeric_state
        entity_id: sensor.flights_overhead_count
        above: 0
    action:
      - service: notify.mobile_app_your_phone
        data:
          message: >
            {{ states('sensor.flights_overhead_count') }} flights overhead! 
            Closest: {{ state_attr('sensor.flights_overhead_details', 'closest_flight_callsign') }}
            at {{ state_attr('sensor.flights_overhead_details', 'closest_flight_distance_m') }}m
```

### Low Flying Aircraft Alert
```yaml
automation:
  - alias: "Low flying aircraft alert"
    trigger:
      - platform: state
        entity_id: sensor.flights_overhead_details
    condition:
      - condition: template
        value_template: >
          {% for flight in state_attr('sensor.flights_overhead_details', 'flights') %}
            {% if flight.altitude < 5000 %}
              true
            {% endif %}
          {% endfor %}
    action:
      - service: notify.home_assistant
        data:
          message: "Low flying aircraft detected!"
```

## Dashboard Card Example

```yaml
type: entities
title: Flights Overhead
entities:
  - entity: sensor.flights_overhead_count
    name: Active Flights
  - type: attribute
    entity: sensor.flights_overhead_details
    attribute: closest_flight_callsign
    name: Closest Flight
  - type: attribute  
    entity: sensor.flights_overhead_details
    attribute: closest_flight_distance_m
    name: Distance (m)
    suffix: m
```

## Troubleshooting

### No Flights Detected
- Verify your coordinates are correct
- Check if your area has regular air traffic
- Try increasing the search radius
- Ensure you have internet connectivity

### API Errors
- The integration uses the unofficial FlightRadar24 API which may have rate limits
- Check Home Assistant logs for specific error messages
- Consider increasing the update interval if you encounter rate limiting

## Technical Details

- **Data Source**: FlightRadar24 unofficial API
- **Update Interval**: 60 seconds
- **Distance Calculation**: Haversine formula for accurate Earth distance
- **Coordinate System**: WGS84 (standard GPS coordinates)
- **API Timeout**: 30 seconds

## Contributing

Feel free to submit issues and enhancement requests on [GitHub](https://github.com/LeonArmston/Flights-OverHead).

## License

This project is licensed under the MIT License.

## Disclaimer

This integration uses an unofficial API and is not affiliated with FlightRadar24. Use at your own discretion and be respectful of API limits.
