import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, ArrowRight } from 'lucide-react';
import { useTrip } from '../context/TripContext';

const PRESETS = [
  {
    id: 'fmcsa_example',
    label: 'FMCSA Example',
    description: 'Richmond → Baltimore → Newark',
    values: {
      current_location: 'Richmond, VA',
      pickup_location: 'Baltimore, MD',
      dropoff_location: 'Newark, NJ',
      current_cycle_used: 0,
    },
  },
  {
    id: 'cross_country',
    label: 'Cross-Country',
    description: 'LA → Denver → New York',
    values: {
      current_location: 'Los Angeles, CA',
      pickup_location: 'Denver, CO',
      dropoff_location: 'New York, NY',
      current_cycle_used: 45,
    },
  },
  {
    id: 'restart_trigger',
    label: 'Cycle Restart',
    description: '67.5 hrs used — triggers 34h restart',
    values: {
      current_location: 'Los Angeles, CA',
      pickup_location: 'Phoenix, AZ',
      dropoff_location: 'Atlanta, GA',
      current_cycle_used: 67.5,
    },
  },
];

export default function PlanPage() {
  const navigate = useNavigate();
  const { planTrip, loading, error, setError } = useTrip();

  const [currentLocation, setCurrentLocation] = useState('Richmond, VA');
  const [pickupLocation, setPickupLocation] = useState('Baltimore, MD');
  const [dropoffLocation, setDropoffLocation] = useState('Newark, NJ');
  const [currentCycleUsed, setCurrentCycleUsed] = useState(0);

  const applyPreset = (preset) => {
    setCurrentLocation(preset.values.current_location);
    setPickupLocation(preset.values.pickup_location);
    setDropoffLocation(preset.values.dropoff_location);
    setCurrentCycleUsed(preset.values.current_cycle_used);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await planTrip({
        current_location: currentLocation,
        pickup_location: pickupLocation,
        dropoff_location: dropoffLocation,
        current_cycle_used: parseFloat(currentCycleUsed),
      });
      navigate('/overview');
    } catch {
      // error handled in context
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Trip Planning</h1>
        <p className="page-subtitle">
          Enter route details and current HOS cycle balance to generate FMCSA-compliant logs and navigation.
        </p>
      </div>

      {error && (
        <div className="alert alert-error" style={{ marginBottom: 24 }}>
          <AlertCircle size={18} style={{ flexShrink: 0, marginTop: 1 }} />
          <div>
            <strong>Planning failed</strong>
            <div style={{ marginTop: 2 }}>{error}</div>
          </div>
          <button
            type="button"
            className="btn btn-ghost"
            style={{ marginLeft: 'auto', padding: '4px 8px' }}
            onClick={() => setError(null)}
          >
            Dismiss
          </button>
        </div>
      )}

      <div className="plan-grid">
        <div className="card">
          <div className="card-header">
            <h2 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>Route Configuration</h2>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit} className="plan-form">
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label" htmlFor="current-location">Current Location</label>
                  <input
                    id="current-location"
                    type="text"
                    required
                    className="form-input"
                    value={currentLocation}
                    onChange={(e) => setCurrentLocation(e.target.value)}
                    placeholder="e.g. Richmond, VA"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" htmlFor="pickup-location">Pickup Location</label>
                  <input
                    id="pickup-location"
                    type="text"
                    required
                    className="form-input"
                    value={pickupLocation}
                    onChange={(e) => setPickupLocation(e.target.value)}
                    placeholder="e.g. Baltimore, MD"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" htmlFor="dropoff-location">Dropoff Location</label>
                  <input
                    id="dropoff-location"
                    type="text"
                    required
                    className="form-input"
                    value={dropoffLocation}
                    onChange={(e) => setDropoffLocation(e.target.value)}
                    placeholder="e.g. Newark, NJ"
                  />
                </div>
              </div>

              <div className="form-group" style={{ marginTop: 8 }}>
                <div className="cycle-header">
                  <label className="form-label" htmlFor="cycle-slider" style={{ marginBottom: 0 }}>
                    Current Cycle Used
                  </label>
                  <span className="cycle-value">{currentCycleUsed} / 70.0 hrs</span>
                </div>
                <p className="form-hint">Hours accumulated in the 70-hour / 8-day rolling window before this trip.</p>
                <input
                  id="cycle-slider"
                  type="range"
                  min="0"
                  max="70"
                  step="0.5"
                  value={currentCycleUsed}
                  onChange={(e) => setCurrentCycleUsed(e.target.value)}
                  className="cycle-slider"
                />
              </div>

              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? (
                    <>
                      <span className="spinner" />
                      Calculating route &amp; generating logs…
                    </>
                  ) : (
                    <>
                      Generate Route &amp; Logs
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>Quick Presets</h2>
          </div>
          <div className="card-body preset-list">
            {PRESETS.map((preset) => (
              <button
                key={preset.id}
                type="button"
                className="preset-item"
                onClick={() => applyPreset(preset)}
              >
                <div>
                  <div className="preset-label">{preset.label}</div>
                  <div className="preset-desc">{preset.description}</div>
                </div>
                <ArrowRight size={16} className="preset-arrow" />
              </button>
            ))}
          </div>
        </div>
      </div>

      <style>{`
        .plan-grid {
          display: grid;
          grid-template-columns: 1fr 320px;
          gap: 24px;
          align-items: start;
        }

        .plan-form .form-row {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 16px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
        }

        .form-hint {
          font-size: 0.75rem;
          color: var(--color-text-muted);
          margin: 4px 0 12px;
        }

        .cycle-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 4px;
        }

        .cycle-value {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--color-primary);
        }

        .cycle-slider {
          width: 100%;
          accent-color: var(--color-primary);
          height: 6px;
        }

        .form-actions {
          margin-top: 24px;
          padding-top: 24px;
          border-top: 1px solid var(--color-border);
        }

        .form-actions .btn-primary {
          width: 100%;
          padding: 12px 20px;
        }

        .preset-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
          padding: 16px !important;
        }

        .preset-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          width: 100%;
          padding: 14px 16px;
          background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
          border: 1px solid rgba(30, 64, 175, 0.12);
          border-radius: var(--radius-md);
          cursor: pointer;
          text-align: left;
          box-shadow: var(--shadow-sm);
          transition: transform 0.15s, border-color 0.15s, box-shadow 0.15s, background 0.15s;
        }

        .preset-item:hover {
          border-color: var(--color-primary);
          background: linear-gradient(180deg, #f8fbff 0%, #eaf2ff 100%);
          box-shadow: var(--shadow-md);
          transform: translateY(-1px);
        }

        .preset-label {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--color-text);
        }

        .preset-desc {
          font-size: 0.75rem;
          color: var(--color-text-secondary);
          margin-top: 2px;
        }

        .preset-arrow {
          color: var(--color-text-muted);
          flex-shrink: 0;
        }

        @media (max-width: 1024px) {
          .plan-grid {
            grid-template-columns: 1fr;
          }
          .plan-form .form-row {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}
