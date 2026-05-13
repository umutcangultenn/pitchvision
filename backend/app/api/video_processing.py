"""
Video processing API endpoints.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import os
import tempfile
import shutil
from datetime import datetime

from ..cv.video_io import VideoProcessor, VideoUploadHandler, check_video_dependencies
from ..cv.pipeline import MatchAnalysisPipeline, PipelineConfig, ProcessingResult, process_match_async
from ..config import settings

router = APIRouter(prefix="/api/video", tags=["video-processing"])


# Pydantic models
class VideoUploadResponse(BaseModel):
    """Video upload response."""
    success: bool
    video_id: str
    filename: str
    metadata: Dict[str, Any]
    message: str


class ProcessingConfigRequest(BaseModel):
    """Processing configuration request."""
    frame_interval: int = Field(1, ge=1, le=10)
    max_frames: Optional[int] = Field(None, ge=100, le=100000)
    save_frames: bool = False
    enable_tactical_analysis: bool = True
    output_video: bool = False
    video_overlay: bool = True


class ProcessingRequest(BaseModel):
    """Video processing request."""
    video_id: str
    match_id: int
    config: Optional[ProcessingConfigRequest] = None
    calibration_points: Optional[List[Dict[str, Any]]] = None


class ProcessingStatusResponse(BaseModel):
    """Processing status response."""
    video_id: str
    match_id: int
    status: str
    progress_percent: float
    current_frame: int
    total_frames: int
    current_step: str
    estimated_remaining: Optional[str] = None
    error_message: Optional[str] = None


class ClipRequest(BaseModel):
    """Video clip creation request."""
    video_id: str
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CalibrationPoint(BaseModel):
    """Calibration point model."""
    pixel: List[float] = Field(..., min_items=2, max_items=2)
    real: List[float] = Field(..., min_items=2, max_items=2)
    label: str


class CalibrationRequest(BaseModel):
    """Calibration request."""
    video_id: str
    points: List[CalibrationPoint] = Field(..., min_items=4, max_items=8)


# Global storage for processing status (in production, use Redis or database)
processing_status: Dict[str, Dict[str, Any]] = {}
uploaded_videos: Dict[str, Dict[str, Any]] = {}

# Initialize components
video_processor = VideoProcessor()
upload_handler = VideoUploadHandler(
    upload_dir=os.path.join(settings.UPLOAD_DIR, "videos"),
    processor=video_processor
)


def progress_callback_factory(video_id: str):
    """Create progress callback for specific video."""
    def callback(progress):
        processing_status[video_id] = {
            "status": progress.status.value,
            "progress_percent": progress.progress_percent,
            "current_frame": progress.current_frame,
            "total_frames": progress.total_frames,
            "current_step": progress.current_step,
            "error_message": progress.error_message,
            "updated_at": datetime.now().isoformat()
        }
    return callback


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    match_id: int,
    file: UploadFile = File(..., description="Video file to upload")
):
    """
    Upload video file for processing.
    
    Args:
        match_id: Associated match ID
        file: Video file
        
    Returns:
        VideoUploadResponse: Upload result
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file size (limit to 2GB)
        max_size = 2 * 1024 * 1024 * 1024  # 2GB
        file_size = 0
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {file_size / (1024**3):.1f}GB (max: 2GB)"
            )
        
        # Handle upload
        upload_result = upload_handler.handle_upload(
            file_data=content,
            filename=file.filename,
            match_id=match_id
        )
        
        if not upload_result["success"]:
            raise HTTPException(status_code=400, detail=upload_result["error"])
        
        # Generate video ID
        video_id = f"video_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store video info
        uploaded_videos[video_id] = {
            "video_path": upload_result["video_path"],
            "filename": upload_result["filename"],
            "match_id": match_id,
            "metadata": upload_result["metadata"].__dict__,
            "uploaded_at": datetime.now().isoformat()
        }
        
        return VideoUploadResponse(
            success=True,
            video_id=video_id,
            filename=upload_result["filename"],
            metadata=upload_result["summary"],
            message="Video uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/process")
