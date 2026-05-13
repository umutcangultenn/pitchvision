#!/usr/bin/env python3
"""
Video processing pipeline test.
"""
import os
import tempfile
import numpy as np
import cv2
from pathlib import Path
import json

from app.cv.video_io import VideoProcessor, check_video_dependencies
from app.cv.pipeline import MatchAnalysisPipeline, PipelineConfig
from app.cv.detector import MockDetector
from app.cv.tracker import SimpleTracker
from app.cv.calibration import PitchCalibrator


def create_test_video(output_path: str, duration: int = 10, fps: int = 25) -> bool:
    """
    Create a test video file.
    
    Args:
        output_path: Output video path
        duration: Video duration in seconds
        fps: Frames per second
        
    Returns:
        bool: Success status
    """
    try:
        # Video properties
        width, height = 1280, 720
        total_frames = duration * fps
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not writer.isOpened():
            print(f"❌ Cannot create video writer for {output_path}")
            return False
        
        # Generate frames
        for frame_idx in range(total_frames):
            # Create a simple animated frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add background (green field)
            frame[:, :] = [34, 139, 34]  # Forest green
            
            # Add moving elements
            t = frame_idx / fps
            
            # Moving ball
            ball_x = int(width * 0.2 + (width * 0.6) * (t / duration))
            ball_y = int(height * 0.5 + 50 * np.sin(t * 2))
            cv2.circle(frame, (ball_x, ball_y), 10, (255, 255, 255), -1)
            
            # Add some "players"
            for i in range(6):
                player_x = int(width * (0.1 + i * 0.15))
                player_y = int(height * (0.3 + 0.1 * np.sin(t + i)))
                color = (255, 0, 0) if i < 3 else (0, 0, 255)  # Red and blue teams
                cv2.circle(frame, (player_x, player_y), 15, color, -1)
            
            # Add frame number
            cv2.putText(frame, f"Frame {frame_idx}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            writer.write(frame)
        
        writer.release()
        print(f"✅ Test video created: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test video: {e}")
        return False


def test_video_processor():
    """Test video processor functionality."""
    print("\n" + "="*50)
    print("Testing Video Processor")
    print("="*50)
    
    processor = VideoProcessor()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test video
        video_path = os.path.join(temp_dir, "test_video.mp4")
        if not create_test_video(video_path):
            return False
        
        # Test video validation
        print("1. Testing video validation...")
        validation = processor.validate_video(video_path)
        
        if validation["valid"]:
            print("✅ Video validation passed")
            metadata = validation["metadata"]
            print(f"   Duration: {metadata.duration:.1f}s")
            print(f"   Resolution: {metadata.width}x{metadata.height}")
            print(f"   FPS: {metadata.fps:.1f}")
            print(f"   Total frames: {metadata.total_frames}")
        else:
            print(f"❌ Video validation failed: {validation['error']}")
            return False
        
        # Test frame extraction
        print("\n2. Testing frame extraction...")
        frames_dir = os.path.join(temp_dir, "frames")
        
        frame_count = 0
        for frame_idx, frame in processor.extract_frames(video_path, frames_dir, frame_interval=5, max_frames=10):
            frame_count += 1
            if frame_count <= 3:  # Show first 3 frames
                print(f"   Extracted frame {frame_idx}: shape {frame.shape}")
        
        print(f"✅ Extracted {frame_count} frames")
        
        # Test thumbnail generation
        print("\n3. Testing thumbnail generation...")
        thumbnail_path = os.path.join(temp_dir, "thumbnail.jpg")
        thumb_result = processor.generate_thumbnail(video_path, 2.0, thumbnail_path)
        
        if thumb_result["success"]:
            print("✅ Thumbnail generated successfully")
        else:
            print(f"❌ Thumbnail generation failed: {thumb_result['error']}")
        
        # Test clip creation (if FFmpeg available)
        deps = check_video_dependencies()
        if deps["ffmpeg"]:
            print("\n4. Testing clip creation...")
            clip_path = os.path.join(temp_dir, "clip.mp4")
            clip_result = processor.create_video_clip(video_path, 2.0, 5.0, clip_path)
            
            if clip_result["success"]:
                print("✅ Video clip created successfully")
                print(f"   Duration: {clip_result['duration']:.1f}s")
            else:
                print(f"❌ Clip creation failed: {clip_result['error']}")
        else:
            print("\n4. ⚠️ Skipping clip creation (FFmpeg not available)")
    
    return True


def test_detection_and_tracking():
    """Test detection and tracking components."""
    print("\n" + "="*50)
    print("Testing Detection and Tracking")
    print("="*50)
    
    # Test detector
    print("1. Testing mock detector...")
    detector = MockDetector()
    
    # Create dummy frame
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    detections = detector.detect_frame(frame, 0)
    
    print(f"✅ Detected {len(detections['players_home'])} home players")
    print(f"✅ Detected {len(detections['players_away'])} away players")
    print(f"✅ Ball detected: {detections['ball'] is not None}")
    
    # Test tracker
    print("\n2. Testing tracker...")
    tracker = SimpleTracker()
    
    tracking_result = tracker.update(detections)
    
    print(f"✅ Tracked {len(tracking_result['tracks_home'])} home tracks")
    print(f"✅ Tracked {len(tracking_result['tracks_away'])} away tracks")
    
    return True


def test_calibration():
    """Test pitch calibration."""
    print("\n" + "="*50)
    print("Testing Pitch Calibration")
    print("="*50)
    
    calibrator = PitchCalibrator()
    
    # Test calibration points
    print("1. Testing calibration points...")
    
    # Mock calibration points (corners of the pitch)
    points = [
        {"pixel": [100, 100], "real": [0, 0]},      # Top-left
        {"pixel": [1180, 100], "real": [105, 0]},   # Top-right
        {"pixel": [100, 620], "real": [0, 68]},     # Bottom-left
        {"pixel": [1180, 620], "real": [105, 68]}   # Bottom-right
    ]
    
    calibrator.set_calibration_points(points)
    print(f"✅ Set {len(points)} calibration points")
    
    # Test coordinate conversion
    print("\n2. Testing coordinate conversion...")
    
    pixel_coord = (640, 360)  # Center of frame
    real_coord = calibrator.pixel_to_real(pixel_coord)
    back_to_pixel = calibrator.real_to_pixel(real_coord)
    
    print(f"   Pixel: {pixel_coord} -> Real: {real_coord} -> Pixel: {back_to_pixel}")
    
    # Test distance calculation
    print("\n3. Testing distance calculation...")
    
    pos1 = (100, 100)
    pos2 = (200, 200)
    distance = calibrator.calculate_distance(pos1, pos2)
    
    print(f"   Distance between {pos1} and {pos2}: {distance:.2f}m")
    
    # Test pitch zones
    print("\n4. Testing pitch zones...")
    zones = calibrator.get_pitch_zones()
    print(f"✅ Defined {len(zones)} pitch zones")
    
    return True


def test_complete_pipeline():
    """Test complete processing pipeline."""
    print("\n" + "="*50)
    print("Testing Complete Pipeline")
    print("="*50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test video
        video_path = os.path.join(temp_dir, "test_match.mp4")
        if not create_test_video(video_path, duration=5):  # Short video for testing
            return False
        
        # Create pipeline
        output_dir = os.path.join(temp_dir, "output")
        config = PipelineConfig(
            frame_interval=5,  # Process every 5th frame
            max_frames=10,     # Limit to 10 frames
            save_frames=True,
            enable_tactical_analysis=True
        )
        
        pipeline = MatchAnalysisPipeline(output_dir, config)
        
        # Set up progress tracking
        progress_updates = []
        
        def progress_callback(progress):
            progress_updates.append({
                "status": progress.status.value,
                "progress": progress.progress_percent,
                "step": progress.current_step
            })
            print(f"   Progress: {progress.progress_percent:.1f}% - {progress.current_step}")
        
        pipeline.set_progress_callback(progress_callback)
        
        # Set mock calibration
        calibration_points = [
            {"pixel": [100, 100], "real": [0, 0]},
            {"pixel": [1180, 100], "real": [105, 0]},
            {"pixel": [100, 620], "real": [0, 68]},
            {"pixel": [1180, 620], "real": [105, 68]}
        ]
        pipeline.set_calibration(calibration_points)
        
        print("1. Processing match video...")
        result = pipeline.process_match_video(video_path, match_id=1)
        
        if result.success:
            print("✅ Pipeline processing completed successfully")
            print(f"   Processing time: {result.processing_time:.2f}s")
            print(f"   Processed frames: {result.processed_frames}/{result.total_frames}")
            
            # Check output files
            if result.detections_path and os.path.exists(result.detections_path):
                print("✅ Detections saved")
            
            if result.tracking_path and os.path.exists(result.tracking_path):
                print("✅ Tracking data saved")
            
            if result.analytics_path and os.path.exists(result.analytics_path):
                print("✅ Analytics data saved")
                
                # Load and check analytics data
                with open(result.analytics_path, 'r') as f:
                    analytics_data = json.load(f)
                print(f"   Analytics frames: {len(analytics_data)}")
            
            # Test match summary
            print("\n2. Generating match summary...")
            summary = pipeline.get_match_summary(match_id=1)
            
            if "error" not in summary:
                print("✅ Match summary generated")
                print(f"   Total alerts: {summary.get('total_alerts', 0)}")
            else:
                print(f"❌ Match summary failed: {summary['error']}")
            
        else:
            print(f"❌ Pipeline processing failed: {result.error_message}")
            return False
    
    return True


def main():
    """Run all video processing tests."""
    print("PitchVision Video Processing Pipeline Test")
    print("=" * 60)
    
    # Check dependencies
    print("Checking dependencies...")
    deps = check_video_dependencies()
    
    for name, available in deps.items():
        status = "✅" if available else "❌"
        print(f"   {status} {name}")
    
    if not deps["opencv"]:
        print("❌ OpenCV not available - cannot run tests")
        return False
    
    # Run tests
    tests = [
        ("Video Processor", test_video_processor),
        ("Detection and Tracking", test_detection_and_tracking),
        ("Calibration", test_calibration),
        ("Complete Pipeline", test_complete_pipeline)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} - PASSED")
            else:
                print(f"\n❌ {test_name} - FAILED")
        except Exception as e:
            print(f"\n❌ {test_name} - ERROR: {e}")
    
    # Final results
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        print("\nVideo processing pipeline is working correctly!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)