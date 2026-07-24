import React from 'react';

export default function SummaryCards({ tripData }) {
  if (!tripData) return null;

  const { distance, duration, fuel_stops, rest_stops, daily_logs } = tripData;

  const restartsCount = rest_stops?.filter((r) => r.reason === '34-hr restart').length || 0;
  const resetsCount = rest_stops?.filter((r) => r.reason === '10-hr reset').length || 0;
  const breakCount = rest_stops?.filter((r) => r.reason === '30-min break').length || 0;

  const stats = [
    {
      label: 'Total Distance',
      value: distance,
      unit: 'mi',
      meta: `${(distance * 1.60934).toFixed(0)} km`,
    },
    {
      label: 'Driving Time',
      value: duration,
      unit: 'hrs',
      meta: 'Net driving duration',
    },
    {
      label: 'Fuel Stops',
      value: fuel_stops?.length || 0,
      unit: '',
      meta: 'Every 1,000 mi',
    },
    {
      label: 'Rest Events',
      value: resetsCount + restartsCount + breakCount,
      unit: '',
      meta: `${resetsCount}× 10h · ${restartsCount}× 34h · ${breakCount}× 30m`,
    },
    {
      label: 'Log Sheets',
      value: daily_logs?.length || 0,
      unit: '',
      meta: 'FMCSA ELD PNGs',
    },
  ];

  return (
    <div className="stat-grid">
      {stats.map((stat) => (
        <div key={stat.label} className="stat-card">
          <div className="stat-label">{stat.label}</div>
          <div>
            <span className="stat-value">{stat.value}</span>
            {stat.unit && <span className="stat-unit">{stat.unit}</span>}
          </div>
          <div className="stat-meta">{stat.meta}</div>
        </div>
      ))}
    </div>
  );
}
