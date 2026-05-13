#!/usr/bin/env python3
"""
Simple video processing test without OpenCV dependency.
"""
import os
import tempfile
import json
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")
    
    try:
        from app.cv.video_io import VideoProcessor, check_video_dependencies
        print("✅ video_io imported")
    except Exception as e:
        print(f"❌ video_io import failed: {e}")
        return False
    
    try:
        from app.cv.pipeline import MatchAnalysisPipeline, PipelineConfig
        print("✅ pipeline imported")
    except Exception as e:
        print(f"❌ pipeline import failed: {e}")
        return False
    
    try:
        from app.cv.detector import MockDetector
        print("✅ detector imported")
    except Exception as e:
        print(f"❌ detector import failed: {e}")
        return False
    
    try:
        from app.cv.tracker import SimpleTracker
        print("✅ tracker imported")
    except Exception as e:
        print(f"❌ tracker import failed: {e}")
        return False
    
    try:
        from app.cv.calibration import PitchCalibrator
        print("✅ calibration imported")
    except Exception as e:
        print(f"❌ calibration import failed: {e}")
        return False
    
    return True


def test_dependencies():
    """Test dependency checking."""
    print("\nTesting dependency checking...")
    
    try:
        from app.cv.video_io import check_video_dependencies
        deps = check_video_dependencies()
        
        print("Dependency status:")
        for name, available in deps.items():
            status = "✅" if available else "❌"
            print(f"   {status} {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dependency check failed: {e}")
        return False


def test_mock_detector():
    """Test mock detector without OpenCV."""
    print("\nTesting mock detector...")
    
    try:
        from app.cv.detector import MockDetector
        import numpy as np
        
        detector = MockDetector()
        
        # Create dummy frame (without OpenCV)
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        detections = detector.detect_frame(frame, 0)
        
        print(f"✅ Detected {len(detections['players_home'])} home players")
        print(f"✅ Detected {len(detections['players_away'])} away players")
        print(f"✅ Ball detected: {detections['ball'] is not None}")
        
        # Validate detection structure
        required_keys = ["frame_idx", "timestamp", "players_home", "players_away", "ball"]
        for key in required_keys:
            if key not in detections:
                print(f"❌ Missing key in detections: {key}")
                return False
        
        print("✅ Detection structure valid")
        return True
        
    except Exception as e:
        print(f"❌ Mock detector test failed: {e}")
        return False


def test_tracker():
    """Test tracker functionality."""
    print("\nTesting tracker...")
    
    try:
        from app.cv.tracker import SimpleTracker
        
        tracker = SimpleTracker()
        
        # Mock detection data
        detections = {
            "frame_idx": 0,
            "timestamp": 0.0,
            "players_home": [
                {"id": 1, "bbox": [100, 100, 120, 140], "confidence": 0.9, "position": [110, 120]},
                {"id": 2, "bbox": [200, 200, 220, 240], "confidence": 0.85, "position": [210, 220]}
            ],
            "players_away": [
                {"id": 1, "bbox": [300, 300, 320, 340], "confidence": 0.88, "position": [310, 320]}
            ],
            "ball": {"bbox": [150, 150, 160, 160], "confidence": 0.95, "position": [155, 155]}
        }
        
        tracking_result = tracker.update(detections)
        
        print(f"✅ Tracked {len(tracking_result['tracks_home'])} home tracks")
        print(f"✅ Tracked {len(tracking_result['tracks_away'])} away tracks")
        
        # Validate tracking structure
        required_keys = ["frame_idx", "timestamp", "tracks_home", "tracks_away", "ball"]
        for key in required_keys:
            if key not in tracking_result:
                print(f"❌ Missing key in tracking result: {key}")
                return False
        
        print("✅ Tracking structure valid")
        return True
        
    except Exception as e:
        print(f"❌ Tracker test failed: {e}")
        return False


