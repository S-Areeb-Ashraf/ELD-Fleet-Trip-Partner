import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { TripProvider } from './context/TripContext';
import AppLayout, { RequireTrip } from './layouts/AppLayout';
import PlanPage from './pages/PlanPage';
import OverviewPage from './pages/OverviewPage';
import MapPage from './pages/MapPage';
import DirectionsPage from './pages/DirectionsPage';
import LogsPage from './pages/LogsPage';
import LandingPage from './pages/LandingPage';

export default function App() {
  return (
    <TripProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<LandingPage />} />
            <Route path="plan" element={<PlanPage />} />
            <Route
              path="overview"
              element={
                <RequireTrip>
                  <OverviewPage />
                </RequireTrip>
              }
            />
            <Route
              path="map"
              element={
                <RequireTrip>
                  <MapPage />
                </RequireTrip>
              }
            />
            <Route
              path="directions"
              element={
                <RequireTrip>
                  <DirectionsPage />
                </RequireTrip>
              }
            />
            <Route
              path="logs"
              element={
                <RequireTrip>
                  <LogsPage />
                </RequireTrip>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </TripProvider>
  );
}
