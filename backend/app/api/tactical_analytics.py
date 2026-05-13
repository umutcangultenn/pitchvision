"""
Tactical Analytics API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from ..analytics.tactical_service import TacticalAnalyticsService


router = APIRouter(prefix="/api/tactical", tags=["tactical-analytics"])


# Pydantic modelleri
class PlayerTrackingData(BaseModel):
    """Oyuncu tracking verisi."""
    player_id: int
    team_id: int
    role: str = Field(..., pattern="^(goalkeeper|defender|midfielder|forward)$")
    x: float = Field(..., ge=0, le=105)  # Saha x koordinatı
    y: float = Field(..., ge=0, le=68)   # Saha y koordinatı
    speed: Optional[float] = Field(None, ge=0, le=15)  # m/s
    vx: Optional[float] = None  # velocity x
    vy: Optional[float] = None  # velocity y


class FrameAnalysisRequest(BaseModel):
    """Frame analizi isteği."""
    match_id: int
    timestamp: float
    players: List[PlayerTrackingData]
    ball_position: Optional[tuple] = None


class TrainingRecommendationRequest(BaseModel):
    """Antrenman önerisi isteği."""
    alerts: List[Dict[str, Any]]
    team_level: str = Field("youth", pattern="^(youth|amateur|professional)$")
    session_duration: int = Field(90, ge=30, le=180)
    player_count: int = Field(11, ge=8, le=22)


class MatchSummaryRequest(BaseModel):
    """Maç özeti isteği."""
    match_id: int
    alerts: List[Dict[str, Any]]


# Service instance
tactical_service = TacticalAnalyticsService()


@router.post("/analyze-frame")
async def analyze_frame(request: FrameAnalysisRequest):
    """
    Tek bir maç frame'ini analiz eder.
    
    Args:
        request: Frame analizi isteği
        
    Returns:
        Dict: Analiz sonuçları
    """
    try:
        # Pydantic modellerini dict'e çevir
        frame_data = [player.dict() for player in request.players]
        
        # Veriyi doğrula
        validation = tactical_service.validate_tracking_data(frame_data)
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Geçersiz tracking verisi",
                    "errors": validation["errors"]
                }
            )
        
        # Analiz yap
        result = tactical_service.analyze_match_frame(
            match_id=request.match_id,
            frame_data=frame_data,
            timestamp=request.timestamp,
            ball_position=request.ball_position
        )
        
        # Uyarıları da ekle
        if validation["warnings"]:
            result["warnings"] = validation["warnings"]
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analiz hatası: {str(e)}"
        )


@router.post("/training-recommendations")
async def get_training_recommendations(request: TrainingRecommendationRequest):
    """
    Uyarılara göre antrenman önerileri getirir.
    
    Args:
        request: Antrenman önerisi isteği
        
    Returns:
        Dict: Antrenman seansı planı
    """
    try:
        recommendations = tactical_service.get_training_recommendations(
            alerts=request.alerts,
            team_level=request.team_level,
            session_duration=request.session_duration,
            player_count=request.player_count
        )
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Antrenman önerisi hatası: {str(e)}"
        )


@router.post("/match-summary")
async def get_match_summary(request: MatchSummaryRequest):
    """
    Maç özeti oluşturur.
    
    Args:
        request: Maç özeti isteği
        
    Returns:
        Dict: Maç özeti
    """
    try:
        summary = tactical_service.get_match_summary(
            match_id=request.match_id,
            all_alerts=request.alerts
        )
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Özet oluşturma hatası: {str(e)}"
        )


@router.post("/validate-data")
async def validate_tracking_data(players: List[PlayerTrackingData]):
    """
    Tracking verisini doğrular.
    
    Args:
        players: Oyuncu tracking verileri
        
    Returns:
        Dict: Doğrulama sonucu
    """
    try:
        frame_data = [player.dict() for player in players]
        validation = tactical_service.validate_tracking_data(frame_data)
        
        return validation
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Doğrulama hatası: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Servis sağlık kontrolü.
    
    Returns:
        Dict: Sağlık durumu
    """
    return {
        "status": "healthy",
        "service": "tactical-analytics",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/config")
async def get_config():
    """
    Taktiksel analiz konfigürasyonunu getirir.
    
    Returns:
        Dict: Konfigürasyon
    """
    from ..analytics.types import TacticalConfig
    
    return {
        "thresholds": {
            "defensive_line_break": TacticalConfig.DEFENSIVE_LINE_BREAK_THRESHOLD,
            "block_gap_warning": TacticalConfig.BLOCK_GAP_WARNING_THRESHOLD,
            "block_gap_critical": TacticalConfig.BLOCK_GAP_CRITICAL_THRESHOLD,
            "transition_speed_slow": TacticalConfig.TRANSITION_SPEED_SLOW_THRESHOLD,
            "depth_run_velocity": TacticalConfig.DEPTH_RUN_VELOCITY_THRESHOLD,
            "compactness_warning": TacticalConfig.COMPACTNESS_WARNING_THRESHOLD
        },
        "field_dimensions": {
            "length": TacticalConfig.FIELD_LENGTH,
            "width": TacticalConfig.FIELD_WIDTH
        },
        "analysis_windows": {
            "transition": TacticalConfig.TRANSITION_ANALYSIS_WINDOW,
            "defensive_line": TacticalConfig.DEFENSIVE_LINE_ANALYSIS_WINDOW
        }
    }


# Örnek kullanım endpoint'i
@router.post("/example-analysis")
async def run_example_analysis():
    """
    Örnek analiz çalıştırır (demo amaçlı).
    
    Returns:
        Dict: Örnek analiz sonuçları
    """
    try:
        from ..analytics.example_usage import create_sample_tracking_data
        from ..analytics.alerts_new import generate_tactical_alerts
        
        # Örnek veri oluştur
        tracking_data = create_sample_tracking_data()
        
        # Frame verisine çevir
        frame_data = []
        for point in tracking_data:
            frame_data.append({
                "player_id": point.player_id,
                "team_id": point.team_id,
                "role": point.role.value,
                "x": point.x,
                "y": point.y,
                "speed": point.speed,
                "vx": point.vx,
                "vy": point.vy
            })
        
        # Analiz yap
        result = tactical_service.analyze_match_frame(
            match_id=999,  # Demo maç ID
            frame_data=frame_data,
            timestamp=1200.0,
            ball_position=(45.0, 30.0)
        )
        
        return {
            "message": "Örnek analiz başarıyla tamamlandı",
            "data_points": len(frame_data),
            "analysis": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Örnek analiz hatası: {str(e)}"
        )