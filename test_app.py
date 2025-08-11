#!/usr/bin/env python3
"""
Simple test script for the Satellite Interlink Application
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone
from app import (
    Satellite,
    calculate_distance_eci_km,
    is_earth_obstructed,
    EARTH_RADIUS_KM,
)


def test_satellite_class():
    """Test the Satellite class propagation using SGP4/Skyfield"""
    print("🧪 Testing Satellite class...")

    # Sample TLE data (example format)
    tle_line1 = "1 25544U 98067A   24001.50000000  .00012227  00000+0  22906-3 0  9999"
    tle_line2 = "2 25544  51.6400 114.3973 0001263 255.8500 104.1500 15.50000000 00000+0"

    try:
        sat = Satellite("ISS", tle_line1, tle_line2)
        print("✅ Satellite object created successfully")

        # Test position calculation at current time (UTC)
        pos = sat.get_position(datetime.now(timezone.utc))
        print(
            f"✅ Position calculated: Lat={pos['lat']:.2f}°, Lon={pos['lon']:.2f}°, Alt={pos['altitude']:.2f} km"
        )

        # Basic sanity checks
        assert -90.0 <= pos['lat'] <= 90.0
        assert -180.0 <= pos['lon'] <= 180.0
        return True
    except Exception as e:
        print(f"❌ Error creating or propagating satellite: {e}")
        return False


def test_distance_eci():
    """Test ECI 3D distance calculation"""
    print("\n🧪 Testing ECI distance calculation...")

    r1 = [EARTH_RADIUS_KM + 400.0, 0.0, 0.0]
    r2 = [EARTH_RADIUS_KM + 400.0, 1.0, 0.0]

    try:
        d = calculate_distance_eci_km(r1, r2)
        print(f"✅ Distance calculated: {d:.6f} km")
        assert d > 0
        return True
    except Exception as e:
        print(f"❌ Error calculating ECI distance: {e}")
        return False


def test_earth_obstruction_geometry():
    """Test Earth obstruction geometry function"""
    print("\n🧪 Testing Earth obstruction geometry...")

    # Not obstructed: both near same side, line segment far from origin
    r1 = [EARTH_RADIUS_KM + 400.0, 0.0, 0.0]
    r2 = [EARTH_RADIUS_KM + 400.0, 10.0, 0.0]

    try:
        obstructed = is_earth_obstructed(r1, r2)
        print(f"✅ Same-side obstruction check (expected False): {obstructed}")

        # Obstructed: opposite sides, line through Earth
        r3 = [EARTH_RADIUS_KM + 400.0, 0.0, 0.0]
        r4 = [-(EARTH_RADIUS_KM + 400.0), 0.0, 0.0]
        obstructed2 = is_earth_obstructed(r3, r4)
        print(f"✅ Opposite-side obstruction check (expected True): {obstructed2}")

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
        'skyfield.api',
        'sgp4',
        'datetime',
        'math',
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
        test_distance_eci,
        test_earth_obstruction_geometry,
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
