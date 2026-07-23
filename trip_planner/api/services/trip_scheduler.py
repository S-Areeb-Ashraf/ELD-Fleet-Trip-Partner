"""
Trip Scheduler

Orchestrates geocoding, route calculation, fixed event scheduling (pickup, fuel every 1000 mi, dropoff),
HOS simulation, Leaflet marker geolocation, and daily log generation.
"""

# from asyncio import protocols
from typing import Dict, Any, List
from api.services.route_service import RouteService
from api.services.hos_engine import HOSEngine, DutyStatus
from api.services.log_generator import LogGenerator



class TripScheduler:
    """Orchestrates end-to-end trip planning workflow."""
    # pickup_locs=""
    # dropoff_locs=""
    
    

    @classmethod
    def plan_trip(
        self,
        current_location: str,
        pickup_location: str,
        dropoff_location: str,
        current_cycle_used: float = 0.0
    ) -> Dict[str, Any]:
        """
        Execute full trip planning pipeline.
        
        :param current_location: Driver starting location (e.g., 'Richmond, VA')
        :param pickup_location: Pickup location (e.g., 'Baltimore, MD')
        :param dropoff_location: Final destination (e.g., 'Newark, NJ')
        :param current_cycle_used: Hours already used in 70-hour / 8-day rolling window
        :return: Complete trip payload matching REST API spec
        """
        # Step 1: Geocode locations
        geo_current = RouteService.geocode(current_location)
        geo_pickup = RouteService.geocode(pickup_location)
        geo_dropoff = RouteService.geocode(dropoff_location)
        # pickup_locs = pickup_location
        # dropoff_locs = dropoff_location
        

        waypoints = [geo_current, geo_pickup, geo_dropoff]

        # Step 2: Calculate full route driving stats & geometry
        route_data = RouteService.get_route(waypoints)
        total_distance = route_data["distance_miles"]
        total_duration = route_data["duration_hours"]
        geometry = route_data["geometry"]
        directions = route_data["directions"]

        # Step 3: Build ordered list of fixed events
        # Pickup: 1 hr On Duty Not Driving at trip start
        # Fuel stops: 30 min On Duty Not Driving every 1,000 miles of driving distance
        # Dropoff: 1 hr On Duty Not Driving at trip end
        fixed_events = [
            {
                "type": "pickup",
                "duration_hours": 1.0,
                "location": geo_pickup["label"],
                "at_mile": 0.0,
            }
        ]

        # Schedule fuel stops every 1,000 miles of driving distance
        fuel_stops = []
        fuel_interval = 1000.0
        current_fuel_mile = fuel_interval
        while current_fuel_mile < total_distance:
            # Interpolate geographic coordinate along route for fuel stop marker
            lat_lon = self._interpolate_coords(geometry, current_fuel_mile, total_distance)
            fuel_stop_info = {
                "type": "fuel",
                "duration_hours": 0.5,
                "location": f"Fuel Stop @ Mile {int(current_fuel_mile)}",
                "at_mile": current_fuel_mile,
                "lat": lat_lon[0],
                "lon": lat_lon[1],
            }
            fixed_events.append(fuel_stop_info)
            fuel_stops.append({
                "mile": int(current_fuel_mile),
                "location": fuel_stop_info["location"],
                "duration_minutes": 30,
                "lat": lat_lon[0],
                "lon": lat_lon[1],
            })
            current_fuel_mile += fuel_interval

        fixed_events.append({
            "type": "dropoff",
            "duration_hours": 1.0,
            "location": geo_dropoff["label"],
            "at_mile": total_distance,
        })

        # Step 4: Run HOS Engine simulation
        engine = HOSEngine(initial_cycle_used=current_cycle_used)
        route_drive_segments = [
            {
                "distance_miles": total_distance,
                "duration_hours": total_duration,
                "location": f"Route from {geo_current['label']} to {geo_dropoff['label']}",
            }
        ]
        timeline = engine.simulate_trip(route_drive_segments, fixed_events)

        # Step 5: Extract rest breaks and map markers
        rest_stops = []
        cum_drive = 0.0
        for seg in timeline:
            if seg.status == DutyStatus.OFF_DUTY:
                reason = "34-hr restart" if seg.duration_hours >= 34.0 else "10-hr reset"
                lat_lon = self._interpolate_coords(geometry, cum_drive, total_distance)
                rest_stops.append({
                    "duration_hours": seg.duration_hours,
                    "reason": reason,
                    "location": seg.location,
                    "start_time": seg.start_time.isoformat(),
                    "end_time": seg.end_time.isoformat(),
                    "lat": lat_lon[0],
                    "lon": lat_lon[1],
                })
            elif seg.status == DutyStatus.ON_DUTY_NOT_DRIVING and "Rest Break" in seg.location:
                lat_lon = self._interpolate_coords(geometry, cum_drive, total_distance)
                rest_stops.append({
                    "duration_hours": 0.5,
                    "reason": "30-min break",
                    "location": seg.location,
                    "start_time": seg.start_time.isoformat(),
                    "end_time": seg.end_time.isoformat(),
                    "lat": lat_lon[0],
                    "lon": lat_lon[1],
                })
            elif seg.status == DutyStatus.DRIVING:
                cum_drive += seg.duration_hours * 60.0  # miles driven

        # Step 6: Split continuous timeline into 24-hour day buckets
        daily_buckets = HOSEngine.split_segments_by_day(timeline)

        # Step 7: Generate daily log PNGs using Pillow
        daily_logs = LogGenerator.generate_logs(
            daily_buckets=daily_buckets,
            # geo_current=geo_current,
            total_trip_miles=total_distance,
            carrier_name="Spotter Services",
            main_office="Washington, D.C.",
            home_terminal=geo_current["label"],
            truck_number="T-101 / Tr-502",
            from_location=geo_pickup["label"],   # <--- Pass pickup location
            to_location=geo_dropoff["label"],    # <--- Pass dropoff location
        )

        return {
            "distance": round(total_distance, 2),
            "duration": round(total_duration, 2),
            "waypoints": {
                "current": geo_current,
                "pickup": geo_pickup,
                "dropoff": geo_dropoff,
            },
            "directions": directions,
            "route_geometry": geometry,
            "fuel_stops": fuel_stops,
            "rest_stops": rest_stops,
            "daily_logs": daily_logs,
        }

    @staticmethod
    def _interpolate_coords(geometry: List[List[float]], mile: float, total_miles: float) -> List[float]:
        """Interpolate lat/lon coordinate pair along geometry array at given mile fraction."""
        if not geometry:
            return [37.5407, -77.4360]
        if total_miles <= 0:
            return geometry[0]

        fraction = min(1.0, max(0.0, mile / total_miles))
        index = int(fraction * (len(geometry) - 1))
        return geometry[index]
