import React from 'react';
import { Navigation } from 'lucide-react';

export default function DirectionsList({ directions, fullPage = false }) {
  if (!directions || directions.length === 0) {
    return (
      <div className="card">
        <div className="empty-state">
          <Navigation className="empty-state-icon" size={48} strokeWidth={1.25} />
          <h3 className="empty-state-title">No directions available</h3>
          <p className="empty-state-text">Plan a trip to generate turn-by-turn navigation instructions.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`directions-panel${fullPage ? ' directions-panel-full' : ''}`}>
      <div className="directions-header">
        <span className="directions-count">{directions.length} steps</span>
      </div>
      <div className="directions-list">
        {directions.map((step, idx) => (
          <div key={idx} className="direction-step">
            <div className="step-number">{idx + 1}</div>
            <div className="step-content">
              <p className="step-instruction">{step.instruction}</p>
              <div className="step-meta">
                <span>{step.distance_miles} mi</span>
                <span className="step-sep">·</span>
                <span>~{step.duration_minutes} min</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .directions-panel {
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          overflow: hidden;
          box-shadow: var(--shadow-sm);
        }

        .directions-panel-full {
          max-height: calc(100vh - 220px);
          display: flex;
          flex-direction: column;
        }

        .directions-header {
          padding: 14px 20px;
          border-bottom: 1px solid var(--color-border);
          background: #f8fafc;
        }

        .directions-count {
          font-size: 0.8125rem;
          font-weight: 500;
          color: var(--color-text-secondary);
        }

        .directions-list {
          overflow-y: auto;
          flex: 1;
        }

        .direction-step {
          display: flex;
          gap: 14px;
          padding: 14px 20px;
          border-bottom: 1px solid var(--color-border);
          transition: background 0.1s;
        }

        .direction-step:last-child {
          border-bottom: none;
        }

        .direction-step:hover {
          background: #f8fafc;
        }

        .step-number {
          width: 28px;
          height: 28px;
          background: var(--color-primary-light);
          color: var(--color-primary);
          border-radius: var(--radius-sm);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.75rem;
          font-weight: 600;
          flex-shrink: 0;
        }

        .step-instruction {
          margin: 0;
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--color-text);
          line-height: 1.4;
        }

        .step-meta {
          margin-top: 4px;
          font-size: 0.75rem;
          color: var(--color-text-muted);
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .step-sep {
          color: var(--color-border-strong);
        }
      `}</style>
    </div>
  );
}
