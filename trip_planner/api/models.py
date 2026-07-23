"""
Django Models for Trip Planner API.
"""

from django.db import models


class TripPlan(models.Model):
    """Stores historical trip plan requests and generated responses."""

    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_used = models.FloatField(default=0.0)
    
    total_distance_miles = models.FloatField(default=0.0)
    total_duration_hours = models.FloatField(default=0.0)
    
    response_json = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TripPlan #{self.id}: {self.current_location} -> {self.pickup_location} -> {self.dropoff_location}"
