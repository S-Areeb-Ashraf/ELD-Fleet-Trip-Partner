"""
API Views for Trip Planning.
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import TripPlanRequestSerializer
from api.services.trip_scheduler import TripScheduler
from api.services.utils import format_api_error
from api.models import TripPlan

logger = logging.getLogger(__name__)


class HomeRootView(APIView):
    """
    GET /
    Returns API status health check and available endpoints.
    """

    def get(self, request, *args, **kwargs):
        return Response({
            "status": "Spotter ELD & GIS Trip Planner API is running",
            "version": "1.0.0",
            "endpoints": {
                "plan_trip": "POST /plan-trip/",
                "admin": "GET /admin/",
            },
            "documentation": "Send POST request to /plan-trip/ with current_location, pickup_location, dropoff_location, and current_cycle_used."
        }, status=status.HTTP_200_OK)


class PlanTripView(APIView):
    """
    POST /plan-trip/
    Accepts trip locations and current cycle hours, returns route instructions, map geometry,
    fuel stops, HOS rest stops, and generated FMCSA ELD Daily Log PNGs.
    """

    def post(self, request, *args, **kwargs):
        serializer = TripPlanRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        current_loc = data["current_location"]
        pickup_loc = data["pickup_location"]
        dropoff_loc = data["dropoff_location"]
        cycle_used = data.get("current_cycle_used", 0.0)

        try:
            trip_result = TripScheduler.plan_trip(
                current_location=current_loc,
                pickup_location=pickup_loc,
                dropoff_location=dropoff_loc,
                current_cycle_used=cycle_used,
            )

            # Store planned trip record in DB
            TripPlan.objects.create(
                current_location=current_loc,
                pickup_location=pickup_loc,
                dropoff_location=dropoff_loc,
                current_cycle_used=cycle_used,
                total_distance_miles=trip_result["distance"],
                total_duration_hours=trip_result["duration"],
                response_json=trip_result,
            )

            return Response(trip_result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error planning trip: {e}", exc_info=True)
            return Response(
                format_api_error(f"Failed to plan trip: {str(e)}", status_code=500),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
