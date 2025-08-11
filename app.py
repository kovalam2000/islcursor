from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import numpy as np
from datetime import datetime, timedelta, timezone
from skyfield.api import EarthSatellite, load, wgs84
import math

app = Flask(__name__)
CORS(app)

# Load Skyfield timescale once
_ts = load.timescale()

EARTH_RADIUS_KM = 6378.137  # WGS84 equatorial radius
DEFAULT_COMM_RANGE_KM = 1000.0
DEFAULT_TIME_STEP_SEC = 300


class Satellite:
    def __init__(self, name: str, tle_line1: str, tle_line2: str):
        self.name = name
        self.tle_line1 = tle_line1.strip()
        self.tle_line2 = tle_line2.strip()
        self._sat = EarthSatellite(self.tle_line1, self.tle_line2, self.name)

    def get_position(self, dt: datetime):
        """Get satellite geodetic position and ECI vector at a specific UTC datetime.

        Returns a dict containing lat (deg), lon (deg), altitude (km), and eci_km [x,y,z].
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        t = _ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        geocentric = self._sat.at(t)

        # ECI position vector in km
        position_km = geocentric.position.km
        eci_vec = [float(position_km[0]), float(position_km[1]), float(position_km[2])]

        # Geodetic subpoint
        sp = wgs84.subpoint_of(geocentric)
        lat = float(sp.latitude.degrees)
        lon = float(sp.longitude.degrees)
        alt_km = float(sp.elevation.km)

        return {
            'lat': lat,
            'lon': lon,
            'altitude': alt_km,
            'eci_km': eci_vec,
        }


def calculate_distance_eci_km(r1_km, r2_km):
    """3D Euclidean distance between two ECI position vectors in km."""
    r1 = np.array(r1_km, dtype=float)
    r2 = np.array(r2_km, dtype=float)
    return float(np.linalg.norm(r2 - r1))


def is_earth_obstructed(r1_km, r2_km, earth_radius_km: float = EARTH_RADIUS_KM) -> bool:
    """Determine if Earth obstructs line-of-sight between two ECI position vectors.

    Uses closest approach from Earth's center (origin) to the line segment r(t)=r1+t*(r2-r1), t in [0,1].
    If the minimum distance from origin to the line segment is below Earth's radius, LoS is blocked.
    """
    r1 = np.array(r1_km, dtype=float)
    r2 = np.array(r2_km, dtype=float)
    d = r2 - r1
    d2 = float(np.dot(d, d))
    if d2 == 0.0:
        # Identical positions; treat as obstructed to be safe
        return True
    t_star = -float(np.dot(r1, d)) / d2
    t_star_clamped = max(0.0, min(1.0, t_star))
    closest = r1 + t_star_clamped * d
    min_dist_km = float(np.linalg.norm(closest))
    return min_dist_km < earth_radius_km


def calculate_interlink_windows(sat1: Satellite, sat2: Satellite, start_date: datetime, end_date: datetime,
                                time_step: int = DEFAULT_TIME_STEP_SEC, max_range_km: float = DEFAULT_COMM_RANGE_KM):
    """Calculate inter-satellite communication windows using SGP4 propagation with Earth obstruction."""
    interlink_windows = []
    current_date = start_date

    # Ensure timezone-aware UTC
    if current_date.tzinfo is None:
        current_date = current_date.replace(tzinfo=timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)

    while current_date <= end_date:
        pos1 = sat1.get_position(current_date)
        pos2 = sat2.get_position(current_date)

        r1 = pos1['eci_km']
        r2 = pos2['eci_km']

        if not is_earth_obstructed(r1, r2):
            distance_km = calculate_distance_eci_km(r1, r2)
            if distance_km <= max_range_km:
                interlink_windows.append({
                    'timestamp': current_date.isoformat(),
                    'sat1_pos': {k: pos1[k] for k in ['lat', 'lon', 'altitude']},
                    'sat2_pos': {k: pos2[k] for k in ['lat', 'lon', 'altitude']},
                    'distance': distance_km,
                    'can_communicate': True
                })

        current_date += timedelta(seconds=time_step)

    return interlink_windows


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/calculate-interlink', methods=['POST'])
def calculate_interlink():
    try:
        data = request.get_json()

        # Parse TLE data
        sat1_name = data.get('sat1_name', 'Satellite 1')
        sat1_tle1 = data['sat1_tle1']
        sat1_tle2 = data['sat1_tle2']

        sat2_name = data.get('sat2_name', 'Satellite 2')
        sat2_tle1 = data['sat2_tle1']
        sat2_tle2 = data['sat2_tle2']

        # Parse date range
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])

        # Optional parameters
        time_step = int(data.get('time_step', DEFAULT_TIME_STEP_SEC))
        max_range_km = float(data.get('max_range_km', DEFAULT_COMM_RANGE_KM))

        # Create satellite objects (validates TLEs implicitly)
        sat1 = Satellite(sat1_name, sat1_tle1, sat1_tle2)
        sat2 = Satellite(sat2_name, sat2_tle1, sat2_tle2)

        # Calculate interlink windows
        interlink_windows = calculate_interlink_windows(
            sat1, sat2, start_date, end_date, time_step=time_step, max_range_km=max_range_km
        )

        # Get initial positions for visualization
        initial_pos1 = sat1.get_position(start_date)
        initial_pos2 = sat2.get_position(start_date)

        return jsonify({
            'success': True,
            'interlink_windows': interlink_windows,
            'initial_positions': {
                'sat1': {k: initial_pos1[k] for k in ['lat', 'lon', 'altitude']},
                'sat2': {k: initial_pos2[k] for k in ['lat', 'lon', 'altitude']}
            },
            'total_windows': len(interlink_windows)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/validate-tle', methods=['POST'])
def validate_tle():
    try:
        data = request.get_json()
        tle_line1 = data['tle_line1']
        tle_line2 = data['tle_line2']

        # Attempt to create a satellite and compute a position to validate
        _ = EarthSatellite(tle_line1.strip(), tle_line2.strip(), 'test')
        now = datetime.now(timezone.utc)
        t = _ts.utc(now.year, now.month, now.day, now.hour, now.minute, now.second)
        _.at(t)  # propagate once

        return jsonify({
            'success': True,
            'message': 'TLE is valid'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
