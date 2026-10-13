# PitchVision Lite - Proje Durum Raporu

**Tarih**: 20 Mayıs 2026  
**Durum**: 🟡 KISMEN HAZIR (Mock Veriler Hala Mevcut)  
**Kritiklik**: YÜKSEK

---

## 1. GENEL PROJE DURUMU

### ✅ Tamamlanan Bileşenler
- Backend API (FastAPI) - Çalışıyor
- Frontend (Next.js) - Çalışıyor
- Worker Process - Çalışıyor
- PostgreSQL Database - Çalışıyor
- Redis Queue - Çalışıyor
- File Upload - Çalışıyor
- Report Generation - Çalışıyor (NVIDIA API)
- YOLO Detection - Entegre edildi

### 🟡 Eksik/Kısmi Bileşenler
- **Mock Veriler Frontend'de Hala Mevcut** ⚠️
- StatsBomb Entegrasyonu - Yapılmadı
- Gerçek Video Kesitleri - Yapılmadı
- Veri Doğrulama Sistemi - Yapılmadı

### ❌ Yapılmayan Bileşenler
- Gerçek maç verileri ile karşılaştırma
- Otomatik test suite
- Performans optimizasyonu

---

## 2. MOCK VERİ SORUNU - DETAYLI ANALİZ

### Frontend'de Mock Veriler Nerede Kullanılıyor?

```
frontend/data/demo.ts (ANA KAYNAK)
├── mockOrganizations (1 org)
├── mockTeams (2 takım)
├── mockPlayers (12 oyuncu)
├── mockMatches (2 maç)
├── mockVideos (2 video)
├── mockAlerts (8 uyarı)
├── mockClips (4 klip)
├── mockPerformances (12 performans)
├── mockScoutingNotes (4 not)
├── mockReports (2 rapor)
├── mockMetrics (6 metrik)
└── mockDrills (8 antrenman)
```

### Mock Veriler Kullanılan Sayfalar

| Sayfa | Mock Veriler | Durum |
|-------|-------------|-------|
| `/matches` | ❌ Kaldırıldı | ✅ Gerçek API |
| `/matches/[id]` | ⚠️ Fallback | 🟡 Kısmi |
| `/matches/[id]/analysis` | ⚠️ Fallback | 🟡 Kısmi |
| `/matches/[id]/report` | ⚠️ Fallback | 🟡 Kısmi |
| `/players/[id]` | ⚠️ Fallback | 🟡 Kısmi |
| `/teams/[id]` | ⚠️ Fallback | 🟡 Kısmi |
| `/scouting` | ✅ Tamamen Mock | ❌ Sorun |
| `/drills` | ✅ Tamamen Mock | ❌ Sorun |
| `/components` | ✅ Tamamen Mock | ❌ Sorun |
| `/settings` | ⚠️ Kısmi Mock | 🟡 Sorun |

### Kritik Sayfalar (Mock Veriler Kaldırılması Gerekli)

1. **`/scouting` - Oyuncu İzleme**
   - Tamamen `mockPlayers` ve `mockScoutingNotes` kullanıyor
   - Gerçek oyuncu verilerine bağlanması gerekli

2. **`/drills` - Antrenman Önerileri**
   - Tamamen `mockDrills` kullanıyor
   - Gerçek uyarılardan dinamik olarak oluşturulması gerekli

3. **`/components` - Bileşen Galerisi**
   - Demo amaçlı, kaldırılabilir veya gizlenebilir

---

## 3. YOLO VE CV PIPELINE DURUMU

### ✅ Mevcut Durum
```python
# backend/app/cv/detector.py
- MockDetector: Gerçekçi mock veriler üretiyor
- YOLODetector: Ultralytics YOLO entegre edildi
- Fallback mekanizması: Mock → YOLO → Hata
- CV_MOCK_MODE: False (Gerçek YOLO kullanılıyor)
```

### 🟡 Sorunlar
1. **YOLO Model**: Genel amaçlı model (futbol spesifik değil)
   - Hugging Face model: `aabyzov/easychamp-player-detection-yolov8`
   - Fallback: YOLOv8n (genel)

2. **Performans**: 500 frame işlemek ~4-5 saniye
   - Optimizasyon gerekli
   - GPU kullanılmıyor

3. **Doğruluk**: Gerçek maç verilerine karşı test edilmedi
   - StatsBomb verileri ile karşılaştırma yapılmadı

---

## 4. STATSBOMB VERİLERİ İLE ENTEGRASYON PLANI

