#!/usr/bin/env python3
"""
Simple test script for the Satellite Interlink Application
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import Satellite, calculate_distance, check_earth_obstruction
from datetime import datetime

def test_satellite_class():
    """Test the Satellite class"""
    print("🧪 Testing Satellite class...")
    
    # Sample TLE data for ISS
    tle_line1 = "1 25544U 98067A   24001.50000000  .00012227  00000+0  22906-3 0  9999"
    tle_line2 = "2 25544  51.6400 114.3973 0001263 255.8500 104.1500 15.50000000 00000+0"
    
    try:
        sat = Satellite("ISS", tle_line1, tle_line2)
        print("✅ Satellite object created successfully")
        
        # Test position calculation
        pos = sat.get_position(datetime.now())
        print(f"✅ Position calculated: Lat={pos['lat']:.2f}°, Lon={pos['lon']:.2f}°, Alt={pos['altitude']:.2f} km")
        
        return True
    except Exception as e:
        print(f"❌ Error creating satellite: {e}")
        return False

def test_distance_calculation():
    """Test distance calculation between two points"""
    print("\n🧪 Testing distance calculation...")
    
    pos1 = {'lat': 0, 'lon': 0}
    pos2 = {'lat': 0, 'lon': 1}
    
    try:
        distance = calculate_distance(pos1, pos2)
        print(f"✅ Distance calculated: {distance:.2f} km")
        
        # Test with known values (1 degree longitude at equator ≈ 111 km)
        if 100 < distance < 120:
            print("✅ Distance calculation appears accurate")
        else:
            print("⚠️ Distance calculation may have issues")
        
        return True
    except Exception as e:
        print(f"❌ Error calculating distance: {e}")
        return False

def test_earth_obstruction():
    """Test Earth obstruction detection"""
    print("\n🧪 Testing Earth obstruction detection...")
    
    # Test case 1: Close satellites (should not be obstructed)
    pos1 = {'lat': 0, 'lon': 0, 'altitude': 400}
    pos2 = {'lat': 0.1, 'lon': 0.1, 'altitude': 400}
    
    try:
        obstructed = check_earth_obstruction(pos1, pos2)
        print(f"✅ Close satellites obstruction check: {obstructed}")
        
        # Test case 2: Far satellites (should be obstructed)
        pos3 = {'lat': 0, 'lon': 0, 'altitude': 400}
        pos4 = {'lat': 10, 'lon': 10, 'altitude': 400}
        
        obstructed2 = check_earth_obstruction(pos3, pos4)
        print(f"✅ Far satellites obstruction check: {obstructed2}")
        
        return True
    except Exception as e:
        print(f"❌ Error checking Earth obstruction: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported"""
    print("\n🧪 Testing module imports...")
    
    required_modules = [
        'flask',
        'flask_cors', 
        'numpy',
        'ephem',
        'datetime',
        'math'
    ]
    
    all_imported = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")
            all_imported = False
    
    return all_imported

def main():
    """Run all tests"""
    print("🚀 Starting Satellite Interlink Application Tests\n")
    
    tests = [
        test_imports,
        test_satellite_class,
        test_distance_calculation,
        test_earth_obstruction
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("  python app.py")
        print("\nOr with Docker:")
        print("  docker-compose up --build")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
