import React from 'react';
import { useTrip } from '../context/TripContext';
import DirectionsList from '../components/DirectionsList';

export default function DirectionsPage() {
  const { tripData } = useTrip();

  if (!tripData) return null;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Navigation Steps</h1>
        <p className="page-subtitle">
          Turn-by-turn directions for {tripData.waypoints?.current?.label} to {tripData.waypoints?.dropoff?.label}
        </p>
      </div>

      <DirectionsList directions={tripData.directions} fullPage />
    </div>
  );
}