### 4.1 StatsBomb Veri Yapısı
```json
{
  "match_id": 123456,
  "team_id": 1,
  "player_id": 456,
  "event_type": "Pass",
  "timestamp": "00:15:30",
  "location": [60.0, 40.0],
  "pass": {
    "recipient_id": 789,
    "length": 15.5,
    "angle": 45.0,
    "outcome": "Complete"
  }
}
```

### 4.2 Entegrasyon Adımları

#### Aşama 1: StatsBomb Veri İndirme
```python
# backend/app/data/statsbomb_loader.py (YENİ)
import requests
import json

class StatsBombLoader:
    BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
    
    def load_matches(self, competition_id: int):
        """Maçları indir"""
        url = f"{self.BASE_URL}/matches/{competition_id}.json"
        return requests.get(url).json()
    
    def load_events(self, match_id: int):
        """Maç olaylarını indir"""
        url = f"{self.BASE_URL}/events/{match_id}.json"
        return requests.get(url).json()
```

#### Aşama 2: Veri Dönüştürme
```python
# backend/app/engine/statsbomb_converter.py (YENİ)
class StatsBombConverter:
    def convert_to_tactical_metrics(self, events: list) -> dict:
        """StatsBomb olaylarını taktiksel metriklere dönüştür"""
        metrics = {
            "possession": self._calculate_possession(events),
            "passes": self._calculate_passes(events),
            "shots": self._calculate_shots(events),
            "pressures": self._calculate_pressures(events),
            "tackles": self._calculate_tackles(events),
        }
        return metrics
    
    def convert_to_alerts(self, events: list) -> list:
        """Olaylardan uyarılar oluştur"""
        alerts = []
        for event in events:
            if event['type']['name'] == 'Miscontrol':
                alerts.append({
                    'type': 'ball_loss',
                    'timestamp': event['timestamp'],
                    'player_id': event['player']['id'],
                })
        return alerts
```

#### Aşama 3: Video Kesitleri Eşleştirme
```python
# backend/app/engine/video_matcher.py (YENİ)
class VideoMatcher:
    def match_event_to_video(self, event: dict, video_path: str) -> dict:
        """StatsBomb olayını video kesitine eşleştir"""
        timestamp = self._parse_timestamp(event['timestamp'])
        
        # Video kesitini çıkar
        clip = {
            'start_time': timestamp - 2,  # 2 saniye öncesi
            'end_time': timestamp + 3,    # 3 saniye sonrası
            'event_type': event['type']['name'],
            'player_id': event['player']['id'],
        }
        
        return clip
```

#### Aşama 4: Doğrulama Sistemi
```python
# backend/app/engine/validation.py (YENİ)
class ValidationEngine:
    def validate_detection_vs_statsbomb(self, 
                                       yolo_detections: list,
                                       statsbomb_events: list) -> dict:
        """YOLO tespitlerini StatsBomb verileri ile karşılaştır"""
        
        results = {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'mismatches': [],
        }
        
        # Eşleştirme ve karşılaştırma
        for yolo_det in yolo_detections:
            matching_event = self._find_matching_event(
                yolo_det, statsbomb_events
            )
            
            if not matching_event:
                results['mismatches'].append(yolo_det)
        
        # Metrikleri hesapla
        results['accuracy'] = self._calculate_accuracy(
            yolo_detections, statsbomb_events
        )
        
        return results
```

---

## 5. MOCK VERİLERİ KALDIRMA PLANI

### Faz 1: Kritik Sayfalar (Bu Hafta)

#### `/scouting` Sayfası
```typescript
// BEFORE (Mock)
const allPlayers = mockPlayers.filter(p => p.teamId === teamId);

// AFTER (Real API)
const [players, setPlayers] = useState<Player[]>([]);

useEffect(() => {
  const fetchPlayers = async () => {
    const result = await apiGetPlayers();
    if (result.ok) {
      setPlayers(result.data.filter(p => p.teamId === teamId));
    }
  };
  fetchPlayers();
}, [teamId]);
```

#### `/drills` Sayfası
```typescript
// BEFORE (Mock)
const filteredDrills = mockDrills.filter(d => ...);

// AFTER (Real API)
const [drills, setDrills] = useState<DrillRecommendation[]>([]);

useEffect(() => {
  const fetchDrills = async () => {
    const result = await apiGetMatchDrills(matchId);
    if (result.ok) {
      setDrills(result.data);
    }
  };
  fetchDrills();
}, [matchId]);
```

### Faz 2: Fallback Mekanizmaları (Sonraki Hafta)

```typescript
// Tüm sayfalar için tutarlı fallback
const useDataWithFallback = async (apiCall, mockData) => {
  try {
    const result = await apiCall();
    return result.ok ? result.data : mockData;
  } catch {
    return mockData;
  }
};
```