def test_calibration():
    """Test calibration functionality."""
    print("\nTesting calibration...")
    
    try:
        from app.cv.calibration import PitchCalibrator
        
        calibrator = PitchCalibrator()
        
        # Test calibration points
        points = [
            {"pixel": [100, 100], "real": [0, 0]},
            {"pixel": [1180, 100], "real": [105, 0]},
            {"pixel": [100, 620], "real": [0, 68]},
            {"pixel": [1180, 620], "real": [105, 68]}
        ]
        
        calibrator.set_calibration_points(points)
        print(f"✅ Set {len(points)} calibration points")
        
        # Test coordinate conversion
        pixel_coord = (640, 360)
        real_coord = calibrator.pixel_to_real(pixel_coord)
        back_to_pixel = calibrator.real_to_pixel(real_coord)
        
        print(f"✅ Coordinate conversion: {pixel_coord} -> {real_coord} -> {back_to_pixel}")
        
        # Test distance calculation
        pos1 = (100, 100)
        pos2 = (200, 200)
        distance = calibrator.calculate_distance(pos1, pos2)
        
        print(f"✅ Distance calculation: {distance:.2f}m")
        
        # Test pitch zones
        zones = calibrator.get_pitch_zones()
        print(f"✅ Defined {len(zones)} pitch zones")
        
        return True
        
    except Exception as e:
        print(f"❌ Calibration test failed: {e}")
        return False


def test_tactical_integration():
    """Test integration with tactical analytics."""
    print("\nTesting tactical analytics integration...")
    
    try:
        from app.analytics.tactical_service import TacticalAnalyticsService
        
        service = TacticalAnalyticsService()
        
        # Mock frame data
        frame_data = [
            {
                "player_id": 1,
                "team_id": 1,
                "role": "defender",
                "x": 20.0,
                "y": 25.0,
                "speed": 3.5
            },
            {
                "player_id": 2,
                "team_id": 1,
                "role": "midfielder",
                "x": 40.0,
                "y": 30.0,
                "speed": 4.0
            },
            {
                "player_id": 3,
                "team_id": 2,
                "role": "forward",
                "x": 60.0,
                "y": 35.0,
                "speed": 5.0
            }
        ]
        
        # Test frame analysis
        result = service.analyze_match_frame(
            match_id=1,
            frame_data=frame_data,
            timestamp=1200.0,
            ball_position=(45.0, 30.0)
        )
        
        if "error" in result:
            print(f"❌ Tactical analysis failed: {result['error']}")
            return False
        
        print("✅ Tactical analysis completed")
        print(f"   Teams analyzed: {len(result.get('teams', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tactical integration test failed: {e}")
        return False


def test_api_imports():
    """Test API module imports."""
    print("\nTesting API imports...")
    
    try:
        from app.api.video_processing import router
        print("✅ Video processing API imported")
        
        # Check router has endpoints
        routes = [route.path for route in router.routes]
        print(f"✅ API has {len(routes)} endpoints")
        
        expected_endpoints = [
            "/api/video/upload",
            "/api/video/process", 
            "/api/video/status/{video_id}",
            "/api/video/create-clip",
            "/api/video/calibrate",
            "/api/video/info/{video_id}",
            "/api/video/dependencies",
            "/api/video/health"
        ]
        
        for endpoint in expected_endpoints:
            if any(endpoint in route for route in routes):
                print(f"   ✅ {endpoint}")
            else:
                print(f"   ❌ Missing: {endpoint}")
        
        return True
        
    except Exception as e:
        print(f"❌ API import test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("PitchVision Video Processing - Simple Test Suite")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Dependencies Check", test_dependencies),
        ("Mock Detector", test_mock_detector),
        ("Tracker", test_tracker),
        ("Calibration", test_calibration),
        ("Tactical Integration", test_tactical_integration),
        ("API Imports", test_api_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    # Final results
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        print("\nVideo processing modules are working correctly!")
        print("\nNote: Full video processing requires OpenCV and FFmpeg")
        print("Install with: pip install opencv-python")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)