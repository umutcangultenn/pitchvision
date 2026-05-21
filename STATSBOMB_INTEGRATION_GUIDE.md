# StatsBomb Entegrasyonu - Teknik Rehber

**Amaç**: StatsBomb Open Data ile gerçek maç verilerini entegre etmek  
**Hedef**: YOLO tespitleri vs StatsBomb verileri karşılaştırması  
**Zaman**: 2-3 hafta

---

## 1. STATSBOMB VERİ YAPISI

### Maç Verisi (Match)
```json
{
  "match_id": 2499700,
  "match_date": "2017-08-12",
  "kick_off": "20:00:00.000",
  "competition": {
    "competition_id": 11,
    "competition_name": "La Liga",
    "season_id": 1,
    "season_name": "2017/18"
  },
  "home_team": {
    "team_id": 217,
    "team_name": "Real Madrid",
    "manager": { "id": 1, "name": "Zinedine Zidane" }
  },
  "away_team": {
    "team_id": 206,
    "team_name": "Barcelona",
    "manager": { "id": 2, "name": "Luis Enrique" }
  },
  "home_score": 3,
  "away_score": 1,
  "duration": 90,
  "status": "Complete"
}
```

### Olay Verisi (Event)
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "index": 1,
  "period": 1,
  "timestamp": "00:00:00.000",
  "minute": 0,
  "second": 0,
  "type": {
    "id": 30,
    "name": "Pass"
  },
  "possession": 1,
  "possession_team": {
    "id": 217,
    "name": "Real Madrid"
  },
  "play_pattern": {
    "id": 1,
    "name": "Regular Play"
  },
  "player": {
    "id": 5203,
    "name": "Cristiano Ronaldo"
  },
  "position": {
    "id": 21,
    "name": "Right Wing"
  },
  "location": [60.0, 40.0],
  "duration": 0.5,
  "pass": {
    "recipient": {
      "id": 5206,
      "name": "Toni Kroos"
    },
    "length": 15.5,
    "angle": 45.0,
    "height": {
      "id": 1,
      "name": "Ground Pass"
    },
    "end_location": [75.5, 55.5],
    "body_part": {
      "id": 40,
      "name": "Right Foot"
    },
    "technique": {
      "id": 93,
      "name": "Straight"
    },
    "outcome": {
      "id": 8,
      "name": "Complete"
    }
  }
}
```

### Olay Tipleri
```python
EVENT_TYPES = {
    "Pass": 30,
    "Offside Pass": 31,
    "Foul Committed": 2,
    "Tackle": 7,
    "Interception": 8,
    "Turnover": 3,
    "Shot": 14,
    "Goalkeeper": 23,
    "Clearance": 12,
    "Miscontrol": 17,
    "Duel": 4,
    "Pressure": 17,
    "Half Start": 35,
    "Half End": 36,
    "Ball Recovery": 50,
    "Dispossessed": 3,
    "Error": 5,
    "Keeper Throw": 49,
    "Keeper Pickup": 51,
    "Keeper Sweeper": 52,
    "Keeper Punch": 53,
    "Keeper Drop": 54,
}
```

---

## 2. BACKEND KURULUMU

### Adım 1: Bağımlılıkları Yükle
```bash
pip install statsbomb-python pandas numpy requests
```

### Adım 2: StatsBomb Veri Yükleme Modülü
```python
# backend/app/data/statsbomb_loader.py (YENİ)
import requests
import json
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class StatsBombLoader:
    """StatsBomb Open Data'dan veri yükle"""
    
    BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
    
    def __init__(self, cache_dir: str = "./statsbomb_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def load_competitions(self) -> List[Dict[str, Any]]:
        """Tüm yarışmaları yükle"""
        url = f"{self.BASE_URL}/competitions.json"
        return self._fetch_and_cache(url, "competitions.json")
    
    def load_matches(self, competition_id: int, season_id: int = None) -> List[Dict[str, Any]]:
        """Belirli yarışmanın maçlarını yükle"""
        url = f"{self.BASE_URL}/matches/{competition_id}.json"
        cache_file = f"matches_{competition_id}.json"
        
        matches = self._fetch_and_cache(url, cache_file)
        
        if season_id:
            matches = [m for m in matches if m.get("season", {}).get("season_id") == season_id]
        
        return matches
    
    def load_events(self, match_id: int) -> List[Dict[str, Any]]:
        """Maç olaylarını yükle"""
        url = f"{self.BASE_URL}/events/{match_id}.json"
        cache_file = f"events_{match_id}.json"
        
        return self._fetch_and_cache(url, cache_file)
    
    def _fetch_and_cache(self, url: str, cache_file: str) -> Any:
        """URL'den veri çek ve cache'le"""
        cache_path = self.cache_dir / cache_file
        
        # Cache'den oku
        if cache_path.exists():
            logger.info(f"Cache'den yükleniyor: {cache_file}")
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # URL'den indir
        logger.info(f"İndiriliyor: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Cache'e kaydet
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return data
        except Exception as e:
            logger.error(f"Veri indirme hatası: {e}")
            raise

# Kullanım
loader = StatsBombLoader()
competitions = loader.load_competitions()
matches = loader.load_matches(competition_id=11)  # La Liga
events = loader.load_events(match_id=2499700)
```

### Adım 3: Veri Dönüştürme Modülü
```python
# backend/app/engine/statsbomb_converter.py (YENİ)
import logging
from typing import List, Dict, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

class StatsBombConverter:
    """StatsBomb olaylarını taktiksel metriklere dönüştür"""
    
    def __init__(self):
        self.event_types = {
            "Pass": 30,
            "Shot": 14,
            "Tackle": 7,
            "Interception": 8,
            "Pressure": 17,
            "Duel": 4,
            "Clearance": 12,
            "Miscontrol": 17,
            "Foul Committed": 2,
            "Ball Recovery": 50,
        }
    
    def convert_to_tactical_metrics(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """StatsBomb olaylarını taktiksel metriklere dönüştür"""
        
        home_team_id = None
        away_team_id = None
        
        # Takım ID'lerini bul
        for event in events:
            if home_team_id is None:
                home_team_id = event.get("possession_team", {}).get("id")
            if away_team_id is None and event.get("possession_team", {}).get("id") != home_team_id:
                away_team_id = event.get("possession_team", {}).get("id")
            if home_team_id and away_team_id:
                break
        
        # Metrikleri hesapla
        metrics = {
            "possession": self._calculate_possession(events, home_team_id, away_team_id),
            "passes": self._calculate_passes(events, home_team_id, away_team_id),
            "shots": self._calculate_shots(events, home_team_id, away_team_id),
            "tackles": self._calculate_tackles(events, home_team_id, away_team_id),
            "pressures": self._calculate_pressures(events, home_team_id, away_team_id),
            "duels": self._calculate_duels(events, home_team_id, away_team_id),
            "clearances": self._calculate_clearances(events, home_team_id, away_team_id),
        }
        
        return metrics
    
    def _calculate_possession(self, events: List[Dict], home_id: int, away_id: int) -> Dict[str, float]:
        """Top hakimiyetini hesapla"""
        home_touches = 0
        away_touches = 0
        
        for event in events:
            team_id = event.get("possession_team", {}).get("id")
            if event.get("type", {}).get("name") in ["Pass", "Shot", "Tackle", "Clearance"]:
                if team_id == home_id:
                    home_touches += 1
                elif team_id == away_id:
                    away_touches += 1
        
        total = home_touches + away_touches
        if total == 0:
            return {"home": 50.0, "away": 50.0}
        
        return {
            "home": round((home_touches / total) * 100, 1),
            "away": round((away_touches / total) * 100, 1),
        }
    
    def _calculate_passes(self, events: List[Dict], home_id: int, away_id: int) -> Dict[str, Dict]:
        """Pas istatistiklerini hesapla"""
        home_passes = {"completed": 0, "total": 0}
        away_passes = {"completed": 0, "total": 0}
        
        for event in events:
            if event.get("type", {}).get("name") == "Pass":
                team_id = event.get("possession_team", {}).get("id")
                outcome = event.get("pass", {}).get("outcome", {}).get("name")
                
                if team_id == home_id:
                    home_passes["total"] += 1
                    if outcome == "Complete" or outcome is None:
                        home_passes["completed"] += 1
                elif team_id == away_id:
                    away_passes["total"] += 1
                    if outcome == "Complete" or outcome is None:
                        away_passes["completed"] += 1
        
        return {
            "home": home_passes,
            "away": away_passes,
        }
    
    def _calculate_shots(self, events: List[Dict], home_id: int, away_id: int) -> Dict[str, int]:
        """Şut istatistiklerini hesapla"""
        home_shots = 0
        away_shots = 0
        
        for event in events:
            if event.get("type", {}).get("name") == "Shot":
                team_id = event.get("possession_team", {}).get("id")
                if team_id == home_id:
                    home_shots += 1
                elif team_id == away_id:
                    away_shots += 1
        
        return {"home": home_shots, "away": away_shots}
    
    def _calculate_tackles(self, events: List[Dict], home_id: int, away_id: int) -> Dict[str, int]:
        """Müdahale istatistiklerini hesapla"""
        home_tackles = 0
        away_tackles = 0
        
        for event in events:
            if event.get("type", {}).get("name") == "Tackle":
                team_id = event.get("possession_team", {}).get("id")
                if team_id == home_id:
                    home_tackles += 1
                elif team_id == away_id:
                    away_tackles += 1
        
        return {"home": home_tackles, "away": away_tackles}
    
    def _calculate_pressures(self, events: List[Dict], home_id: int, away_id: int) -> Dict[str, int]:
        """Baskı istatistiklerini hesapla"""
        home_pressures = 0
        away_pressures = 0
        
        for event in events:
            if event.get("type", {}).get("name") == "Pressure":
                team_id = event.get("possession_team", {}).get("id")
                if team_id == home_id:
                    home_pressures += 1
                elif team_id == away_id:
                    away_pressures += 1
        
        return {"home": home_pressures, "away": away_pressures}
    
    def _calculate_duels(self, events: List[Dict], home_id: int, away_id: int) -> Dict[str, int]:
        """Duel istatistiklerini hesapla"""
        home_duels = 0
        away_duels = 0
        
        for event in events:
            if event.get("type", {}).get("name") == "Duel":
                team_id = event.get("possession_team", {}).get("id")
                if team_id == home_id:
                    home_duels += 1
                elif team_id == away_id:
                    away_duels += 1
        
        return {"home": home_duels, "away": away_duels}
    
    def _calculate_clearances(self, events: List[Dict], home_id: int, away_id: int) -> Dict[str, int]:
        """Temizleme istatistiklerini hesapla"""
        home_clearances = 0
        away_clearances = 0
        
        for event in events:
            if event.get("type", {}).get("name") == "Clearance":
                team_id = event.get("possession_team", {}).get("id")
                if team_id == home_id:
                    home_clearances += 1
                elif team_id == away_id:
                    away_clearances += 1
        
        return {"home": home_clearances, "away": away_clearances}
    
    def convert_to_alerts(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """StatsBomb olaylarından uyarılar oluştur"""
        alerts = []
        
        for event in events:
            event_type = event.get("type", {}).get("name")
            
            # Hata
            if event_type == "Error":
                alerts.append({
                    "type": "ball_loss",
                    "timestamp": self._parse_timestamp(event.get("timestamp")),
                    "player_id": event.get("player", {}).get("id"),
                    "team_id": event.get("possession_team", {}).get("id"),
                    "severity": "medium",
                    "description": "Hata nedeniyle top kaybı",
                })
            
            # Miscontrol
            elif event_type == "Miscontrol":
                alerts.append({
                    "type": "miscontrol",
                    "timestamp": self._parse_timestamp(event.get("timestamp")),
                    "player_id": event.get("player", {}).get("id"),
                    "team_id": event.get("possession_team", {}).get("id"),
                    "severity": "low",
                    "description": "Top kontrolü kaybı",
                })
            
            # Dispossessed
            elif event_type == "Dispossessed":
                alerts.append({
                    "type": "dispossessed",
                    "timestamp": self._parse_timestamp(event.get("timestamp")),
                    "player_id": event.get("player", {}).get("id"),
                    "team_id": event.get("possession_team", {}).get("id"),
                    "severity": "high",
                    "description": "Top çalındı",
                })
            
            # Offside Pass
            elif event_type == "Offside Pass":
                alerts.append({
                    "type": "offside",
                    "timestamp": self._parse_timestamp(event.get("timestamp")),
                    "player_id": event.get("player", {}).get("id"),
                    "team_id": event.get("possession_team", {}).get("id"),
                    "severity": "high",
                    "description": "Ofsayt pozisyonunda pas",
                })
        
        return alerts
    
    def _parse_timestamp(self, timestamp_str: str) -> float:
        """Timestamp'i saniyeye dönüştür"""
        if not timestamp_str:
            return 0.0
        
        parts = timestamp_str.split(":")
        minutes = int(parts[0])
        seconds = int(parts[1])
        milliseconds = int(parts[2].split(".")[0]) if len(parts) > 2 else 0
        
        return minutes * 60 + seconds + milliseconds / 1000
```

### Adım 4: API Endpoints
```python
# backend/app/api/statsbomb.py (YENİ)
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.data.statsbomb_loader import StatsBombLoader
from app.engine.statsbomb_converter import StatsBombConverter

router = APIRouter(prefix="/statsbomb", tags=["statsbomb"])

loader = StatsBombLoader()
converter = StatsBombConverter()

@router.get("/competitions")
def get_competitions():
    """Tüm yarışmaları getir"""
    return loader.load_competitions()

@router.get("/matches/{competition_id}")
def get_matches(competition_id: int, season_id: int = None):
    """Yarışmanın maçlarını getir"""
    return loader.load_matches(competition_id, season_id)

@router.get("/events/{match_id}")
def get_events(match_id: int):
    """Maç olaylarını getir"""
    return loader.load_events(match_id)

@router.get("/metrics/{match_id}")
def get_metrics(match_id: int):
    """Maç metriklerini hesapla"""
    events = loader.load_events(match_id)
    metrics = converter.convert_to_tactical_metrics(events)
    return metrics

@router.get("/alerts/{match_id}")
def get_alerts(match_id: int):
    """Maç uyarılarını getir"""
    events = loader.load_events(match_id)
    alerts = converter.convert_to_alerts(events)
    return alerts
```

### Adım 5: Main.py'ye Ekle
```python
# backend/app/main.py
from app.api import statsbomb

app.include_router(statsbomb.router)
```

---

## 3. DOĞRULAMA SİSTEMİ

### Adım 1: Doğrulama Motoru
```python
# backend/app/engine/validation.py (YENİ)
import logging
from typing import List, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

class ValidationEngine:
    """YOLO tespitleri vs StatsBomb verileri karşılaştır"""
    
    def __init__(self, distance_threshold: float = 50.0):
        """
        distance_threshold: Piksel cinsinden eşleştirme mesafesi
        """
        self.distance_threshold = distance_threshold
    
    def validate_detection_vs_statsbomb(self,
                                       yolo_detections: List[Dict],
                                       statsbomb_events: List[Dict]) -> Dict[str, Any]:
        """YOLO tespitleri vs StatsBomb karşılaştırması"""
        
        results = {
            "total_yolo_detections": len(yolo_detections),
            "total_statsbomb_events": len(statsbomb_events),
            "matched": 0,
            "unmatched_yolo": [],
            "unmatched_statsbomb": [],
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
        }
        
        matched_yolo = set()
        matched_statsbomb = set()
        
        # Eşleştirme yap
        for i, yolo_det in enumerate(yolo_detections):
            for j, sb_event in enumerate(statsbomb_events):
                if self._is_match(yolo_det, sb_event):
                    results["matched"] += 1
                    matched_yolo.add(i)
                    matched_statsbomb.add(j)
                    break
        
        # Eşleşmeyenleri kaydet
        results["unmatched_yolo"] = [
            yolo_detections[i] for i in range(len(yolo_detections))
            if i not in matched_yolo
        ]
        results["unmatched_statsbomb"] = [
            statsbomb_events[j] for j in range(len(statsbomb_events))
            if j not in matched_statsbomb
        ]
        
        # Metrikleri hesapla
        if len(yolo_detections) > 0:
            results["precision"] = results["matched"] / len(yolo_detections)
        
        if len(statsbomb_events) > 0:
            results["recall"] = results["matched"] / len(statsbomb_events)
        
        if results["precision"] + results["recall"] > 0:
            results["f1_score"] = 2 * (
                (results["precision"] * results["recall"]) /
                (results["precision"] + results["recall"])
            )
        
        results["accuracy"] = results["matched"] / max(
            len(yolo_detections),
            len(statsbomb_events)
        )
        
        return results
    
    def _is_match(self, yolo_det: Dict, sb_event: Dict) -> bool:
        """YOLO tespiti vs StatsBomb olayı eşleşme kontrolü"""
        
        # Zaman kontrolü (±1 saniye)
        yolo_time = yolo_det.get("timestamp", 0)
        sb_time = self._parse_timestamp(sb_event.get("timestamp", "00:00:00.000"))
        
        if abs(yolo_time - sb_time) > 1.0:
            return False
        
        # Konum kontrolü (±50 piksel)
        yolo_pos = yolo_det.get("position", [0, 0])
        sb_pos = sb_event.get("location", [0, 0])
        
        distance = np.sqrt(
            (yolo_pos[0] - sb_pos[0]) ** 2 +
            (yolo_pos[1] - sb_pos[1]) ** 2
        )
        
        if distance > self.distance_threshold:
            return False
        
        return True
    
    def _parse_timestamp(self, timestamp_str: str) -> float:
        """Timestamp'i saniyeye dönüştür"""
        if not timestamp_str:
            return 0.0
        
        parts = timestamp_str.split(":")
        minutes = int(parts[0])
        seconds = int(parts[1])
        
        return minutes * 60 + seconds
```

### Adım 2: Doğrulama API Endpoint'i
```python
# backend/app/api/validation.py (YENİ)
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.engine.validation import ValidationEngine
from app.data.statsbomb_loader import StatsBombLoader
from app.cv.detector import get_detector
import cv2

router = APIRouter(prefix="/validation", tags=["validation"])

validator = ValidationEngine()
loader = StatsBombLoader()

@router.post("/compare/{match_id}")
def compare_yolo_vs_statsbomb(
    match_id: int,
    video_path: str,
    session: Session = Depends(get_session)
):
    """YOLO vs StatsBomb karşılaştırması"""
    
    # YOLO tespitleri
    detector = get_detector()
    yolo_detections = []
    
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_idx % 5 == 0:  # Her 5. frame
            detections = detector.detect_frame(frame, frame_idx)
            yolo_detections.append(detections)
        
        frame_idx += 1
    
    cap.release()
    
    # StatsBomb olayları
    statsbomb_events = loader.load_events(match_id)
    
    # Karşılaştırma
    results = validator.validate_detection_vs_statsbomb(
        yolo_detections,
        statsbomb_events
    )
    
    return results
```

---

## 4. TEST PLANI

### Test 1: Veri Yükleme
```python
def test_statsbomb_loading():
    loader = StatsBombLoader()
    
    # Yarışmaları yükle
    competitions = loader.load_competitions()
    assert len(competitions) > 0
    
    # La Liga maçlarını yükle
    matches = loader.load_matches(11)
    assert len(matches) > 0
    
    # İlk maçın olaylarını yükle
    events = loader.load_events(matches[0]["match_id"])
    assert len(events) > 0
```

### Test 2: Veri Dönüştürme
```python
def test_statsbomb_conversion():
    loader = StatsBombLoader()
    converter = StatsBombConverter()
    
    # Maç olaylarını yükle
    events = loader.load_events(2499700)
    
    # Metrikleri hesapla
    metrics = converter.convert_to_tactical_metrics(events)
    
    assert "possession" in metrics
    assert metrics["possession"]["home"] + metrics["possession"]["away"] == 100.0
    assert "passes" in metrics
    assert "shots" in metrics
```

### Test 3: Doğrulama
```python
def test_validation():
    validator = ValidationEngine()
    
    # Mock veriler
    yolo_detections = [
        {"timestamp": 10.0, "position": [100, 100]},
        {"timestamp": 11.0, "position": [110, 110]},
    ]
    
    statsbomb_events = [
        {"timestamp": "00:10:00.000", "location": [100, 100]},
        {"timestamp": "00:11:00.000", "location": [110, 110]},
    ]
    
    results = validator.validate_detection_vs_statsbomb(
        yolo_detections,
        statsbomb_events
    )
    
    assert results["matched"] == 2
    assert results["accuracy"] == 1.0
```

---

## 5. ZAMAN ÇIZELGESI

| Hafta | Görev |
|-------|-------|
| 1 | StatsBomb veri yükleme modülü |
| 1 | Veri dönüştürme modülü |
| 2 | Doğrulama sistemi |
| 2 | API endpoints |
| 3 | Test ve optimizasyon |

---

## 6. BAŞARI KRİTERLERİ

✅ **Tamamlandı Sayılacak**:
- [ ] StatsBomb verileri başarıyla yükleniyor
- [ ] Veri dönüştürme hatasız çalışıyor
- [ ] YOLO vs StatsBomb karşılaştırması yapılıyor
- [ ] Doğruluk metrikleri hesaplanıyor
- [ ] Tüm testler geçiyor
- [ ] Dokümantasyon tamamlanmış