### Faz 3: Mock Veri Dosyasını Kaldırma (2 Hafta Sonra)

```bash
# Adım 1: Tüm mock verileri API'ye taşı
# Adım 2: Frontend'den mock import'larını kaldır
# Adım 3: frontend/data/demo.ts dosyasını sil
```

---

## 6. TEST PLANI - STATSBOMB VERİLERİ İLE

### Test Maçları (StatsBomb Open Data)

```python
# Örnek maçlar
TEST_MATCHES = [
    {
        "competition": "La Liga",
        "season": "2017/18",
        "match_id": 2499700,  # Real Madrid vs Barcelona
        "teams": ["Real Madrid", "Barcelona"],
    },
    {
        "competition": "Premier League",
        "season": "2017/18",
        "match_id": 2499701,  # Manchester City vs Liverpool
        "teams": ["Manchester City", "Liverpool"],
    },
]
```

### Test Senaryoları

#### Test 1: Veri Yükleme
```python
def test_statsbomb_data_loading():
    loader = StatsBombLoader()
    matches = loader.load_matches(11)  # La Liga
    assert len(matches) > 0
    assert 'match_id' in matches[0]
```

#### Test 2: Veri Dönüştürme
```python
def test_statsbomb_conversion():
    converter = StatsBombConverter()
    events = load_test_events()
    metrics = converter.convert_to_tactical_metrics(events)
    
    assert 'possession' in metrics
    assert metrics['possession']['home'] > 0
    assert metrics['possession']['away'] > 0
```

#### Test 3: YOLO vs StatsBomb Karşılaştırması
```python
def test_yolo_vs_statsbomb():
    # Video'yu işle
    yolo_detections = process_video_with_yolo(video_path)
    
    # StatsBomb verilerini yükle
    statsbomb_events = load_statsbomb_events(match_id)
    
    # Karşılaştır
    validator = ValidationEngine()
    results = validator.validate_detection_vs_statsbomb(
        yolo_detections, 
        statsbomb_events
    )
    
    assert results['accuracy'] > 0.7  # %70+ doğruluk hedefi
```

#### Test 4: Video Kesitleri Eşleştirme
```python
def test_video_clip_matching():
    matcher = VideoMatcher()
    
    for event in statsbomb_events:
        clip = matcher.match_event_to_video(event, video_path)
        
        assert clip['start_time'] >= 0
        assert clip['end_time'] > clip['start_time']
        assert clip['event_type'] is not None
```

---

## 7. YOLO OPTIMIZASYON PLANI

### Mevcut Performans
- **İşlem Süresi**: 500 frame = 4-5 saniye
- **FPS**: ~100-125 frame/saniye
- **Doğruluk**: Bilinmiyor (test edilmedi)

### Optimizasyon Stratejileri

#### 1. Model Seçimi
```python
# Mevcut: YOLOv8n (nano)
# Alternatifler:
# - YOLOv8s (small) - Daha doğru, biraz yavaş
# - YOLOv8m (medium) - Çok doğru, daha yavaş
# - YOLOv8-pose - Oyuncu pozisyonları için

# Futbol spesifik modeller:
# - aabyzov/easychamp-player-detection-yolov8
# - ultralytics/yolov8-football
```

#### 2. GPU Kullanımı
```python
# Mevcut: CPU
# Hedef: GPU (CUDA/Metal)

# backend/app/config.py
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO("yolov8n.pt").to(DEVICE)
```

#### 3. Batch Processing
```python
# Mevcut: Frame-by-frame
# Hedef: Batch processing (8-16 frame)

def process_video_batch(video_path, batch_size=8):
    frames = []
    for frame in video_reader:
        frames.append(frame)
        if len(frames) == batch_size:
            detections = model.predict(frames, batch=True)
            yield detections
            frames = []
```

#### 4. Frame Sampling
```python
# Mevcut: Her 5. frame
# Hedef: Akıllı sampling

def smart_frame_sampling(video_path):
    # Hızlı hareket: Her frame
    # Yavaş hareket: Her 5. frame
    # Durgun: Her 10. frame
    
    prev_frame = None
    for frame in video_reader:
        motion = calculate_optical_flow(prev_frame, frame)
        
        if motion > HIGH_THRESHOLD:
            yield frame  # Her frame
        elif motion > MEDIUM_THRESHOLD:
            if frame_idx % 5 == 0:
                yield frame  # Her 5. frame
        else:
            if frame_idx % 10 == 0:
                yield frame  # Her 10. frame
```

---

## 8. PROJE ZAMAN ÇIZELGESI

