import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Map, ListOrdered, FileText, MapPin, RotateCcw } from 'lucide-react';
import { useTrip } from '../context/TripContext';
import SummaryCards from '../components/SummaryCards';

export default function OverviewPage() {
  const { tripData, clearTrip } = useTrip();
  const navigate = useNavigate();

  if (!tripData) return null;

  const handleClear = () => {
    clearTrip();
    navigate('/plan');
  };

  const restartsCount = tripData.rest_stops?.filter((r) => r.reason === '34-hr restart').length || 0;
  const resetsCount = tripData.rest_stops?.filter((r) => r.reason === '10-hr reset').length || 0;

  const quickLinks = [
    {
      to: '/map',
      label: 'View Route Map',
      description: 'Interactive map with stops, fuel, and rest markers',
      icon: Map,
    },
    {
      to: '/directions',
      label: 'Navigation Steps',
      description: `${tripData.directions?.length || 0} turn-by-turn instructions`,
      icon: ListOrdered,
    },
    {
      to: '/logs',
      label: 'Daily Log Sheets',
      description: `${tripData.daily_logs?.length || 0} FMCSA ELD log PNG${tripData.daily_logs?.length !== 1 ? 's' : ''} generated`,
      icon: FileText,
    },
  ];

  return (
    <div className="page-container">
      <div className="overview-header">
        <div>
          <h1 className="page-title">Trip Overview</h1>
          <p className="page-subtitle">
            {tripData.waypoints?.current?.label} → {tripData.waypoints?.pickup?.label} → {tripData.waypoints?.dropoff?.label}
          </p>
        </div>
        <div className="overview-actions">
          <Link to="/plan" className="btn btn-secondary">
            <MapPin size={16} />
            New Trip
          </Link>
          <button type="button" className="btn btn-ghost" onClick={handleClear}>
            <RotateCcw size={16} />
            Clear
          </button>
        </div>
      </div>

      <SummaryCards tripData={tripData} />

      <div className="overview-section">
        <h2 className="section-title">HOS Summary</h2>
        <div className="hos-grid">
          <div className="hos-item">
            <span className="hos-label">10-Hour Resets</span>
            <span className="hos-value">{resetsCount}</span>
          </div>
          <div className="hos-item">
            <span className="hos-label">34-Hour Restarts</span>
            <span className="hos-value">{restartsCount}</span>
          </div>
          <div className="hos-item">
            <span className="hos-label">Fuel Stops</span>
            <span className="hos-value">{tripData.fuel_stops?.length || 0}</span>
          </div>
          <div className="hos-item">
            <span className="hos-label">Log Sheets</span>
            <span className="hos-value">{tripData.daily_logs?.length || 0}</span>
          </div>
        </div>
      </div>

      <div className="overview-section">
        <h2 className="section-title">Explore Results</h2>
        <div className="quick-links">
          {quickLinks.map((link) => (
            <Link key={link.to} to={link.to} className="quick-link-card">
              <div className="quick-link-icon">
                <link.icon size={22} strokeWidth={1.75} />
              </div>
              <div>
                <div className="quick-link-label">{link.label}</div>
                <div className="quick-link-desc">{link.description}</div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      <style>{`
        .overview-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 16px;
          margin-bottom: 28px;
        }

        .overview-actions {
          display: flex;
          gap: 8px;
          flex-shrink: 0;
        }

        .overview-section {
          margin-top: 32px;
        }

        .section-title {
          font-size: 0.9375rem;
          font-weight: 600;
          color: var(--color-text);
          margin: 0 0 16px;
        }

        .hos-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 12px;
        }

        .hos-item {
          position: relative;
          overflow: hidden;
          background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
          border: 1px solid rgba(30, 64, 175, 0.12);
          border-radius: var(--radius-md);
          padding: 16px 20px;
          display: flex;
          flex-direction: column;
          gap: 4px;
          box-shadow: var(--shadow-sm);
        }

        .hos-item::after {
          content: '';
          position: absolute;
          inset: 0 0 auto 0;
          height: 3px;
          background: linear-gradient(90deg, var(--color-primary), #60a5fa);
        }

        .hos-item:nth-child(2n)::after {
          background: linear-gradient(90deg, #0f766e, #5eead4);
        }

        .hos-item:nth-child(3n)::after {
          background: linear-gradient(90deg, #d97706, #fdba74);
        }

        .hos-item:nth-child(4n)::after {
          background: linear-gradient(90deg, #7c3aed, #c4b5fd);
        }

        .hos-label {
          font-size: 0.75rem;
          color: var(--color-text-secondary);
          font-weight: 500;
        }

        .hos-value {
          font-size: 1.5rem;
          font-weight: 600;
          color: var(--color-text);
        }

        .quick-links {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 16px;
        }

        .quick-link-card {
          display: flex;
          align-items: flex-start;
          gap: 16px;
          padding: 20px;
          background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
          border: 1px solid rgba(30, 64, 175, 0.12);
          border-radius: var(--radius-lg);
          text-decoration: none;
          color: inherit;
          box-shadow: var(--shadow-sm);
          transition: transform 0.15s, border-color 0.15s, box-shadow 0.15s;
        }

        .quick-link-card:hover {
          border-color: var(--color-primary);
          box-shadow: var(--shadow-md);
          transform: translateY(-1px);
        }

        .quick-link-icon {
          width: 44px;
          height: 44px;
          background: var(--color-primary-light);
          color: var(--color-primary);
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .quick-link-label {
          font-size: 0.9375rem;
          font-weight: 600;
          color: var(--color-text);
        }

        .quick-link-desc {
          font-size: 0.8125rem;
          color: var(--color-text-secondary);
          margin-top: 4px;
        }

        @media (max-width: 900px) {
          .hos-grid, .quick-links {
            grid-template-columns: 1fr;
          }
          .overview-header {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
}
