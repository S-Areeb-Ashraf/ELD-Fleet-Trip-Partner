"""
API URL Configuration.
"""

from django.urls import path
from api.views import HomeRootView, PlanTripView

urlpatterns = [
    path("", HomeRootView.as_view(), name="api-root"),
    path("plan-trip/", PlanTripView.as_view(), name="plan-trip"),
]