### Bu Hafta (Haftası)
- [ ] Mock verileri `/scouting` sayfasından kaldır
- [ ] Mock verileri `/drills` sayfasından kaldır
- [ ] StatsBomb veri yükleme modülü oluştur

### Sonraki Hafta
- [ ] StatsBomb veri dönüştürme modülü oluştur
- [ ] Video kesitleri eşleştirme sistemi oluştur
- [ ] Doğrulama motoru oluştur

### 2 Hafta Sonra
- [ ] Test maçları ile test et
- [ ] YOLO optimizasyonu yap
- [ ] Performans raporunu hazırla

### 3 Hafta Sonra
- [ ] Tüm mock verileri kaldır
- [ ] Gerçek veri ile tam test
- [ ] Production deployment

---

## 9. TEKNIK GEREKSINIMLER

### Backend Bağımlılıkları (Yeni)
```txt
# requirements.txt'e eklenecek
statsbomb-python>=1.0.0
pandas>=1.3.0
numpy>=1.21.0
torch>=1.9.0  # GPU desteği için
torchvision>=0.10.0
```

### API Endpoints (Yeni)
```
GET /api/statsbomb/matches/{competition_id}
GET /api/statsbomb/events/{match_id}
POST /api/validation/compare-yolo-vs-statsbomb
GET /api/validation/results/{match_id}
```

### Frontend Bileşenleri (Yeni)
```
components/validation/ComparisonChart.tsx
components/validation/AccuracyMetrics.tsx
components/statsbomb/EventTimeline.tsx
```

---

## 10. RİSK ANALİZİ

### Yüksek Risk
| Risk | Etki | Çözüm |
|------|------|-------|
| StatsBomb API'si kapalı | Veri yüklenemez | Lokal JSON dosyaları |
| YOLO doğruluğu düşük | Yanlış analiz | Model fine-tuning |
| Video senkronizasyon | Yanlış eşleştirme | Timestamp doğrulaması |

### Orta Risk
| Risk | Etki | Çözüm |
|------|------|-------|
| Performans düşüşü | Yavaş işlem | GPU optimizasyonu |
| Veri tutarsızlığı | Hata | Veri doğrulama |
| API rate limiting | Veri yüklenemez | Caching |

### Düşük Risk
| Risk | Etki | Çözüm |
|------|------|-------|
| Mock veri kalıntıları | Karışıklık | Kod temizliği |
| Dokümantasyon eksikliği | Anlaşılmama | Wiki oluşturma |

---

## 11. BAŞARI KRİTERLERİ

### Faz 1: Mock Veriler Kaldırılması
- [ ] Frontend'de mock import'ları sıfır
- [ ] Tüm sayfalar gerçek API'den veri alıyor
- [ ] Fallback mekanizması çalışıyor

### Faz 2: StatsBomb Entegrasyonu
- [ ] StatsBomb verileri başarıyla yükleniyor
- [ ] Veri dönüştürme hatasız çalışıyor
- [ ] Video kesitleri doğru eşleştirilmiş

### Faz 3: Doğrulama Sistemi
- [ ] YOLO vs StatsBomb karşılaştırması yapılıyor
- [ ] Doğruluk metrikleri hesaplanıyor
- [ ] Raporlar otomatik oluşturuluyor

### Faz 4: Optimizasyon
- [ ] İşlem süresi < 2 saniye (500 frame)
- [ ] Doğruluk > %80
- [ ] GPU kullanımı aktif

---

## 12. SONUÇ VE ÖNERİLER

### Mevcut Durum Özeti
✅ **Yapılan**: Backend, API, Worker, YOLO entegrasyonu  
🟡 **Kısmi**: Mock veriler hala mevcut, test edilmedi  
❌ **Yapılmayan**: StatsBomb entegrasyonu, doğrulama sistemi

### Acil Yapılması Gerekenler
1. **Bu Hafta**: Mock verileri `/scouting` ve `/drills`'ten kaldır
2. **Sonraki Hafta**: StatsBomb veri yükleme sistemi oluştur
3. **2 Hafta Sonra**: Doğrulama motoru ve test suite oluştur

### Uzun Vadeli Hedefler
- Gerçek maç verileri ile %85+ doğruluk
- < 2 saniye işlem süresi
- Otomatik test ve doğrulama sistemi
- Production-ready sistem

---

**Rapor Hazırlayan**: AI Assistant  
**Tarih**: 20 Mayıs 2026  
**Durum**: 🟡 KISMEN HAZIR - MOCK VERİLER KALDIRMA VE STATSBOMB ENTEGRASYONU GEREKLİ

