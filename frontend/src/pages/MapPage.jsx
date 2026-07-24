import React from 'react';
import { useTrip } from '../context/TripContext';
import RouteMap from '../components/RouteMap';

export default function MapPage() {
  const { tripData } = useTrip();

  if (!tripData) return null;

  return (
    <div className="page-container page-container-full">
      <div className="page-header">
        <h1 className="page-title">Route Map</h1>
        <p className="page-subtitle">
          {tripData.distance} mi · {tripData.duration} hrs driving · {tripData.fuel_stops?.length || 0} fuel stops · {tripData.rest_stops?.length || 0} rest events
        </p>
      </div>

      <RouteMap tripData={tripData} fullHeight />

      <style>{`
        .page-container-full {
          display: flex;
          flex-direction: column;
          height: calc(100vh - 130px);
          min-height: 500px;
        }
        .page-container-full .page-header {
          flex-shrink: 0;
          margin-bottom: 20px;
        }
      `}</style>
    </div>
  );
}
