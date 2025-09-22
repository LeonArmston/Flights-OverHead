"""Example script to test the FlightRadar24 API."""
import asyncio
import json
from custom_components.flights_overhead.api import FlightRadar24API


async def test_api():
    """Test the API with example coordinates."""
    api = FlightRadar24API()
    
    # Example coordinates (London, UK)
    latitude = 51.5074
    longitude = -0.1278
    distance_m = 20000  # 20km radius
    
    print(f"Testing FlightRadar24 API...")
    print(f"Location: {latitude}, {longitude}")
    print(f"Search radius: {distance_m}m")
    print("-" * 50)
    
    try:
        result = api.get_flights_overhead(latitude, longitude, distance_m)
        
        print(f"Flights found: {result.get('count', 0)}")
        print(f"Search center: {result.get('search_center')}")
        print(f"Search radius: {result.get('search_radius_m')}m")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
        
        flights = result.get('flights', {})
        if flights:
            print("\nFlight details:")
            for flight_id, flight_info in list(flights.items())[:5]:  # Show first 5
                print(f"  {flight_info.get('callsign', 'Unknown')} - "
                      f"{flight_info.get('distance_m', 0):.0f}m away, "
                      f"{flight_info.get('altitude', 0)}ft altitude")
        
        return result
        
    except Exception as e:
        print(f"Error testing API: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(test_api())