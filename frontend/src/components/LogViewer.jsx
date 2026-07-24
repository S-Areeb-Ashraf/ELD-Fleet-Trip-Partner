import React, { useState } from 'react';
import { Download, Maximize2, X, FileText } from 'lucide-react';
import { API_BASE_URL } from '../config';

export default function LogViewer({ dailyLogs }) {
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  const [zoomModal, setZoomModal] = useState(false);

  if (!dailyLogs || dailyLogs.length === 0) {
    return (
      <div className="card">
        <div className="empty-state">
          <FileText className="empty-state-icon" size={48} strokeWidth={1.25} />
          <h3 className="empty-state-title">No log sheets generated</h3>
          <p className="empty-state-text">Plan a trip to generate FMCSA daily log PNGs.</p>
        </div>
      </div>
    );
  }

  const currentLog = dailyLogs[selectedDayIndex] || dailyLogs[0];
  const fullPngUrl = currentLog.png_url.startsWith('http')
    ? currentLog.png_url
    : `${API_BASE_URL}${currentLog.png_url}`;

  return (
    <>
      <div className="log-viewer">
        <div className="log-tabs">
          {dailyLogs.map((log, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setSelectedDayIndex(idx)}
              className={`log-tab${selectedDayIndex === idx ? ' log-tab-active' : ''}`}
            >
              Day {log.day_number}
              <span className="log-tab-date">{log.date}</span>
            </button>
          ))}
        </div>

        <div className="log-metrics">
          <div className="log-metric">
            <span className="log-metric-label">Driving</span>
            <span className="log-metric-value">{currentLog.total_driving_hours} hrs</span>
          </div>
          <div className="log-metric">
            <span className="log-metric-label">On Duty (ND)</span>
            <span className="log-metric-value">{currentLog.total_on_duty_hours} hrs</span>
          </div>
          <div className="log-metric">
            <span className="log-metric-label">Off Duty</span>
            <span className="log-metric-value">{currentLog.total_off_duty_hours} hrs</span>
          </div>
          <div className="log-metric">
            <span className="log-metric-label">Miles</span>
            <span className="log-metric-value">{currentLog.total_miles_driven} mi</span>
          </div>
        </div>

        <div className="log-preview-card">
          <div className="log-preview-toolbar">
            <span className="log-preview-title">
              FMCSA Driver Daily Log — Day {currentLog.day_number} ({currentLog.date})
            </span>
            <div className="log-preview-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setZoomModal(true)}>
                <Maximize2 size={14} />
                Zoom
              </button>
              <a
                href={fullPngUrl}
                download={`daily_log_day_${currentLog.day_number}.png`}
                target="_blank"
                rel="noreferrer"
                className="btn btn-primary"
              >
                <Download size={14} />
                Download
              </a>
            </div>
          </div>
          <div className="log-preview-frame">
            <img
              src={fullPngUrl}
              alt={`FMCSA Daily Log Day ${currentLog.day_number}`}
              className="log-preview-img"
              onClick={() => setZoomModal(true)}
            />
          </div>
        </div>
      </div>

      {zoomModal && (
        <div className="log-modal" onClick={() => setZoomModal(false)} role="presentation">
          <div className="log-modal-inner" onClick={(e) => e.stopPropagation()}>
            <div className="log-modal-header">
              <span>Day {currentLog.day_number} — {currentLog.date}</span>
              <button type="button" className="btn btn-ghost" onClick={() => setZoomModal(false)}>
                <X size={18} />
              </button>
            </div>
            <div className="log-modal-body">
              <img src={fullPngUrl} alt="Zoomed daily log" className="log-modal-img" />
            </div>
          </div>
        </div>
      )}

      <style>{`
        .log-viewer {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .log-tabs {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .log-tab {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
          padding: 10px 16px;
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          cursor: pointer;
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--color-text);
          transition: border-color 0.15s, background 0.15s;
        }

        .log-tab:hover {
          border-color: var(--color-border-strong);
        }

        .log-tab-active {
          background: var(--color-primary-light);
          border-color: var(--color-primary);
          color: var(--color-primary);
        }

        .log-tab-date {
          font-size: 0.6875rem;
          font-weight: 400;
          color: var(--color-text-muted);
          margin-top: 2px;
        }

        .log-tab-active .log-tab-date {
          color: var(--color-primary);
          opacity: 0.75;
        }

        .log-metrics {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 12px;
        }

        .log-metric {
          position: relative;
          overflow: hidden;
          background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
          border: 1px solid rgba(30, 64, 175, 0.12);
          border-radius: var(--radius-md);
          padding: 14px 18px;
          box-shadow: var(--shadow-sm);
        }

        .log-metric::before {
          content: '';
          position: absolute;
          inset: 0 auto 0 0;
          width: 4px;
          background: linear-gradient(180deg, var(--color-primary), #60a5fa);
        }

        .log-metric:nth-child(2n)::before {
          background: linear-gradient(180deg, #0f766e, #5eead4);
        }

        .log-metric:nth-child(3n)::before {
          background: linear-gradient(180deg, #d97706, #fdba74);
        }

        .log-metric:nth-child(4n)::before {
          background: linear-gradient(180deg, #7c3aed, #c4b5fd);
        }

        .log-metric-label {
          display: block;
          font-size: 0.6875rem;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.04em;
          color: var(--color-text-secondary);
          margin-bottom: 4px;
        }

        .log-metric-value {
          font-size: 1.125rem;
          font-weight: 600;
          color: var(--color-text);
        }

        .log-preview-card {
          background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
          border: 1px solid rgba(30, 64, 175, 0.12);
          border-radius: var(--radius-lg);
          overflow: hidden;
          box-shadow: var(--shadow-sm);
        }

        .log-preview-toolbar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
          padding: 14px 20px;
          border-bottom: 1px solid var(--color-border);
          background: linear-gradient(180deg, #f8fafc 0%, #eef4ff 100%);
        }

        .log-preview-title {
          font-size: 0.8125rem;
          font-weight: 500;
          color: var(--color-text-secondary);
        }

        .log-preview-actions {
          display: flex;
          gap: 8px;
        }

        .log-preview-frame {
          padding: 20px;
          background: linear-gradient(180deg, #edf3ff 0%, #f8fafc 100%);
        }

        .log-preview-img {
          width: 100%;
          height: auto;
          max-height: 700px;
          object-fit: contain;
          border-radius: var(--radius-md);
          border: 1px solid var(--color-border);
          background: #fff;
          cursor: zoom-in;
        }

        .log-modal {
          position: fixed;
          inset: 0;
          z-index: 200;
          background: rgba(15, 23, 42, 0.75);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px;
        }

        .log-modal-inner {
          background: var(--color-surface);
          border-radius: var(--radius-lg);
          max-width: 960px;
          width: 100%;
          max-height: 90vh;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          box-shadow: var(--shadow-lg);
        }

        .log-modal-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px 20px;
          border-bottom: 1px solid var(--color-border);
          font-weight: 500;
          font-size: 0.875rem;
        }

        .log-modal-body {
          overflow: auto;
          padding: 20px;
          background: #f1f5f9;
        }

        .log-modal-img {
          width: 100%;
          height: auto;
        }

        @media (max-width: 768px) {
          .log-metrics {
            grid-template-columns: repeat(2, 1fr);
          }
          .log-preview-toolbar {
            flex-direction: column;
            align-items: flex-start;
          }
        }
      `}</style>
    </>
  );
}
