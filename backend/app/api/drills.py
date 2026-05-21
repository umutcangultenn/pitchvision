"""
Drills API - Antrenman önerileri ve egzersizler
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models.drill_recommendation import DrillRecommendation
from app.models.tactical_alert import TacticalAlert
from app.auth import get_current_active_user
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drills", tags=["drills"])


@router.get("")
def get_drills(
    alert_type: str = Query(None),
    problem_type: str = Query(None),
    difficulty: str = Query(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Antrenman önerileri listesi
    
    Query Parameters:
    - alert_type: Uyarı tipi ile filtreleme (opsiyonel)
    - problem_type: Problem tipi ile filtreleme (opsiyonel)
    - difficulty: Zorluk seviyesi (easy, medium, hard) (opsiyonel)
    """
    try:
        statement = select(DrillRecommendation)
        
        if alert_type:
            statement = statement.where(DrillRecommendation.alert_type == alert_type)
        
        if problem_type:
            statement = statement.where(DrillRecommendation.problem_type == problem_type)
        
        if difficulty:
            statement = statement.where(DrillRecommendation.difficulty == difficulty)
        
        drills = session.exec(statement).all()
        
        logger.info(f"Drills: {len(drills)} antrenman önerisi listelendi")
        return drills
        
    except Exception as e:
        logger.error(f"Drills listesi hatası: {e}")
        raise HTTPException(status_code=500, detail="Antrenman önerileri alınamadı")


@router.get("/{drill_id}")
def get_drill(
    drill_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Belirli bir antrenman önerisini getir
    """
    try:
        drill = session.get(DrillRecommendation, drill_id)
        if not drill:
            raise HTTPException(status_code=404, detail="Antrenman önerisi bulunamadı")
        
        return drill
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Drill getirme hatası: {e}")
        raise HTTPException(status_code=500, detail="Antrenman önerisi alınamadı")


@router.get("/match/{match_id}")
def get_match_drills(
    match_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Maç için önerilen antrenmanları getir
    
    Maçtaki uyarılara dayalı olarak ilgili antrenmanları önerir
    """
    try:
        # Maçtaki uyarıları getir
        statement = select(TacticalAlert).where(TacticalAlert.match_id == match_id)
        alerts = session.exec(statement).all()
        
        if not alerts:
            # Uyarı yoksa tüm antrenmanları döndür
            drills = session.exec(select(DrillRecommendation)).all()
            logger.info(f"Drills: Maç {match_id} için {len(drills)} antrenman önerisi (uyarı yok)")
            return drills
        
        # Uyarı tiplerini topla
        alert_types = set(alert.alert_type for alert in alerts)
        
        # İlgili antrenmanları getir
        drills = []
        for alert_type in alert_types:
            statement = select(DrillRecommendation).where(
                DrillRecommendation.alert_type == alert_type
            )
            matching_drills = session.exec(statement).all()
            drills.extend(matching_drills)
        
        # Duplikatları kaldır
        unique_drills = list({drill.id: drill for drill in drills}.values())
        
        logger.info(f"Drills: Maç {match_id} için {len(unique_drills)} antrenman önerisi")
        return unique_drills
        
    except Exception as e:
        logger.error(f"Maç antrenmanları hatası: {e}")
        raise HTTPException(status_code=500, detail="Antrenman önerileri alınamadı")


@router.get("/difficulty/{difficulty}")
def get_drills_by_difficulty(
    difficulty: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Zorluk seviyesine göre antrenmanları getir
    
    Path Parameters:
    - difficulty: easy, medium, hard
    """
    try:
        valid_difficulties = ["easy", "medium", "hard"]
        if difficulty not in valid_difficulties:
            raise HTTPException(
                status_code=400,
                detail=f"Zorluk seviyesi {valid_difficulties} arasında olmalı"
            )
        
        statement = select(DrillRecommendation).where(
            DrillRecommendation.difficulty == difficulty
        )
        drills = session.exec(statement).all()
        
        logger.info(f"Drills: {difficulty} zorlukta {len(drills)} antrenman")
        return drills
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Zorluk seviyesi antrenmanları hatası: {e}")
        raise HTTPException(status_code=500, detail="Antrenman önerileri alınamadı")


@router.get("/duration/{duration_minutes}")
def get_drills_by_duration(
    duration_minutes: int,
    tolerance: int = 5,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Süreye göre antrenmanları getir
    
    Path Parameters:
    - duration_minutes: Antrenman süresi (dakika)
    - tolerance: Tolerans aralığı (dakika)
    """
    try:
        min_duration = duration_minutes - tolerance
        max_duration = duration_minutes + tolerance
        
        statement = select(DrillRecommendation).where(
            (DrillRecommendation.duration_minutes >= min_duration) &
            (DrillRecommendation.duration_minutes <= max_duration)
        )
        drills = session.exec(statement).all()
        
        logger.info(f"Drills: {duration_minutes}±{tolerance} dakikada {len(drills)} antrenman")
        return drills
        
    except Exception as e:
        logger.error(f"Süre antrenmanları hatası: {e}")
        raise HTTPException(status_code=500, detail="Antrenman önerileri alınamadı")


@router.get("/stats")
def get_drills_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Antrenman istatistikleri
    """
    try:
        all_drills = session.exec(select(DrillRecommendation)).all()
        
        stats = {
            "total_drills": len(all_drills),
            "by_difficulty": {
                "easy": len([d for d in all_drills if d.difficulty == "easy"]),
                "medium": len([d for d in all_drills if d.difficulty == "medium"]),
                "hard": len([d for d in all_drills if d.difficulty == "hard"]),
            },
            "average_duration": sum(d.duration_minutes or 0 for d in all_drills) / len(all_drills) if all_drills else 0,
            "by_alert_type": {}
        }
        
        # Alert type'a göre sayı
        for drill in all_drills:
            alert_type = drill.alert_type
            if alert_type not in stats["by_alert_type"]:
                stats["by_alert_type"][alert_type] = 0
            stats["by_alert_type"][alert_type] += 1
        
        logger.info(f"Drills: İstatistikler hesaplandı")
        return stats
        
    except Exception as e:
        logger.error(f"Drills istatistikleri hatası: {e}")
        raise HTTPException(status_code=500, detail="İstatistikler alınamadı")


@router.post("")
def create_drill(
    title: str,
    description: str,
    alert_type: str,
    problem_type: str,
    difficulty: str,
    duration_minutes: int,
    instructions: str = None,
    equipment: list = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Yeni antrenman önerisi oluştur (Admin)
    """
    try:
        # Zorluk seviyesi doğrulaması
        valid_difficulties = ["easy", "medium", "hard"]
        if difficulty not in valid_difficulties:
            raise HTTPException(
                status_code=400,
                detail=f"Zorluk seviyesi {valid_difficulties} arasında olmalı"
            )
        
        drill = DrillRecommendation(
            title=title,
            description=description,
            alert_type=alert_type,
            problem_type=problem_type,
            difficulty=difficulty,
            duration_minutes=duration_minutes,
            instructions=instructions,
            equipment=equipment or []
        )
        
        session.add(drill)
        session.commit()
        session.refresh(drill)
        
        logger.info(f"Drills: Yeni antrenman '{title}' oluşturuldu")
        return drill
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Antrenman oluşturma hatası: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Antrenman oluşturulamadı")