async def start_processing(
    request: ProcessingRequest,
    background_tasks: BackgroundTasks
):
    """
    Start video processing in background.
    
    Args:
        request: Processing request
        background_tasks: FastAPI background tasks
        
    Returns:
        Dict: Processing start confirmation
    """
    try:
        # Validate video exists
        if request.video_id not in uploaded_videos:
            raise HTTPException(status_code=404, detail="Video not found")
        
        video_info = uploaded_videos[request.video_id]
        video_path = video_info["video_path"]
        
        # Create pipeline config
        config = PipelineConfig()
        if request.config:
            config.frame_interval = request.config.frame_interval
            config.max_frames = request.config.max_frames
            config.save_frames = request.config.save_frames
            config.enable_tactical_analysis = request.config.enable_tactical_analysis
            config.output_video = request.config.output_video
            config.video_overlay = request.config.video_overlay
        
        # Initialize processing status
        processing_status[request.video_id] = {
            "status": "pending",
            "progress_percent": 0.0,
            "current_frame": 0,
            "total_frames": 0,
            "current_step": "Initializing",
            "error_message": None,
            "started_at": datetime.now().isoformat()
        }
        
        # Start processing in background
        background_tasks.add_task(
            process_video_background,
            video_path,
            request.match_id,
            request.video_id,
            config,
            request.calibration_points
        )
        
        return {
            "success": True,
            "video_id": request.video_id,
            "match_id": request.match_id,
            "message": "Processing started",
            "status_endpoint": f"/api/video/status/{request.video_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing start failed: {str(e)}")


