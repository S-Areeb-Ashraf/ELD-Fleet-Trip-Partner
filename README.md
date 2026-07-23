# Spotter AI - FMCSA ELD & GIS Trip Planner

A full-stack logistics application built with Django REST Framework, React, Leaflet, and Pillow to calculate optimal truck routes, schedule FMCSA-compliant Hours of Service (HOS) rest breaks, and generate official FMCSA Driver Daily Log PNGs.

---

## Technical Stack

- **Frontend**: React, Tailwind CSS, Leaflet (GIS Map rendering using free CartoDB & OpenStreetMap tiles)
- **Backend**: Django 5.2, Django REST Framework, Python 3.13, Pillow (image manipulation)
- **Free APIs**:
  - Geocoding: OpenStreetMap Nominatim
  - Routing: OpenRouteService & OSRM (with automatic Haversine fallback)
  - Map Visualization: Leaflet.js
- **HTTP Client**: Native Browser `fetch` API (No Axios per specification)

---

## Key Features

1. **Pure-Python HOS Engine (`hos_engine.py`)**:
   - Framework-agnostic state machine simulating FMCSA property-carrying 70-hour / 8-day rolling window rules.
   - Enforces 11-hour daily driving limit and 14-hour duty window limit.
   - Mandatory 30-minute rest break after 8 hours of cumulative driving.
   - Automatic insertion of 10-hour daily Off-Duty resets and 34-hour Off-Duty cycle restarts when the 70-hour balance is exhausted.
   - Calendar-day splitting (midnight-to-midnight) for accurate daily log attribution.

2. **Canvas-Accurate ELD Log Generator (`log_generator.py`)**:
   - Renders exact 24-hour graph grid lines, status transition vertical connectors, location remarks, header fields, and 70-hour rolling recap totals.
   - Draws directly onto the single canonical FMCSA Driver Daily Log template image (`log_template.png`).
   - Produces one high-resolution PNG image per 24-hour calendar day (`daily_log_day_1.png`, `daily_log_day_2.png`, etc.).

3. **Interactive GIS Map & Navigation**:
   - Visualizes complete route geometry polylines.
   - Displays custom markers for Origin, Pickup (1 hr), Dropoff (1 hr), Fuel Stops (every 1,000 mi), 10-hr Resets, and 34-hr Restarts.
   - Displays step-by-step turn-by-turn navigation instructions.

---

## Assumptions & Simplifications

Per assessment guidelines, the following explicit business rules and simplifications are applied:

1. **No Sleeper-Berth Split Provision**: Sleeper berth pairing rules from FMCSA guide are excluded; off-duty resets are modeled strictly as single continuous 10-hour (or 34-hour restart) Off-Duty blocks.
2. **No Adverse Driving Conditions Exception**: The 2-hour adverse driving extension exception is not modeled.
3. **Fixed Fuel Stop Duration**: Fuel stops are scheduled at least once every 1,000 miles of driving and assumed to take exactly 30 minutes, logged as On Duty (Not Driving).
4. **Single Canonical Log Template**: All generated daily log PNGs are rendered onto the primary full-page template (`media__1784726143161.png`).
5. **Fixed Pickup & Dropoff Durations**: Pickup takes 1 hour On Duty (Not Driving) before driving begins. Dropoff takes 1 hour On Duty (Not Driving) at trip end.

---

## Quick Start & Setup Instructions

### Backend (Django REST API)

1. Navigate to the Django project directory:
   ```bash
   cd trip_planner
   ```

2. Install Python dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

3. Run database migrations:
   ```bash
   python manage.py migrate
   ```

4. Run unit tests to verify HOS Engine against FMCSA worked example:
   ```bash
   python -m unittest api.tests
   ```

5. Start Django development server (runs on port 8000):
   ```bash
   python manage.py runserver 8000
   ```

### Frontend (React + Vite)

1. Open a second terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Start Vite development server (runs on port 5173):
   ```bash
   npx vite
   ```

3. Open your browser and navigate to `http://localhost:5173`.

---

## API Documentation

### `POST /plan-trip/`

**Request Payload:**
```json
{
  "current_location": "Richmond, VA",
  "pickup_location": "Baltimore, MD",
  "dropoff_location": "Newark, NJ",
  "current_cycle_used": 0.0
}
```

**Response Example:**
See [example_response.json](./example_response.json) in the repository root.

```json
{
  "distance": 325.3,
  "duration": 6.78,
  "waypoints": { ... },
  "directions": [ ... ],
  "route_geometry": [ ... ],
  "fuel_stops": [ ... ],
  "rest_stops": [ ... ],
  "daily_logs": [
    {
      "day_number": 1,
      "date": "2026-07-22",
      "png_url": "/media/logs/daily_log_day_1.png",
      "total_driving_hours": 6.78,
      "total_on_duty_hours": 2.5,
      "total_off_duty_hours": 14.72,
      "total_miles_driven": 406.8
    }
  ]
}
```

---

## Project Structure

```
Spotter AI Assessment/
├── trip_planner/
│   ├── manage.py
│   ├── trip_planner/
│   │   ├── settings.py
│   │   └── urls.py
│   ├── api/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   └── services/
│   │       ├── hos_engine.py
│   │       ├── route_service.py
│   │       ├── trip_scheduler.py
│   │       ├── log_generator.py
│   │       └── utils.py
│   └── static/
│       └── templates/
│           └── log_template.png
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── TripForm.jsx
│   │       ├── SummaryCards.jsx
│   │       ├── RouteMap.jsx
│   │       ├── DirectionsList.jsx
│   │       └── LogViewer.jsx
├── example_response.json
├── requirements.txt
└── README.md
```
