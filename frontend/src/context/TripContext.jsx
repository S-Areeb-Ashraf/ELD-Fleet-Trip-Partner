import React, { createContext, useContext, useState, useCallback } from 'react';
import { planTrip as fetchPlanTrip } from '../api';

const TripContext = createContext(null);

const STORAGE_KEY = 'spotter_trip_data';

function loadStoredTrip() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function TripProvider({ children }) {
  const [tripData, setTripDataState] = useState(loadStoredTrip);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastPayload, setLastPayload] = useState(null);

  const setTripData = useCallback((data) => {
    setTripDataState(data);
    if (data) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } else {
      sessionStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const planTrip = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    setLastPayload(payload);
    try {
      const data = await fetchPlanTrip(payload);
      setTripData(data);
      return data;
    } catch (err) {
      const message = err.message || 'Failed to plan trip. Please verify backend connection.';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setTripData]);

  const clearTrip = useCallback(() => {
    setTripData(null);
    setError(null);
    setLastPayload(null);
  }, [setTripData]);

  return (
    <TripContext.Provider
      value={{
        tripData,
        loading,
        error,
        lastPayload,
        planTrip,
        clearTrip,
        setError,
        hasTrip: Boolean(tripData),
      }}
    >
      {children}
    </TripContext.Provider>
  );
}

export function useTrip() {
  const ctx = useContext(TripContext);
  if (!ctx) {
    throw new Error('useTrip must be used within TripProvider');
  }
  return ctx;
}