async def process_video_background(
    video_path: str,
    match_id: int,
    video_id: str,
    config: PipelineConfig,
    calibration_points: Optional[List[Dict[str, Any]]] = None
):
    """Background video processing task."""
    try:
        # Create output directory
        output_dir = os.path.join(settings.UPLOAD_DIR, "processed", video_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create pipeline
        pipeline = MatchAnalysisPipeline(output_dir, config)
        pipeline.set_progress_callback(progress_callback_factory(video_id))
        
        # Set calibration if provided
        if calibration_points:
            pipeline.set_calibration(calibration_points)
        
        # Process video
        result = pipeline.process_match_video(video_path, match_id)
        
        # Update final status
        if result.success:
            processing_status[video_id].update({
                "status": "completed",
                "progress_percent": 100.0,
                "current_step": "Processing completed",
                "completed_at": datetime.now().isoformat(),
                "result": {
                    "processing_time": result.processing_time,
                    "processed_frames": result.processed_frames,
                    "total_frames": result.total_frames,
                    "output_paths": {
                        "detections": result.detections_path,
                        "tracking": result.tracking_path,
                        "analytics": result.analytics_path
                    }
                }
            })
        else:
            processing_status[video_id].update({
                "status": "failed",
                "error_message": result.error_message,
                "failed_at": datetime.now().isoformat()
            })
            
    except Exception as e:
        processing_status[video_id].update({
            "status": "failed",
            "error_message": str(e),
            "failed_at": datetime.now().isoformat()
        })


@router.get("/status/{video_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(video_id: str):
    """
    Get video processing status.
    
    Args:
        video_id: Video ID
        
    Returns:
        ProcessingStatusResponse: Current processing status
    """
    if video_id not in processing_status:
        raise HTTPException(status_code=404, detail="Processing status not found")
    
    status = processing_status[video_id]
    video_info = uploaded_videos.get(video_id, {})
    
    return ProcessingStatusResponse(
        video_id=video_id,
        match_id=video_info.get("match_id", 0),
        status=status["status"],
        progress_percent=status["progress_percent"],
        current_frame=status["current_frame"],
        total_frames=status["total_frames"],
        current_step=status["current_step"],
        error_message=status.get("error_message")
    )


@router.post("/create-clip")
async def create_video_clip(request: ClipRequest):
    """
    Create video clip from processed video.
    
    Args:
        request: Clip creation request
        
    Returns:
        Dict: Clip creation result
    """
    try:
        # Validate video exists
        if request.video_id not in uploaded_videos:
            raise HTTPException(status_code=404, detail="Video not found")
        
        video_info = uploaded_videos[request.video_id]
        video_path = video_info["video_path"]
        
        # Validate time range
        if request.start_time >= request.end_time:
            raise HTTPException(status_code=400, detail="Invalid time range")
        
        # Create clip
        clips_dir = os.path.join(settings.UPLOAD_DIR, "clips")
        os.makedirs(clips_dir, exist_ok=True)
        
        clip_filename = f"clip_{request.video_id}_{int(request.start_time)}_{int(request.end_time)}.mp4"
        clip_path = os.path.join(clips_dir, clip_filename)
        
        clip_result = video_processor.create_video_clip(
            video_path, request.start_time, request.end_time, clip_path
        )
        
        if not clip_result["success"]:
            raise HTTPException(status_code=500, detail=clip_result["error"])
        
        return {
            "success": True,
            "clip_id": clip_filename.replace(".mp4", ""),
            "clip_path": clip_path,
            "duration": request.end_time - request.start_time,
            "title": request.title,
            "description": request.description,
            "size_bytes": clip_result["size_bytes"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clip creation failed: {str(e)}")


@router.post("/calibrate")
async def set_calibration(request: CalibrationRequest):
    """
    Set pitch calibration points.
    
    Args:
        request: Calibration request
        
    Returns:
        Dict: Calibration result
    """
    try:
        # Validate video exists
        if request.video_id not in uploaded_videos:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Convert points to calibrator format
        calibration_points = []
        for point in request.points:
            calibration_points.append({
                "pixel": point.pixel,
                "real": point.real,
                "label": point.label
            })
        
        # Store calibration (in production, save to database)
        calibration_data = {
            "video_id": request.video_id,
            "points": calibration_points,
            "created_at": datetime.now().isoformat()
        }
        
        # Save calibration file
        calibration_dir = os.path.join(settings.UPLOAD_DIR, "calibrations")
        os.makedirs(calibration_dir, exist_ok=True)
        
        calibration_file = os.path.join(calibration_dir, f"{request.video_id}_calibration.json")
        
        import json
        with open(calibration_file, "w") as f:
            json.dump(calibration_data, f, indent=2)
        
        return {
            "success": True,
            "video_id": request.video_id,
            "points_count": len(calibration_points),
            "calibration_file": calibration_file,
            "message": "Calibration saved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calibration failed: {str(e)}")


@router.get("/info/{video_id}")
async def get_video_info(video_id: str):
    """
    Get detailed video information.
    
    Args:
        video_id: Video ID
        
    Returns:
        Dict: Video information
    """
    if video_id not in uploaded_videos:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_info = uploaded_videos[video_id]
    video_path = video_info["video_path"]
    
    # Get detailed info using FFprobe
    detailed_info = video_processor.get_video_info(video_path)
    
    return {
        "video_id": video_id,
        "basic_info": video_info,
        "detailed_info": detailed_info,
        "processing_status": processing_status.get(video_id)
    }


@router.get("/dependencies")
async def check_dependencies():
    """
    Check video processing dependencies.
    
    Returns:
        Dict: Dependency status
    """
    deps = check_video_dependencies()
    
    return {
        "dependencies": deps,
        "all_available": all(deps.values()),
        "missing": [name for name, available in deps.items() if not available],
        "recommendations": {
            "ffmpeg": "Install FFmpeg for video processing: https://ffmpeg.org/download.html",
            "ffprobe": "FFprobe comes with FFmpeg installation"
        }
    }


@router.get("/health")
async def health_check():
    """
    Video processing service health check.
    
    Returns:
        Dict: Health status
    """
    deps = check_video_dependencies()
    
    return {
        "status": "healthy" if deps["opencv"] else "degraded",
        "service": "video-processing",
        "dependencies": deps,
        "upload_dir": settings.UPLOAD_DIR,
        "active_uploads": len(uploaded_videos),
        "active_processing": len([s for s in processing_status.values() 
                                if s["status"] in ["pending", "extracting", "detecting", "tracking", "analyzing"]])
    }