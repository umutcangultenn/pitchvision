"""
Complete video processing pipeline for PitchVision.
Integrates detection, tracking, calibration, and tactical analytics.
"""
import numpy as np
import os
import json
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

# Try to import OpenCV, use mock if not available
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from .video_io import VideoProcessor, ProcessingStatus, ProcessingProgress
from .detector import get_detector
from .tracker import SimpleTracker
from .calibration import PitchCalibrator
from ..analytics.tactical_service import TacticalAnalyticsService
from ..analytics.types import TrackPoint, PlayerRole

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Pipeline configuration."""
    frame_interval: int = 1  # Process every N frames
    max_frames: Optional[int] = None
    save_frames: bool = False
    save_detections: bool = True
    save_tracking: bool = True
    save_analytics: bool = True
    enable_tactical_analysis: bool = True
    output_video: bool = False
    video_overlay: bool = True


@dataclass
class ProcessingResult:
    """Complete processing result."""
    match_id: int
    video_path: str
    processing_time: float
    total_frames: int
    processed_frames: int
    success: bool
    error_message: Optional[str] = None
    
    # Output paths
    detections_path: Optional[str] = None
    tracking_path: Optional[str] = None
    analytics_path: Optional[str] = None
    output_video_path: Optional[str] = None
    
    # Statistics
    detection_stats: Optional[Dict[str, Any]] = None
    tracking_stats: Optional[Dict[str, Any]] = None
    analytics_stats: Optional[Dict[str, Any]] = None


class MatchAnalysisPipeline:
    """Complete match analysis pipeline."""
    
    def __init__(self, 
                 output_dir: str,
                 config: Optional[PipelineConfig] = None):
        """
        Initialize pipeline.
        
        Args:
            output_dir: Directory for output files
            config: Pipeline configuration
        """
        self.output_dir = output_dir
        self.config = config or PipelineConfig()
        
        # Initialize components
        self.video_processor = VideoProcessor()
        self.detector = get_detector()
        self.tracker = SimpleTracker()
        self.calibrator = PitchCalibrator()
        self.tactical_service = TacticalAnalyticsService()
        
        # Progress tracking
        self.progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
        self.current_progress = ProcessingProgress(
            status=ProcessingStatus.PENDING,
            current_frame=0,
            total_frames=0,
            progress_percent=0.0
        )
        
        # Results storage
        self.detections_data = []
        self.tracking_data = []
        self.analytics_data = []
        
        # Thread safety
        self._lock = threading.Lock()
        
        os.makedirs(output_dir, exist_ok=True)
    
    def set_progress_callback(self, callback: Callable[[ProcessingProgress], None]):
        """Set progress callback function."""
        self.progress_callback = callback
    
    def set_calibration(self, calibration_points: List[Dict[str, Any]]):
        """Set pitch calibration points."""
        self.calibrator.set_calibration_points(calibration_points)
    
    def _update_progress(self, 
                        status: ProcessingStatus,
                        current_frame: int = 0,
                        total_frames: int = 0,
                        step: str = ""):
        """Update processing progress."""
        with self._lock:
            self.current_progress.status = status
            self.current_progress.current_frame = current_frame
            self.current_progress.total_frames = total_frames
            self.current_progress.current_step = step
            
            if total_frames > 0:
                self.current_progress.progress_percent = (current_frame / total_frames) * 100
            
            if self.progress_callback:
                self.progress_callback(self.current_progress)
    
    def process_match_video(self, 
                           video_path: str, 
                           match_id: int) -> ProcessingResult:
        """
        Process complete match video.
        
        Args:
            video_path: Path to match video
            match_id: Match ID
            
        Returns:
            ProcessingResult: Complete processing result
        """
        start_time = datetime.now()
        
        try:
            # Validate video
            validation = self.video_processor.validate_video(video_path)
            if not validation["valid"]:
                return ProcessingResult(
                    match_id=match_id,
                    video_path=video_path,
                    processing_time=0.0,
                    total_frames=0,
                    processed_frames=0,
                    success=False,
                    error_message=validation["error"]
                )
            
            metadata = validation["metadata"]
            total_frames = metadata.total_frames
            
            self._update_progress(
                ProcessingStatus.EXTRACTING,
                0, total_frames,
                "Initializing video processing"
            )
            
            # Create output directories
            match_output_dir = os.path.join(self.output_dir, f"match_{match_id}")
            os.makedirs(match_output_dir, exist_ok=True)
            
            frames_dir = os.path.join(match_output_dir, "frames")
            if self.config.save_frames:
                os.makedirs(frames_dir, exist_ok=True)
            
            # Process frames
            processed_frames = 0
            
            for frame_idx, frame in self.video_processor.extract_frames(
                video_path, frames_dir, self.config.frame_interval, self.config.max_frames
            ):
                # Update progress
                self._update_progress(
                    ProcessingStatus.DETECTING,
                    frame_idx, total_frames,
                    f"Processing frame {frame_idx}"
                )
                
                # Detection
                detections = self.detector.detect_frame(frame, frame_idx)
                
                # Tracking
                self._update_progress(
                    ProcessingStatus.TRACKING,
                    frame_idx, total_frames,
                    f"Tracking frame {frame_idx}"
                )
                
                tracking_result = self.tracker.update(detections)
                
                # Tactical analysis
                if self.config.enable_tactical_analysis:
                    self._update_progress(
                        ProcessingStatus.ANALYZING,
                        frame_idx, total_frames,
                        f"Analyzing frame {frame_idx}"
                    )
                    
                    analytics_result = self._analyze_frame_tactics(
                        tracking_result, match_id
                    )
                    self.analytics_data.append(analytics_result)
                
                # Store results
                if self.config.save_detections:
                    self.detections_data.append(detections)
                
                if self.config.save_tracking:
                    self.tracking_data.append(tracking_result)
                
                processed_frames += 1
                
                # Check if we've reached max frames
                if (self.config.max_frames and 
                    processed_frames >= self.config.max_frames):
                    break
            
            # Save results
            self._update_progress(
                ProcessingStatus.COMPLETED,
                processed_frames, total_frames,
                "Saving results"
            )
            
            result_paths = self._save_results(match_output_dir, match_id)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Generate statistics
            stats = self._generate_statistics()
            
            return ProcessingResult(
                match_id=match_id,
                video_path=video_path,
                processing_time=processing_time,
                total_frames=total_frames,
                processed_frames=processed_frames,
                success=True,
                **result_paths,
                **stats
            )
            
        except Exception as e:
            logger.error(f"Pipeline processing error: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                match_id=match_id,
                video_path=video_path,
                processing_time=processing_time,
                total_frames=0,
                processed_frames=0,
                success=False,
                error_message=str(e)
            )
    
    def _analyze_frame_tactics(self, 
                              tracking_result: Dict[str, Any],
                              match_id: int) -> Dict[str, Any]:
        """
        Analyze frame for tactical insights.
        
        Args:
            tracking_result: Tracking data
            match_id: Match ID
            
        Returns:
            Dict: Tactical analysis result
        """
        try:
            # Convert tracking data to TrackPoint format
            frame_data = []
            
            # Process home team
            for track in tracking_result.get("tracks_home", []):
                # Convert pixel coordinates to real coordinates
                pixel_pos = track["position"]
                real_pos = self.calibrator.pixel_to_real(pixel_pos)
                
                frame_data.append({
                    "player_id": track["track_id"],
                    "team_id": 1,  # Home team
                    "role": "midfielder",  # Default role - could be enhanced
                    "x": real_pos[0],
                    "y": real_pos[1],
                    "speed": None,  # Could be calculated from previous frames
                    "vx": None,
                    "vy": None
                })
            
            # Process away team
            for track in tracking_result.get("tracks_away", []):
                pixel_pos = track["position"]
                real_pos = self.calibrator.pixel_to_real(pixel_pos)
                
                frame_data.append({
                    "player_id": track["track_id"],
                    "team_id": 2,  # Away team
                    "role": "midfielder",
                    "x": real_pos[0],
                    "y": real_pos[1],
                    "speed": None,
                    "vx": None,
                    "vy": None
                })
            
            # Get ball position
            ball_position = None
            if tracking_result.get("ball"):
                ball_pixel = tracking_result["ball"]["position"]
                ball_position = self.calibrator.pixel_to_real(ball_pixel)
            
            # Perform tactical analysis
            analysis_result = self.tactical_service.analyze_match_frame(
                match_id=match_id,
                frame_data=frame_data,
                timestamp=tracking_result["timestamp"],
                ball_position=ball_position
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Tactical analysis error: {e}")
            return {
                "error": str(e),
                "timestamp": tracking_result.get("timestamp", 0),
                "match_id": match_id
            }
    
    def _save_results(self, output_dir: str, match_id: int) -> Dict[str, str]:
        """
        Save processing results to files.
        
        Args:
            output_dir: Output directory
            match_id: Match ID
            
        Returns:
            Dict: Paths to saved files
        """
        result_paths = {}
        
        try:
            # Save detections
            if self.config.save_detections and self.detections_data:
                detections_path = os.path.join(output_dir, "detections.json")
                with open(detections_path, "w") as f:
                    json.dump(self.detections_data, f, indent=2)
                result_paths["detections_path"] = detections_path
            
            # Save tracking
            if self.config.save_tracking and self.tracking_data:
                tracking_path = os.path.join(output_dir, "tracking.json")
                with open(tracking_path, "w") as f:
                    json.dump(self.tracking_data, f, indent=2)
                result_paths["tracking_path"] = tracking_path
            
            # Save analytics
            if self.config.save_analytics and self.analytics_data:
                analytics_path = os.path.join(output_dir, "analytics.json")
                with open(analytics_path, "w") as f:
                    json.dump(self.analytics_data, f, indent=2, default=str)
                result_paths["analytics_path"] = analytics_path
            
            return result_paths
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return result_paths
    
    def _generate_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Generate processing statistics."""
        stats = {}
        
        try:
            # Detection statistics
            if self.detections_data:
                total_detections = sum(
                    len(d.get("players_home", [])) + len(d.get("players_away", []))
                    for d in self.detections_data
                )
                avg_confidence = np.mean([
                    p["confidence"]
                    for d in self.detections_data
                    for p in d.get("players_home", []) + d.get("players_away", [])
                ])
                
                stats["detection_stats"] = {
                    "total_frames": len(self.detections_data),
                    "total_detections": total_detections,
                    "avg_detections_per_frame": total_detections / len(self.detections_data),
                    "avg_confidence": float(avg_confidence)
                }
            
            # Tracking statistics
            if self.tracking_data:
                unique_tracks_home = set()
                unique_tracks_away = set()
                
                for t in self.tracking_data:
                    unique_tracks_home.update(track["track_id"] for track in t.get("tracks_home", []))
                    unique_tracks_away.update(track["track_id"] for track in t.get("tracks_away", []))
                
                stats["tracking_stats"] = {
                    "total_frames": len(self.tracking_data),
                    "unique_tracks_home": len(unique_tracks_home),
                    "unique_tracks_away": len(unique_tracks_away),
                    "total_unique_tracks": len(unique_tracks_home) + len(unique_tracks_away)
                }
            
            # Analytics statistics
            if self.analytics_data:
                total_alerts = sum(
                    len(a.get("teams", {}).get("1", {}).get("alerts", [])) +
                    len(a.get("teams", {}).get("2", {}).get("alerts", []))
                    for a in self.analytics_data
                    if "teams" in a
                )
                
                stats["analytics_stats"] = {
                    "total_frames": len(self.analytics_data),
                    "total_alerts": total_alerts,
                    "avg_alerts_per_frame": total_alerts / len(self.analytics_data) if self.analytics_data else 0
                }
            
        except Exception as e:
            logger.error(f"Error generating statistics: {e}")
        
        return stats
    
    def get_match_summary(self, match_id: int) -> Dict[str, Any]:
        """
        Generate match summary from analytics data.
        
        Args:
            match_id: Match ID
            
        Returns:
            Dict: Match summary
        """
        try:
            # Collect all alerts from analytics data
            all_alerts = []
            
            for frame_analytics in self.analytics_data:
                if "teams" in frame_analytics:
                    for team_id, team_data in frame_analytics["teams"].items():
                        alerts = team_data.get("alerts", [])
                        all_alerts.extend(alerts)
            
            # Generate summary using tactical service
            summary = self.tactical_service.get_match_summary(match_id, all_alerts)
            
            # Add processing metadata
            summary["processing_metadata"] = {
                "total_frames_analyzed": len(self.analytics_data),
                "processing_timestamp": datetime.now().isoformat(),
                "pipeline_config": asdict(self.config)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating match summary: {e}")
            return {
                "error": str(e),
                "match_id": match_id
            }
    
    def create_highlight_clips(self, 
                              video_path: str,
                              output_dir: str,
                              alert_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Create highlight clips based on tactical alerts.
        
        Args:
            video_path: Source video path
            output_dir: Output directory for clips
            alert_threshold: Minimum confidence for highlights
            
        Returns:
            List: Created clips information
        """
        clips = []
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Find high-confidence alerts
            highlight_moments = []
            
            for frame_analytics in self.analytics_data:
                if "teams" not in frame_analytics:
                    continue
                
                timestamp = frame_analytics.get("timestamp", 0)
                
                for team_id, team_data in frame_analytics["teams"].items():
                    alerts = team_data.get("alerts", [])
                    
                    for alert in alerts:
                        if alert.get("confidence", 0) >= alert_threshold:
                            highlight_moments.append({
                                "timestamp": timestamp,
                                "alert": alert,
                                "team_id": team_id
                            })
            
            # Group nearby moments and create clips
            if highlight_moments:
                # Sort by timestamp
                highlight_moments.sort(key=lambda x: x["timestamp"])
                
                # Group moments within 10 seconds
                grouped_moments = []
                current_group = [highlight_moments[0]]
                
                for moment in highlight_moments[1:]:
                    if moment["timestamp"] - current_group[-1]["timestamp"] <= 10.0:
                        current_group.append(moment)
                    else:
                        grouped_moments.append(current_group)
                        current_group = [moment]
                
                grouped_moments.append(current_group)
                
                # Create clips for each group
                for i, group in enumerate(grouped_moments):
                    start_time = max(0, group[0]["timestamp"] - 5.0)  # 5s before
                    end_time = group[-1]["timestamp"] + 5.0  # 5s after
                    
                    clip_filename = f"highlight_{i+1}_{int(start_time)}s.mp4"
                    clip_path = os.path.join(output_dir, clip_filename)
                    
                    clip_result = self.video_processor.create_video_clip(
                        video_path, start_time, end_time, clip_path
                    )
                    
                    if clip_result["success"]:
                        clips.append({
                            "clip_path": clip_path,
                            "start_time": start_time,
                            "end_time": end_time,
                            "duration": end_time - start_time,
                            "alerts": [m["alert"] for m in group],
                            "description": f"Tactical highlight {i+1}"
                        })
            
        except Exception as e:
            logger.error(f"Error creating highlight clips: {e}")
        
        return clips


def create_processing_pipeline(output_dir: str, 
                             config: Optional[PipelineConfig] = None) -> MatchAnalysisPipeline:
    """
    Create configured processing pipeline.
    
    Args:
        output_dir: Output directory
        config: Pipeline configuration
        
    Returns:
        MatchAnalysisPipeline: Configured pipeline
    """
    return MatchAnalysisPipeline(output_dir, config)


def process_match_async(video_path: str,
                       match_id: int,
                       output_dir: str,
                       config: Optional[PipelineConfig] = None,
                       progress_callback: Optional[Callable] = None) -> ProcessingResult:
    """
    Process match video asynchronously.
    
    Args:
        video_path: Video file path
        match_id: Match ID
        output_dir: Output directory
        config: Pipeline configuration
        progress_callback: Progress callback function
        
    Returns:
        ProcessingResult: Processing result
    """
    pipeline = create_processing_pipeline(output_dir, config)
    
    if progress_callback:
        pipeline.set_progress_callback(progress_callback)
    
    return pipeline.process_match_video(video_path, match_id)