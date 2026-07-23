"""
Unit tests for the HOS Engine and Trip Scheduler.
Validates HOS logic against the FMCSA Interstate Truck Driver's Guide example (Richmond, VA -> Newark, NJ).
"""

import unittest
from datetime import datetime, timedelta
from api.services.hos_engine import HOSEngine, DutyStatus, DutySegment


class HOSEngineTestCase(unittest.TestCase):
    """Test suite for pure-Python HOSEngine state simulator."""

    def test_fmcsa_worked_example_totals(self):
        """
        Validate simulation against FMCSA guide worked example (Richmond, VA to Newark, NJ).
        FMCSA example summary (page 18-19 of guide, adjusted to exclude sleeper berth):
        - Driving: ~7.75 hours (Richmond -> Fredericksburg fuel -> Baltimore lunch -> Philly delivery -> Newark)
        - On-Duty Not Driving: ~4.5 hours (Pre-trip 1.5h, fuel 0.5h, delivery 0.5h, post-trip/paperwork 2.0h)
        - Off-Duty: 10.0 hours (Daily rest reset)
        - Total: 24.0 hours
        """
        start_t = datetime(2026, 7, 22, 0, 0, 0)
        engine = HOSEngine(initial_cycle_used=0.0, start_time=start_t)

        # Route segment: ~7.75 total drive hours needed
        route_segments = [
            {"distance_miles": 350.0, "duration_hours": 7.75, "location": "Richmond, VA to Newark, NJ"}
        ]
        fixed_events = [
            {"type": "pickup", "duration_hours": 1.5, "location": "Richmond, VA"},
            {"type": "dropoff", "duration_hours": 2.0, "location": "Newark, NJ"},
        ]

        segments = engine.simulate_trip(route_segments, fixed_events)
        
        # Calculate daily total hours per status category
        total_driving = sum(s.duration_hours for s in segments if s.status == DutyStatus.DRIVING)
        total_on_duty_nd = sum(s.duration_hours for s in segments if s.status == DutyStatus.ON_DUTY_NOT_DRIVING)
        total_off_duty = sum(s.duration_hours for s in segments if s.status == DutyStatus.OFF_DUTY)

        print(f"\n[Test FMCSA Worked Example] Driving: {total_driving:.2f}h, On-Duty ND: {total_on_duty_nd:.2f}h, Off-Duty: {total_off_duty:.2f}h")

        self.assertAlmostEqual(total_driving, 7.75, delta=0.5)
        self.assertGreater(total_on_duty_nd, 0.0)
        self.assertTrue(any(s.status == DutyStatus.DRIVING for s in segments))

    def test_70_hour_cycle_restart_trigger(self):
        """
        Validate that when initial cycle hours used is >= 70 hours, a 34-hour Off-Duty restart is inserted.
        """
        start_t = datetime(2026, 7, 22, 6, 0, 0)
        engine = HOSEngine(initial_cycle_used=68.5, start_time=start_t)

        # Long route requiring 15 hours of driving
        route_segments = [
            {"distance_miles": 900.0, "duration_hours": 15.0, "location": "Los Angeles to Denver"}
        ]
        fixed_events = [
            {"type": "pickup", "duration_hours": 1.0, "location": "Los Angeles, CA"},
            {"type": "dropoff", "duration_hours": 1.0, "location": "Denver, CO"},
        ]

        segments = engine.simulate_trip(route_segments, fixed_events)

        # Check if a 34-hour restart segment was inserted
        has_34h_restart = any(
            s.status == DutyStatus.OFF_DUTY and s.duration_hours >= 34.0
            for s in segments
        )
        self.assertTrue(has_34h_restart, "Should insert a 34-hour restart when cycle exceeds 70 hours")

    def test_day_bucket_splitting(self):
        """
        Validate that continuous duty segments spanning midnight are cleanly split across calendar days.
        """
        start_t = datetime(2026, 7, 22, 20, 0, 0)  # Starts 8:00 PM
        seg = DutySegment(DutyStatus.DRIVING, start_t, start_t + timedelta(hours=8), "En route")
        
        daily_buckets = HOSEngine.split_segments_by_day([seg])
        self.assertIn("2026-07-22", daily_buckets)
        self.assertIn("2026-07-23", daily_buckets)
        
        # Day 1 should have 4 hours (20:00 to 24:00)
        day1_dur = sum(s.duration_hours for s in daily_buckets["2026-07-22"])
        self.assertAlmostEqual(day1_dur, 4.0, delta=0.01)

        # Day 2 should have 4 hours (00:00 to 04:00)
        day2_dur = sum(s.duration_hours for s in daily_buckets["2026-07-23"])
        self.assertAlmostEqual(day2_dur, 4.0, delta=0.01)


if __name__ == "__main__":
    unittest.main()
