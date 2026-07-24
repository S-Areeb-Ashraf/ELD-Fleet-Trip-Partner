import React from 'react';
import { useTrip } from '../context/TripContext';
import LogViewer from '../components/LogViewer';

export default function LogsPage() {
  const { tripData } = useTrip();

  if (!tripData) return null;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Daily Log Sheets</h1>
        <p className="page-subtitle">
          FMCSA driver daily logs rendered on official ELD template — {tripData.daily_logs?.length || 0} sheet(s) for this trip
        </p>
      </div>

      <LogViewer dailyLogs={tripData.daily_logs} />
    </div>
  );
}
