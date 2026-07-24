import React, { useEffect, useRef } from 'react';

const LEGEND = [
  { color: '#2563eb', label: 'Route' },
  { color: '#0284c7', label: 'Start' },
  { color: '#059669', label: 'Pickup' },
  { color: '#dc2626', label: 'Dropoff' },
  { color: '#d97706', label: 'Fuel' },
  { color: '#7c3aed', label: '10h Reset' },
  { color: '#ea580c', label: '34h Restart' },
];

export default function RouteMap({ tripData, fullHeight = false }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    if (!tripData || !mapRef.current || !window.L) return;

    const { waypoints, route_geometry, fuel_stops, rest_stops } = tripData;
    const L = window.L;

    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    const startLat = waypoints?.current?.lat || 37.5407;
    const startLon = waypoints?.current?.lon || -77.4360;

    const map = L.map(mapRef.current, {
      zoomControl: true,
      attributionControl: true,
    }).setView([startLat, startLon], 6);

    mapInstanceRef.current = map;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    const bounds = L.latLngBounds();

    if (route_geometry && route_geometry.length > 0) {
      const polyline = L.polyline(route_geometry, {
        color: '#2563eb',
        weight: 4,
        opacity: 0.85,
        lineCap: 'round',
        lineJoin: 'round',
      }).addTo(map);

      polyline.getLatLngs().forEach((ll) => bounds.extend(ll));
    }

    const createIcon = (bgColor, text) =>
      L.divIcon({
        className: 'route-marker',
        html: `<div style="background:${bgColor};width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:600;font-size:11px;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.25);">${text}</div>`,
        iconSize: [26, 26],
        iconAnchor: [13, 13],
      });

    if (waypoints?.current) {
      const p = [waypoints.current.lat, waypoints.current.lon];
      bounds.extend(p);
      L.marker(p, { icon: createIcon('#0284c7', 'A') })
        .addTo(map)
        .bindPopup(`<strong>Start</strong><br/>${waypoints.current.label}`);
    }

    if (waypoints?.pickup) {
      const p = [waypoints.pickup.lat, waypoints.pickup.lon];
      bounds.extend(p);
      L.marker(p, { icon: createIcon('#059669', 'P') })
        .addTo(map)
        .bindPopup(`<strong>Pickup (1 hr)</strong><br/>${waypoints.pickup.label}`);
    }

    if (waypoints?.dropoff) {
      const p = [waypoints.dropoff.lat, waypoints.dropoff.lon];
      bounds.extend(p);
      L.marker(p, { icon: createIcon('#dc2626', 'D') })
        .addTo(map)
        .bindPopup(`<strong>Dropoff (1 hr)</strong><br/>${waypoints.dropoff.label}`);
    }

    fuel_stops?.forEach((f) => {
      const p = [f.lat, f.lon];
      bounds.extend(p);
      L.marker(p, { icon: createIcon('#d97706', 'F') })
        .addTo(map)
        .bindPopup(`<strong>Fuel Stop</strong><br/>${f.location}<br/>${f.duration_minutes} min`);
    });

    rest_stops?.forEach((r) => {
      const p = [r.lat, r.lon];
      bounds.extend(p);
      const isRestart = r.reason.includes('34');
      L.marker(p, { icon: createIcon(isRestart ? '#ea580c' : '#7c3aed', isRestart ? 'R' : 'Z') })
        .addTo(map)
        .bindPopup(`<strong>${r.reason}</strong><br/>${r.location}<br/>${r.duration_hours} hrs`);
    });

    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [48, 48] });
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [tripData]);

  return (
    <div className={`map-panel${fullHeight ? ' map-panel-full' : ''}`}>
      <div className="map-legend">
        {LEGEND.map((item) => (
          <span key={item.label} className="legend-item">
            <span className="legend-dot" style={{ background: item.color }} />
            {item.label}
          </span>
        ))}
      </div>
      <div ref={mapRef} className="map-canvas" />

      <style>{`
        .map-panel {
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          overflow: hidden;
          box-shadow: var(--shadow-sm);
        }

        .map-panel-full {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-height: 0;
        }

        .map-legend {
          display: flex;
          flex-wrap: wrap;
          gap: 16px;
          padding: 12px 20px;
          border-bottom: 1px solid var(--color-border);
          background: #f8fafc;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.75rem;
          color: var(--color-text-secondary);
          font-weight: 500;
        }

        .legend-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          flex-shrink: 0;
        }

        .map-canvas {
          width: 100%;
          height: ${fullHeight ? '100%' : '520px'};
          min-height: 400px;
        }

        .route-marker {
          background: transparent !important;
          border: none !important;
        }
      `}</style>
    </div>
  );
}
