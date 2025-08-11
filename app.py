from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import numpy as np
from datetime import datetime, timedelta
import ephem
import json
import math

app = Flask(__name__)
CORS(app)

class Satellite:
    def __init__(self, name, tle_line1, tle_line2):
        self.name = name
        self.tle_line1 = tle_line1
        self.tle_line2 = tle_line2
        self.satellite = ephem.readtle(name, tle_line1, tle_line2)
    
    def get_position(self, date):
        """Get satellite position at a specific date"""
        self.satellite.compute(date)
        return {
            'lat': float(self.satellite.sublat) * 180 / math.pi,
            'lon': float(self.satellite.sublong) * 180 / math.pi,
            'altitude': float(self.satellite.elevation) / 1000.0,  # Convert to km
            'azimuth': float(self.satellite.az) * 180 / math.pi
        }

def calculate_distance(pos1, pos2):
    """Calculate distance between two positions on Earth"""
    lat1, lon1 = math.radians(pos1['lat']), math.radians(pos1['lon'])
    lat2, lon2 = math.radians(pos2['lat']), math.radians(pos2['lon'])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return 6371 * c  # Earth radius in km

def check_earth_obstruction(pos1, pos2):
    """Check if Earth obstructs the line of sight between satellites"""
    # Simple Earth obstruction check based on elevation angles
    # This is a simplified model - in reality, you'd need more complex calculations
    
    # Calculate the angle from each satellite to the other
    # If the angle is too low, Earth blocks the view
    
    # For now, we'll use a simple heuristic based on distance and altitude
    distance = calculate_distance(pos1, pos2)
    
    # If satellites are too far apart relative to their altitudes, Earth blocks view
    if pos1['altitude'] < 100 or pos2['altitude'] < 100:  # Low Earth orbit
        max_distance = 2000  # km
        if distance > max_distance:
            return True
    
    return False

def calculate_interlink_windows(sat1, sat2, start_date, end_date, time_step=300):
    """Calculate interlink communication windows between two satellites"""
    interlink_windows = []
    current_date = start_date
    
    while current_date <= end_date:
        pos1 = sat1.get_position(current_date)
        pos2 = sat2.get_position(current_date)
        
        # Check if Earth obstructs the view
        if not check_earth_obstruction(pos1, pos2):
            # Calculate distance between satellites
            distance = calculate_distance(pos1, pos2)
            
            # Check if satellites are within communication range
            # Assuming typical satellite communication range of 1000 km
            if distance <= 1000:
                interlink_windows.append({
                    'timestamp': current_date.isoformat(),
                    'sat1_pos': pos1,
                    'sat2_pos': pos2,
                    'distance': distance,
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
        
        # Create satellite objects
        sat1 = Satellite(sat1_name, sat1_tle1, sat1_tle2)
        sat2 = Satellite(sat2_name, sat2_tle1, sat2_tle2)
        
        # Calculate interlink windows
        interlink_windows = calculate_interlink_windows(sat1, sat2, start_date, end_date)
        
        # Get initial positions for visualization
        initial_pos1 = sat1.get_position(start_date)
        initial_pos2 = sat2.get_position(start_date)
        
        return jsonify({
            'success': True,
            'interlink_windows': interlink_windows,
            'initial_positions': {
                'sat1': initial_pos1,
                'sat2': initial_pos2
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
        
        # Try to create a satellite object to validate TLE
        test_sat = ephem.readtle('test', tle_line1, tle_line2)
        test_sat.compute(datetime.now())
        
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
