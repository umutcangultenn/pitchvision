"""
Scouting API - Oyuncu izleme ve gözlem notları
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.player import Player
from app.models.scout_note import ScoutNote
from app.auth import get_current_active_user
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scouting", tags=["scouting"])


@router.get("/players")
def get_scouting_players(
    team_id: int = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Oyuncu izleme listesi - Gelişim hızına göre sıralanmış
    
    Query Parameters:
    - team_id: Belirli takımın oyuncuları (opsiyonel)
    """
    try:
        statement = select(Player)
        
        if team_id:
            statement = statement.where(Player.team_id == team_id)
        
        players = session.exec(statement).all()
        
        # Gelişim hızına göre sırala (yüksekten düşüğe)
        sorted_players = sorted(
            players,
            key=lambda p: p.development_velocity or 0,
            reverse=True
        )
        
        logger.info(f"Scouting: {len(sorted_players)} oyuncu listelendi")
        return sorted_players
        
    except Exception as e:
        logger.error(f"Scouting oyuncu listesi hatası: {e}")
        raise HTTPException(status_code=500, detail="Oyuncu listesi alınamadı")


@router.get("/players/{player_id}/notes")
def get_player_scout_notes(
    player_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Oyuncu izleme notları
    
    Path Parameters:
    - player_id: Oyuncu ID
    """
    try:
        # Oyuncu var mı kontrol et
        player = session.get(Player, player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Oyuncu bulunamadı")
        
        # Notları getir
        statement = select(ScoutNote).where(ScoutNote.player_id == player_id)
        notes = session.exec(statement).all()
        
        logger.info(f"Scouting: Oyuncu {player_id} için {len(notes)} not listelendi")
        return notes
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scouting notları hatası: {e}")
        raise HTTPException(status_code=500, detail="Notlar alınamadı")


@router.post("/players/{player_id}/notes")
def create_scout_note(
    player_id: int,
    note: str,
    rating: float = None,
    tags_json: dict = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Oyuncu için yeni izleme notu oluştur
    
    Path Parameters:
    - player_id: Oyuncu ID
    
    Body Parameters:
    - note: Not metni
    - rating: Derecelendirme (0-10)
    - tags_json: Etiketler
    """
    try:
        # Oyuncu var mı kontrol et
        player = session.get(Player, player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Oyuncu bulunamadı")
        
        # Rating doğrulaması
        if rating is not None and (rating < 0 or rating > 10):
            raise HTTPException(status_code=400, detail="Rating 0-10 arasında olmalı")
        
        # Not oluştur
        scout_note = ScoutNote(
            player_id=player_id,
            scout_id=current_user.id,
            note=note,
            rating=rating,
            tags_json=tags_json or {}
        )
        
        session.add(scout_note)
        session.commit()
        session.refresh(scout_note)
        
        logger.info(f"Scouting: Oyuncu {player_id} için yeni not oluşturuldu")
        return scout_note
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scouting notu oluşturma hatası: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Not oluşturulamadı")


@router.get("/players/{player_id}/notes/{note_id}")
def get_scout_note(
    player_id: int,
    note_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Belirli bir izleme notunu getir
    """
    try:
        note = session.get(ScoutNote, note_id)
        if not note or note.player_id != player_id:
            raise HTTPException(status_code=404, detail="Not bulunamadı")
        
        return note
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scouting notu getirme hatası: {e}")
        raise HTTPException(status_code=500, detail="Not alınamadı")


@router.put("/players/{player_id}/notes/{note_id}")
def update_scout_note(
    player_id: int,
    note_id: int,
    note: str = None,
    rating: float = None,
    tags_json: dict = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    İzleme notunu güncelle
    """
    try:
        db_note = session.get(ScoutNote, note_id)
        if not db_note or db_note.player_id != player_id:
            raise HTTPException(status_code=404, detail="Not bulunamadı")
        
        # Sadece not sahibi güncelleyebilir
        if db_note.scout_id != current_user.id:
            raise HTTPException(status_code=403, detail="Yetkiniz yok")
        
        if note is not None:
            db_note.note = note
        if rating is not None:
            if rating < 0 or rating > 10:
                raise HTTPException(status_code=400, detail="Rating 0-10 arasında olmalı")
            db_note.rating = rating
        if tags_json is not None:
            db_note.tags_json = tags_json
        
        session.add(db_note)
        session.commit()
        session.refresh(db_note)
        
        logger.info(f"Scouting: Not {note_id} güncellendi")
        return db_note
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scouting notu güncelleme hatası: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Not güncellenemedi")


@router.delete("/players/{player_id}/notes/{note_id}")
def delete_scout_note(
    player_id: int,
    note_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    İzleme notunu sil
    """
    try:
        db_note = session.get(ScoutNote, note_id)
        if not db_note or db_note.player_id != player_id:
            raise HTTPException(status_code=404, detail="Not bulunamadı")
        
        # Sadece not sahibi silebilir
        if db_note.scout_id != current_user.id:
            raise HTTPException(status_code=403, detail="Yetkiniz yok")
        
        session.delete(db_note)
        session.commit()
        
        logger.info(f"Scouting: Not {note_id} silindi")
        return {"message": "Not silindi"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scouting notu silme hatası: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Not silinemedi")


@router.get("/hidden-gems")
def get_hidden_gems(
    min_velocity: float = 0.5,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Yüksek gelişim hızına sahip oyuncuları getir (gizli hazineler)
    
    Query Parameters:
    - min_velocity: Minimum gelişim hızı (default: 0.5)
    """
    try:
        statement = select(Player).where(
            Player.development_velocity >= min_velocity
        )
        
        players = session.exec(statement).all()
        
        # Gelişim hızına göre sırala
        sorted_players = sorted(
            players,
            key=lambda p: p.development_velocity or 0,
            reverse=True
        )
        
        logger.info(f"Scouting: {len(sorted_players)} gizli hazine bulundu")
        return sorted_players
        
    except Exception as e:
        logger.error(f"Gizli hazine hatası: {e}")
        raise HTTPException(status_code=500, detail="Gizli hazineler alınamadı")


@router.get("/stats")
def get_scouting_stats(
    team_id: int = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Scouting istatistikleri
    """
    try:
        statement = select(Player)
        if team_id:
            statement = statement.where(Player.team_id == team_id)
        
        players = session.exec(statement).all()
        
        stats = {
            "total_players": len(players),
            "high_potential": len([p for p in players if (p.development_velocity or 0) > 1.0]),
            "high_velocity": len([p for p in players if (p.development_velocity or 0) > 0.5]),
            "average_velocity": sum(p.development_velocity or 0 for p in players) / len(players) if players else 0,
        }
        
        logger.info(f"Scouting: İstatistikler hesaplandı")
        return stats
        
    except Exception as e:
        logger.error(f"Scouting istatistikleri hatası: {e}")
        raise HTTPException(status_code=500, detail="İstatistikler alınamadı")
