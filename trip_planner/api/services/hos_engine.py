from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple


class DutyStatus:
    OFF_DUTY = "OFF_DUTY"
    SLEEPER_BERTH = "SLEEPER_BERTH"  # Unused per assessment assumptions
    DRIVING = "DRIVING"
    ON_DUTY_NOT_DRIVING = "ON_DUTY_NOT_DRIVING"


class DutySegment:

    def __init__(self, status: str, start_time: datetime, end_time: datetime, location: str = ""):
        self.status = status
        self.start_time = start_time
        self.end_time = end_time
        self.location = location

    @property
    def duration_hours(self) -> float:
        """Returns the segment duration in decimal hours."""
        return (self.end_time - self.start_time).total_seconds() / 3600.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_hours": round(self.duration_hours, 2),
            "location": self.location,
        }

    def __repr__(self):
        return f"<DutySegment {self.status} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')} ({self.duration_hours:.2f}h) @ {self.location}>"


class HOSEngine:

    def __init__(self, initial_cycle_used: float = 0.0, start_time: datetime = None):
        self.initial_cycle_used = float(initial_cycle_used)
        if start_time is None:
            now = datetime.now()
            self.start_time = datetime(now.year, now.month, now.day, 6, 0, 0)
        else:
            self.start_time = start_time

    def simulate_trip(
        self,
        route_segments: List[Dict[str, Any]],
        fixed_events: List[Dict[str, Any]] = None
    ) -> List[DutySegment]:
        fixed_events = fixed_events or []
        timeline: List[DutySegment] = []

        current_time = self.start_time
        cumulative_drive_since_break = 0.0
        drive_hours_used_in_window = 0.0
        window_elapsed = 0.0
        cycle_hours_used = self.initial_cycle_used

        def advance_time(status: str, duration_hours: float, location: str) -> DutySegment:
            nonlocal current_time
            end_t = current_time + timedelta(hours=duration_hours)
            segment = DutySegment(status, current_time, end_t, location)
            current_time = end_t
            return segment

        pickup_event = next((e for e in fixed_events if e.get("type") == "pickup"), None)
        if pickup_event:
            p_dur = pickup_event.get("duration_hours", 1.0)
            p_loc = pickup_event.get("location", "Pickup Location")
            
            if cycle_hours_used >= 70.0:
                seg = advance_time(DutyStatus.OFF_DUTY, 34.0, p_loc)
                timeline.append(seg)
                cycle_hours_used = 0.0
                window_elapsed = 0.0
                drive_hours_used_in_window = 0.0
                cumulative_drive_since_break = 0.0

            seg = advance_time(DutyStatus.ON_DUTY_NOT_DRIVING, p_dur, p_loc)
            timeline.append(seg)
            window_elapsed += p_dur
            cycle_hours_used += p_dur

        total_drive_needed = sum(s.get("duration_hours", 0.0) for s in route_segments)
        remaining_drive_needed = total_drive_needed

        fuel_events = [e for e in fixed_events if e.get("type") == "fuel"]
        next_fuel_index = 0

        current_location = route_segments[0].get("location", "Origin") if route_segments else "Origin"
        cumulative_miles = 0.0

        while remaining_drive_needed > 1e-4:
            if cycle_hours_used >= 70.0:
                seg = advance_time(DutyStatus.OFF_DUTY, 34.0, f"{current_location} (34-hr Restart)")
                timeline.append(seg)
                cycle_hours_used = 0.0
                window_elapsed = 0.0
                drive_hours_used_in_window = 0.0
                cumulative_drive_since_break = 0.0
                continue

            if window_elapsed >= 14.0 or drive_hours_used_in_window >= 11.0:
                seg = advance_time(DutyStatus.OFF_DUTY, 10.0, f"{current_location} (10-hr Reset)")
                timeline.append(seg)
                window_elapsed = 0.0
                drive_hours_used_in_window = 0.0
                cumulative_drive_since_break = 0.0
                continue

            if cumulative_drive_since_break >= 8.0:
                break_dur = 0.5
                seg = advance_time(DutyStatus.ON_DUTY_NOT_DRIVING, break_dur, f"{current_location} (30-min Rest Break)")
                timeline.append(seg)
                cumulative_drive_since_break = 0.0
                window_elapsed += break_dur
                cycle_hours_used += break_dur
                continue

            max_drive_step = min(
                remaining_drive_needed,
                11.0 - drive_hours_used_in_window,
                14.0 - window_elapsed,
                8.0 - cumulative_drive_since_break
            )

            if next_fuel_index < len(fuel_events):
                fuel_evt = fuel_events[next_fuel_index]
                target_fuel_mile = fuel_evt.get("at_mile", 1000.0)
                miles_to_fuel = target_fuel_mile - cumulative_miles
                
                if miles_to_fuel > 0:
                    avg_speed = 60.0  # mph
                    time_to_fuel = miles_to_fuel / avg_speed
                    if time_to_fuel < max_drive_step:
                        max_drive_step = time_to_fuel

            if max_drive_step > 1e-4:
                seg = advance_time(DutyStatus.DRIVING, max_drive_step, f"En route near {current_location}")
                timeline.append(seg)

                cumulative_drive_since_break += max_drive_step
                drive_hours_used_in_window += max_drive_step
                window_elapsed += max_drive_step
                cycle_hours_used += max_drive_step
                remaining_drive_needed -= max_drive_step

                driven_miles = max_drive_step * 60.0  # approx 60 mph average
                cumulative_miles += driven_miles

                if next_fuel_index < len(fuel_events):
                    fuel_evt = fuel_events[next_fuel_index]
                    if cumulative_miles >= fuel_evt.get("at_mile", 1000.0) - 1.0:
                        f_dur = fuel_evt.get("duration_hours", 0.5)
                        f_loc = fuel_evt.get("location", f"Fuel Stop @ Mi {int(cumulative_miles)}")
                        f_seg = advance_time(DutyStatus.ON_DUTY_NOT_DRIVING, f_dur, f_loc)
                        timeline.append(f_seg)

                        window_elapsed += f_dur
                        cycle_hours_used += f_dur
                        next_fuel_index += 1

        dropoff_event = next((e for e in fixed_events if e.get("type") == "dropoff"), None)
        if dropoff_event:
            d_dur = dropoff_event.get("duration_hours", 1.0)
            d_loc = dropoff_event.get("location", "Dropoff Location")

            if cycle_hours_used >= 70.0:
                seg = advance_time(DutyStatus.OFF_DUTY, 34.0, d_loc)
                timeline.append(seg)
                cycle_hours_used = 0.0
                window_elapsed = 0.0
                drive_hours_used_in_window = 0.0
                cumulative_drive_since_break = 0.0

            seg = advance_time(DutyStatus.ON_DUTY_NOT_DRIVING, d_dur, d_loc)
            timeline.append(seg)
            window_elapsed += d_dur
            cycle_hours_used += d_dur

        # Process fixed final event: Dropoff
        # dropoff_event = next((e for e in fixed_events if e.get("type") == "dropoff"), None)
        # if dropoff_event:
        #     d_dur = dropoff_event.get("duration_hours", 1.0)
        #     d_loc = dropoff_event.get("location", "Dropoff Location")

        #     if cycle_hours_used >= 70.0:
        #         seg = advance_time(DutyStatus.OFF_DUTY, 34.0, d_loc)
        #         timeline.append(seg)
        #         cycle_hours_used = 0.0
        #         window_elapsed = 0.0
        #         drive_hours_used_in_window = 0.0
        #         cumulative_drive_since_break = 0.0

        #     seg = advance_time(DutyStatus.ON_DUTY_NOT_DRIVING, d_dur, d_loc)
        #     timeline.append(seg)
        #     window_elapsed += d_dur
        #     cycle_hours_used += d_dur

        # # =========================================================================
        # # ADD THIS BLOCK: Fill remaining time of the last day until Midnight (00:00)
        # # =========================================================================
        # next_midnight = datetime(current_time.year, current_time.month, current_time.day) + timedelta(days=1)
        # if current_time < next_midnight:
        #     remaining_hours = (next_midnight - current_time).total_seconds() / 3600.0
        #     if remaining_hours > 0:
        #         pad_seg = advance_time(DutyStatus.OFF_DUTY, remaining_hours, "End of Day (Off Duty)")
        #         timeline.append(pad_seg)
        # # =========================================================================

        return timeline



    @staticmethod
    def split_segments_by_day(segments: List[DutySegment]) -> Dict[str, List[DutySegment]]:
        daily_buckets: Dict[str, List[DutySegment]] = {}

        for seg in segments:
            cur_start = seg.start_time
            end_t = seg.end_time

            while cur_start < end_t:
                day_key = cur_start.strftime("%Y-%m-%d")
                next_midnight = datetime(cur_start.year, cur_start.month, cur_start.day) + timedelta(days=1)

                if end_t <= next_midnight:
                    sub_seg = DutySegment(seg.status, cur_start, end_t, seg.location)
                    daily_buckets.setdefault(day_key, []).append(sub_seg)
                    break
                else:
                    sub_seg = DutySegment(seg.status, cur_start, next_midnight, seg.location)
                    daily_buckets.setdefault(day_key, []).append(sub_seg)
                    cur_start = next_midnight

        return daily_buckets
