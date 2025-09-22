"""Standalone test for the FlightRadar24 API without Home Assistant dependencies."""
import json
import math
import requests


class FlightRadar24API:
    """FlightRadar24 API client - standalone version for testing."""

    def __init__(self) -> None:
        """Initialize the API client."""
        self.base_url = "https://data-live.flightradar24.com/zones/fcgi/feed.js"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the distance between two points in metres using Haversine formula."""
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in metres
        r = 6371000
        
        return c * r

    def _get_bounding_box(self, lat: float, lon: float, distance_m: float) -> dict:
        """Calculate bounding box for the given distance."""
        # Approximate degrees per meter (varies by latitude)
        lat_deg_per_m = 1 / 111111
        lon_deg_per_m = 1 / (111111 * math.cos(math.radians(lat)))
        
        lat_offset = distance_m * lat_deg_per_m
        lon_offset = distance_m * lon_deg_per_m
        
        return {
            "tl_y": lat + lat_offset,  # North
            "tl_x": lon - lon_offset,  # West
            "br_y": lat - lat_offset,  # South
            "br_x": lon + lon_offset,  # East
        }

    def get_flights_overhead(self, latitude: float, longitude: float, distance_m: float) -> dict:
        """Get flights within the specified distance from the given coordinates."""
        try:
            # Calculate bounding box
            bbox = self._get_bounding_box(latitude, longitude, distance_m)
            
            # Make API request
            params = {
                "bounds": f"{bbox['tl_y']:.6f},{bbox['br_y']:.6f},{bbox['tl_x']:.6f},{bbox['br_x']:.6f}",
                "faa": "1",
                "satellite": "1",
                "mlat": "1",
                "flarm": "1",
                "adsb": "1",
                "gnd": "1",
                "air": "1",
                "vehicles": "1",
                "estimated": "1",
                "maxage": "14400",
                "gliders": "1",
                "stats": "1"
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter flights by exact distance
            flights_overhead = {}
            
            for flight_id, flight_data in data.items():
                # Skip non-flight data (like "full_count", "version", etc.)
                if not isinstance(flight_data, list) or len(flight_data) < 8:
                    continue
                
                try:
                    flight_lat = float(flight_data[1])
                    flight_lon = float(flight_data[2])
                    
                    # Calculate exact distance
                    distance = self._calculate_distance(latitude, longitude, flight_lat, flight_lon)
                    
                    if distance <= distance_m:
                        flights_overhead[flight_id] = {
                            "flight_id": flight_id,
                            "callsign": flight_data[16] if len(flight_data) > 16 else "Unknown",
                            "latitude": flight_lat,
                            "longitude": flight_lon,
                            "altitude": flight_data[4] if len(flight_data) > 4 else 0,
                            "speed": flight_data[5] if len(flight_data) > 5 else 0,
                            "heading": flight_data[3] if len(flight_data) > 3 else 0,
                            "distance_m": round(distance, 2),
                            "aircraft": flight_data[8] if len(flight_data) > 8 else "Unknown",
                            "origin": flight_data[11] if len(flight_data) > 11 else "Unknown",
                            "destination": flight_data[12] if len(flight_data) > 12 else "Unknown",
                        }
                except (ValueError, IndexError) as e:
                    print(f"Error processing flight data for {flight_id}: {e}")
                    continue
            
            return {
                "flights": flights_overhead,
                "count": len(flights_overhead),
                "search_center": {"latitude": latitude, "longitude": longitude},
                "search_radius_m": distance_m,
            }
            
        except requests.RequestException as e:
            print(f"Error fetching flight data: {e}")
            return {"flights": {}, "count": 0, "error": str(e)}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"flights": {}, "count": 0, "error": str(e)}


def test_api():
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
            for i, (flight_id, flight_info) in enumerate(flights.items()):
                if i >= 5:  # Show first 5
                    break
                print(f"  {flight_info.get('callsign', 'Unknown')} - "
                      f"{flight_info.get('distance_m', 0):.0f}m away, "
                      f"{flight_info.get('altitude', 0)}ft altitude")
        
        return result
        
    except Exception as e:
        print(f"Error testing API: {e}")
        return None


if __name__ == "__main__":
    test_api()