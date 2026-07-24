import React from 'react';
import { NavLink, Outlet, useLocation, Navigate } from 'react-router-dom';
import {
  Home,
  Truck,
  MapPin,
  Map,
  ListOrdered,
  FileText,
  LayoutDashboard,
  ChevronRight,
} from 'lucide-react';
import { useTrip } from '../context/TripContext';

const navItems = [
  { to: '/', label: 'Home', icon: Home, requiresTrip: false },
  { to: '/plan', label: 'Trip Planning', icon: MapPin, requiresTrip: false },
  { to: '/overview', label: 'Trip Overview', icon: LayoutDashboard, requiresTrip: true },
  { to: '/map', label: 'Route Map', icon: Map, requiresTrip: true },
  { to: '/directions', label: 'Navigation Steps', icon: ListOrdered, requiresTrip: true },
  { to: '/logs', label: 'Daily Log Sheets', icon: FileText, requiresTrip: true },
];

function SidebarLink({ to, label, icon: Icon, disabled }) {
  if (disabled) {
    return (
      <div className="sidebar-link sidebar-link-disabled" title="Plan a trip first">
        <Icon size={18} strokeWidth={1.75} />
        <span>{label}</span>
      </div>
    );
  }

  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `sidebar-link${isActive ? ' sidebar-link-active' : ''}`
      }
    >
      <Icon size={18} strokeWidth={1.75} />
      <span>{label}</span>
    </NavLink>
  );
}

export default function AppLayout() {
  const { hasTrip, tripData } = useTrip();
  const location = useLocation();

  const currentNav = navItems.find((item) => item.to === location.pathname);
  const routeLabel = tripData?.waypoints
    ? `${tripData.waypoints.current?.label || 'Origin'} → ${tripData.waypoints.dropoff?.label || 'Destination'}`
    : null;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">
            <Truck size={22} strokeWidth={1.75} />
          </div>
          <div>
            <div className="sidebar-brand-title">Spotter ELD</div>
            <div className="sidebar-brand-sub">Fleet Trip Planner</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="sidebar-section-label">Navigation</div>
          {navItems.map((item) => (
            <SidebarLink
              key={item.to}
              to={item.to}
              label={item.label}
              icon={item.icon}
              disabled={item.requiresTrip && !hasTrip}
            />
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-compliance">
            <span className="compliance-dot" />
            FMCSA 70-Hr / 8-Day Compliant
          </div>
        </div>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <nav className="breadcrumb" aria-label="Breadcrumb">
              <span className="breadcrumb-root">Spotter ELD</span>
              {currentNav && (
                <>
                  <ChevronRight size={14} className="breadcrumb-sep" />
                  <span className="breadcrumb-current">{currentNav.label}</span>
                </>
              )}
            </nav>
            {routeLabel && hasTrip && (
              <p className="topbar-route">{routeLabel}</p>
            )}
          </div>
          <div className="topbar-right">
            {hasTrip && (
              <span className="topbar-badge topbar-badge-active">Trip Active</span>
            )}
          </div>
        </header>

        <main className="main-content">
          <Outlet />
        </main>

        <footer className="app-footer">
          Spotter AI Assessment · FMCSA Hours of Service & ELD Log Engine
        </footer>
      </div>

      <style>{`
        .app-shell {
          display: flex;
          min-height: 100vh;
        }

        .sidebar {
          width: var(--sidebar-width);
          background: var(--color-sidebar);
          color: #e2e8f0;
          display: flex;
          flex-direction: column;
          flex-shrink: 0;
          position: fixed;
          top: 0;
          left: 0;
          bottom: 0;
          z-index: 100;
        }

        .sidebar-brand {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 24px 20px;
          border-bottom: 1px solid rgba(255,255,255,0.08);
        }

        .sidebar-brand-icon {
          width: 40px;
          height: 40px;
          background: var(--color-primary);
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
          color: #fff;
        }

        .sidebar-brand-title {
          font-size: 0.9375rem;
          font-weight: 600;
          color: #fff;
          letter-spacing: -0.01em;
        }

        .sidebar-brand-sub {
          font-size: 0.6875rem;
          color: #94a3b8;
          margin-top: 2px;
        }

        .sidebar-nav {
          flex: 1;
          padding: 16px 12px;
          overflow-y: auto;
        }

        .sidebar-section-label {
          font-size: 0.6875rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.06em;
          color: #64748b;
          padding: 8px 12px 10px;
        }

        .sidebar-link {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px 12px;
          border-radius: var(--radius-md);
          font-size: 0.875rem;
          font-weight: 500;
          color: #cbd5e1;
          text-decoration: none;
          margin-bottom: 2px;
          transition: background 0.15s, color 0.15s;
        }

        .sidebar-link:hover:not(.sidebar-link-disabled) {
          background: var(--color-sidebar-hover);
          color: #fff;
        }

        .sidebar-link-active {
          background: var(--color-sidebar-active) !important;
          color: #fff !important;
        }

        .sidebar-link-disabled {
          opacity: 0.4;
          cursor: not-allowed;
        }

        .sidebar-footer {
          padding: 16px 20px;
          border-top: 1px solid rgba(255,255,255,0.08);
        }

        .sidebar-compliance {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 0.6875rem;
          color: #94a3b8;
        }

        .compliance-dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: var(--color-success);
          flex-shrink: 0;
        }

        .main-area {
          flex: 1;
          margin-left: var(--sidebar-width);
          display: flex;
          flex-direction: column;
          min-height: 100vh;
        }

        .topbar {
          background: var(--color-surface);
          border-bottom: 1px solid var(--color-border);
          padding: 16px 32px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          position: sticky;
          top: 0;
          z-index: 50;
        }

        .topbar-left {
          min-width: 0;
        }

        .breadcrumb {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.8125rem;
        }

        .breadcrumb-root {
          color: var(--color-text-muted);
        }

        .breadcrumb-sep {
          color: var(--color-text-muted);
        }

        .breadcrumb-current {
          color: var(--color-text);
          font-weight: 500;
        }

        .topbar-route {
          margin: 4px 0 0;
          font-size: 0.8125rem;
          color: var(--color-text-secondary);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .topbar-badge {
          font-size: 0.75rem;
          font-weight: 500;
          padding: 5px 12px;
          border-radius: 999px;
          border: 1px solid var(--color-border);
          color: var(--color-text-secondary);
        }

        .topbar-badge-active {
          background: #ecfdf5;
          border-color: #a7f3d0;
          color: #065f46;
        }

        .main-content {
          flex: 1;
        }

        .app-footer {
          padding: 16px 32px;
          border-top: 1px solid var(--color-border);
          background: var(--color-surface);
          font-size: 0.75rem;
          color: var(--color-text-muted);
          text-align: center;
        }

        @media (max-width: 768px) {
          .sidebar {
            width: 64px;
          }
          .sidebar-brand > div:last-child,
          .sidebar-link span,
          .sidebar-section-label,
          .sidebar-compliance,
          .sidebar-footer {
            display: none;
          }
          .sidebar-brand {
            justify-content: center;
            padding: 16px 8px;
          }
          .sidebar-link {
            justify-content: center;
            padding: 12px;
          }
          .main-area {
            margin-left: 64px;
          }
          .topbar {
            padding: 12px 16px;
          }
        }
      `}</style>
    </div>
  );
}

export function RequireTrip({ children }) {
  const { hasTrip } = useTrip();
  if (!hasTrip) {
    return <Navigate to="/plan" replace />;
  }
  return children;
}
