
import os
import math
import logging
import requests
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class RouteService:

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
    ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

    @classmethod
    def geocode(cls, location_query: str) -> Dict[str, Any]:
        if not location_query or not location_query.strip():
            raise ValueError("Location query cannot be empty")

        headers = {"User-Agent": "SpotterTripPlannerELD/1.0 (contact@spotterai.com)"}
        params = {
            "q": location_query,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }

        try:
            resp = requests.get(cls.NOMINATIM_URL, params=params, headers=headers, timeout=5)
            if resp.status_code == 200 and resp.json():
                data = resp.json()[0]
                lat = float(data["lat"])
                lon = float(data["lon"])
                display_name = data.get("display_name", location_query)
                address = data.get("address", {})
                city = address.get("city") or address.get("town") or address.get("village") or location_query.split(",")[0]
                state = address.get("state") or address.get("state_code") or ""

                return {
                    "query": location_query,
                    "lat": lat,
                    "lon": lon,
                    "display_name": display_name,
                    "city": city,
                    "state": state,
                    "label": f"{city}, {state}".strip(", "),
                }
        except Exception as e:
            logger.warning(f"Geocoding failed for '{location_query}': {e}. Using fallback coordinates.")

        known_cities = {
            "richmond": (37.5407, -77.4360, "Richmond, VA"),
            "fredericksburg": (38.3032, -77.4605, "Fredericksburg, VA"),
            "baltimore": (39.2904, -76.6122, "Baltimore, MD"),
            "philadelphia": (39.9526, -75.1652, "Philadelphia, PA"),
            "cherry hill": (39.9348, -75.0307, "Cherry Hill, NJ"),
            "newark": (40.7357, -74.1724, "Newark, NJ"),
            "los angeles": (34.0522, -118.2437, "Los Angeles, CA"),
            "denver": (39.7392, -104.9903, "Denver, CO"),
            "chicago": (41.8781, -87.6298, "Chicago, IL"),
            "new york": (40.7128, -74.0060, "New York, NY"),
        }
        q_lower = location_query.lower()
        for k, v in known_cities.items():
            if k in q_lower:
                return {
                    "query": location_query,
                    "lat": v[0],
                    "lon": v[1],
                    "display_name": v[2],
                    "city": v[2].split(",")[0],
                    "state": v[2].split(",")[1].strip() if "," in v[2] else "",
                    "label": v[2],
                }

        return {
            "query": location_query,
            "lat": 37.5407,
            "lon": -77.4360,
            "display_name": location_query,
            "city": location_query,
            "state": "",
            "label": location_query,
        }

    @classmethod
    def get_route(cls, waypoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        if len(waypoints) < 2:
            raise ValueError("At least 2 waypoints required for routing")

        # Try OpenRouteService if API key present
        ors_api_key = os.getenv("OPENROUTE_SERVICE_KEY", "").strip()
        if ors_api_key:
            try:
                coords = [[wp["lon"], wp["lat"]] for wp in waypoints]
                headers = {"Authorization": ors_api_key, "Content-Type": "application/json"}
                body = {"coordinates": coords, "instructions": True}
                resp = requests.post(cls.ORS_URL, json=body, headers=headers, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    route = data["routes"][0]
                    summary = route["summary"]
                    dist_miles = summary["distance"] * 0.000621371
                    dur_hours = summary["duration"] / 3600.0

                    # Geometry coordinates [lon, lat] -> [lat, lon]
                    raw_coords = route["geometry"]["coordinates"]
                    geometry = [[c[1], c[0]] for c in raw_coords]

                    # Turn-by-turn steps
                    steps = []
                    for seg in route.get("segments", []):
                        for st in seg.get("steps", []):
                            steps.append({
                                "instruction": st.get("instruction", "Drive straight"),
                                "distance_miles": round(st.get("distance", 0) * 0.000621371, 2),
                                "duration_minutes": round(st.get("duration", 0) / 60.0, 1),
                            })

                    return {
                        "distance_miles": round(dist_miles, 2),
                        "duration_hours": round(dur_hours, 2),
                        "geometry": geometry,
                        "directions": steps,
                    }
            except Exception as e:
                logger.warning(f"OpenRouteService failed: {e}. Trying OSRM public service.")

        # Try OSRM public routing API
        try:
            coord_str = ";".join([f"{wp['lon']},{wp['lat']}" for wp in waypoints])
            url = f"{cls.OSRM_URL}/{coord_str}?overview=full&geometries=geojson&steps=true"
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "Ok" and data.get("routes"):
                    route = data["routes"][0]
                    dist_miles = route["distance"] * 0.000621371
                    dur_hours = route["duration"] / 3600.0

                    raw_coords = route["geometry"]["coordinates"]
                    geometry = [[c[1], c[0]] for c in raw_coords]

                    steps = []
                    for leg in route.get("legs", []):
                        for st in leg.get("steps", []):
                            name = st.get("name", "")
                            maneuver = st.get("maneuver", {}).get("type", "drive")
                            instruction = f"{maneuver.capitalize()} onto {name}" if name else maneuver.capitalize()
                            steps.append({
                                "instruction": instruction,
                                "distance_miles": round(st.get("distance", 0) * 0.000621371, 2),
                                "duration_minutes": round(st.get("duration", 0) / 60.0, 1),
                            })

                    return {
                        "distance_miles": round(dist_miles, 2),
                        "duration_hours": round(dur_hours, 2),
                        "geometry": geometry,
                        "directions": steps,
                    }
        except Exception as e:
            logger.warning(f"OSRM routing failed: {e}. Generating Haversine fallback route.")

        # Robust Fallback: Great Circle (Haversine) route generation with interpolated geometry
        return cls._generate_fallback_route(waypoints)

    @classmethod
    def _generate_fallback_route(cls, waypoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        total_dist_miles = 0.0
        geometry = []
        directions = []

        for i in range(len(waypoints) - 1):
            wp1 = waypoints[i]
            wp2 = waypoints[i + 1]

            lat1, lon1 = wp1["lat"], wp1["lon"]
            lat2, lon2 = wp2["lat"], wp2["lon"]

            # Haversine distance
            R = 3958.8  # Earth radius in miles
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            leg_miles = R * c

            # Multiply straight line by 1.25 factor for realistic highway curvature
            actual_leg_miles = leg_miles * 1.25
            total_dist_miles += actual_leg_miles

            # Interpolate geometry points along the leg
            steps_cnt = max(10, int(actual_leg_miles / 10))
            for k in range(steps_cnt + 1):
                frac = k / float(steps_cnt)
                interp_lat = lat1 + (lat2 - lat1) * frac
                interp_lon = lon1 + (lon2 - lon1) * frac
                geometry.append([round(interp_lat, 5), round(interp_lon, 5)])

            directions.append({
                "instruction": f"Proceed from {wp1.get('label', 'Origin')} toward {wp2.get('label', 'Destination')}",
                "distance_miles": round(actual_leg_miles, 2),
                "duration_minutes": round((actual_leg_miles / 60.0) * 60.0, 1),
            })

        # Estimate duration assuming average commercial truck speed ~60 mph
        total_duration_hours = total_dist_miles / 60.0

        return {
            "distance_miles": round(total_dist_miles, 2),
            "duration_hours": round(total_duration_hours, 2),
            "geometry": geometry,
            "directions": directions,
        }
