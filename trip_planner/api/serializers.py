"""
Django REST Framework Serializers for Trip Planning.
"""

from rest_framework import serializers


class TripPlanRequestSerializer(serializers.Serializer):
    """Input payload serializer for trip planning request."""

    current_location = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Starting location of driver (e.g., 'Richmond, VA')",
    )
    pickup_location = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Pickup location (e.g., 'Baltimore, MD')",
    )
    dropoff_location = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Dropoff / final destination location (e.g., 'Newark, NJ')",
    )
    current_cycle_used = serializers.FloatField(
        required=False,
        default=0.0,
        min_value=0.0,
        max_value=70.0,
        help_text="Hours accumulated in 70-hour / 8-day rolling window before trip start",
    )


class DailyLogSerializer(serializers.Serializer):
    """Serializer for individual daily log sheet metadata."""

    day_number = serializers.IntegerField()
    date = serializers.CharField()
    png_url = serializers.CharField()
    total_driving_hours = serializers.FloatField()
    total_on_duty_hours = serializers.FloatField()
    total_off_duty_hours = serializers.FloatField()
    total_miles_driven = serializers.FloatField()


class TripPlanResponseSerializer(serializers.Serializer):
    """Output payload serializer matching assessment response spec."""

    distance = serializers.FloatField(help_text="Total distance in miles")
    duration = serializers.FloatField(help_text="Estimated driving time in hours")
    directions = serializers.ListField(child=serializers.DictField())
    route_geometry = serializers.ListField(child=serializers.ListField(child=serializers.FloatField()))
    fuel_stops = serializers.ListField(child=serializers.DictField())
    rest_stops = serializers.ListField(child=serializers.DictField())
    daily_logs = DailyLogSerializer(many=True)
