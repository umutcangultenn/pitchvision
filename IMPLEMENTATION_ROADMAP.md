# PitchVision Lite - Çalışır Hale Getirme Roadmap

**Başlangıç**: 20 Mayıs 2026  
**Hedef**: Production-ready sistem  
**Toplam Süre**: 3-4 hafta (paralel çalışma ile 2-3 hafta)

---

## FAZA 1: MOCK VERİLERİ KALDIRMA (5-6 gün)

### Gün 1-2: `/scouting` Sayfası

#### Backend Endpoints Oluştur
```python
# backend/app/api/scouting.py (YENİ)
```

**Yapılacaklar**:
- [ ] `GET /api/scouting/players` - Oyuncu listesi
- [ ] `GET /api/scouting/players/{player_id}/notes` - Oyuncu notları
- [ ] `POST /api/scouting/players/{player_id}/notes` - Not ekle
- [ ] Database queries yazılacak
- [ ] Response models oluşturulacak

**Dosyalar**:
- `backend/app/api/scouting.py` (YENİ)
- `backend/app/models/scout_note.py` (Kontrol et)

#### Frontend Güncelle
```typescript
// frontend/app/(app)/scouting/page.tsx
```

**Yapılacaklar**:
- [ ] `apiGetScoutingPlayers()` fonksiyonu ekle
- [ ] `apiGetScoutingNotes()` fonksiyonu ekle
- [ ] Mock import'ları kaldır
- [ ] useEffect ile veri çek
- [ ] Fallback mekanizması ekle

**Dosyalar**:
- `frontend/lib/api.ts` (Güncelle)
- `frontend/app/(app)/scouting/page.tsx` (Güncelle)

---

### Gün 3-4: `/drills` Sayfası

#### Backend Endpoints Oluştur
```python
# backend/app/api/drills.py (YENİ)
```

**Yapılacaklar**:
- [ ] `GET /api/drills` - Antrenman listesi
- [ ] `GET /api/drills?alert_type=...` - Filtreleme
- [ ] Database queries yazılacak
- [ ] Response models oluşturulacak

**Dosyalar**:
- `backend/app/api/drills.py` (YENİ)
- `backend/app/models/drill_recommendation.py` (Kontrol et)

#### Frontend Güncelle
```typescript
// frontend/app/(app)/drills/page.tsx
```

**Yapılacaklar**:
- [ ] `apiGetDrills()` fonksiyonu ekle
- [ ] Mock import'ları kaldır
- [ ] useEffect ile veri çek
- [ ] Fallback mekanizması ekle

**Dosyalar**:
- `frontend/lib/api.ts` (Güncelle)
- `frontend/app/(app)/drills/page.tsx` (Güncelle)

---

### Gün 5: Diğer Sayfalar

#### `/teams/[id]` Sayfası
- [ ] `apiGetTeamById()` fonksiyonu ekle
- [ ] Mock import'ları kaldır
- [ ] useEffect ile veri çek

#### `/players/[id]` Sayfası
- [ ] `apiGetPlayerById()` fonksiyonu ekle
- [ ] `apiGetPlayerPerformances()` fonksiyonu ekle
- [ ] `apiGetPlayerClips()` fonksiyonu ekle
- [ ] Mock import'ları kaldır

#### `/settings` Sayfası
- [ ] `apiGetPlayers()` fonksiyonu ekle
- [ ] Mock import'ları kaldır

**Dosyalar**:
- `frontend/lib/api.ts` (Güncelle)
- `frontend/app/(app)/teams/[id]/page.tsx` (Güncelle)
- `frontend/app/(app)/players/[id]/page.tsx` (Güncelle)
- `frontend/app/(app)/settings/page.tsx` (Güncelle)

---

### Gün 6: Fallback Mekanizması ve Temizlik

#### Fallback Hook Oluştur
```typescript
// frontend/hooks/useDataWithFallback.ts (YENİ)
```

**Yapılacaklar**:
- [ ] `useDataWithFallback()` hook oluştur
- [ ] Tüm sayfalar için uygula
- [ ] Error handling ekle

#### Mock Veri Dosyasını Temizle
**Yapılacaklar**:
- [ ] Tüm import'ları kontrol et
- [ ] `/components` sayfasını gizle
- [ ] `frontend/data/demo.ts` dosyasını sil (veya backup al)

**Dosyalar**:
- `frontend/hooks/useDataWithFallback.ts` (YENİ)
- `frontend/data/demo.ts` (SİL)

---

## FAZA 2: STATSBOMB ENTEGRASYONU (2-3 hafta)

### Hafta 1: Veri Yükleme ve Dönüştürme

#### Gün 1-2: StatsBomb Veri Yükleme Modülü
```python
# backend/app/data/statsbomb_loader.py (YENİ)
```

**Yapılacaklar**:
- [ ] `StatsBombLoader` sınıfı oluştur
- [ ] `load_competitions()` metodu
- [ ] `load_matches()` metodu
- [ ] `load_events()` metodu
- [ ] Cache mekanizması
- [ ] Error handling

**Dosyalar**:
- `backend/app/data/statsbomb_loader.py` (YENİ)
- `backend/requirements.txt` (Güncelle - requests, pandas)

#### Gün 3-4: Veri Dönüştürme Modülü
```python
# backend/app/engine/statsbomb_converter.py (YENİ)
```

**Yapılacaklar**:
- [ ] `StatsBombConverter` sınıfı oluştur
- [ ] `convert_to_tactical_metrics()` metodu
- [ ] `convert_to_alerts()` metodu
- [ ] Possession hesaplama
- [ ] Passes hesaplama
- [ ] Shots hesaplama
- [ ] Tackles hesaplama

**Dosyalar**:
- `backend/app/engine/statsbomb_converter.py` (YENİ)

#### Gün 5: API Endpoints
```python
# backend/app/api/statsbomb.py (YENİ)
```

**Yapılacaklar**:
- [ ] `GET /api/statsbomb/competitions`
- [ ] `GET /api/statsbomb/matches/{competition_id}`
- [ ] `GET /api/statsbomb/events/{match_id}`
- [ ] `GET /api/statsbomb/metrics/{match_id}`
- [ ] `GET /api/statsbomb/alerts/{match_id}`

**Dosyalar**:
- `backend/app/api/statsbomb.py` (YENİ)
- `backend/app/main.py` (Güncelle - router ekle)

---

### Hafta 2: Doğrulama Sistemi

#### Gün 1-2: Doğrulama Motoru
```python
# backend/app/engine/validation.py (YENİ)
```

**Yapılacaklar**:
- [ ] `ValidationEngine` sınıfı oluştur
- [ ] `validate_detection_vs_statsbomb()` metodu
- [ ] Eşleştirme algoritması
- [ ] Doğruluk metrikleri (precision, recall, F1)
- [ ] Mismatch detection

**Dosyalar**:
- `backend/app/engine/validation.py` (YENİ)

#### Gün 3-4: Doğrulama API Endpoints
```python
# backend/app/api/validation.py (YENİ)
```

**Yapılacaklar**:
- [ ] `POST /api/validation/compare/{match_id}`
- [ ] Video işleme
- [ ] YOLO tespitleri
- [ ] StatsBomb karşılaştırması
- [ ] Sonuçları döndür

**Dosyalar**:
- `backend/app/api/validation.py` (YENİ)
- `backend/app/main.py` (Güncelle - router ekle)

#### Gün 5: Frontend Bileşenleri
```typescript
// frontend/components/validation/ComparisonChart.tsx (YENİ)
```

**Yapılacaklar**:
- [ ] `ComparisonChart` bileşeni
- [ ] `AccuracyMetrics` bileşeni
- [ ] Doğruluk gösterimi
- [ ] Grafik ve tablolar

**Dosyalar**:
- `frontend/components/validation/ComparisonChart.tsx` (YENİ)
- `frontend/components/validation/AccuracyMetrics.tsx` (YENİ)
- `frontend/lib/api.ts` (Güncelle - validation endpoints)

---

### Hafta 3: Test ve Optimizasyon

#### Gün 1-2: Test Suite
```python
# backend/tests/test_statsbomb.py (YENİ)
```

**Yapılacaklar**:
- [ ] `test_statsbomb_loading()`
- [ ] `test_statsbomb_conversion()`
- [ ] `test_validation()`
- [ ] `test_yolo_vs_statsbomb()`
- [ ] Gerçek maç verileri ile test

**Dosyalar**:
- `backend/tests/test_statsbomb.py` (YENİ)
- `backend/tests/test_validation.py` (YENİ)

#### Gün 3-4: YOLO Optimizasyonu
```python
# backend/app/cv/detector.py (Güncelle)
```

**Yapılacaklar**:
- [ ] GPU desteği ekle (CUDA/Metal)
- [ ] Batch processing
- [ ] Frame sampling optimizasyonu
- [ ] Model seçimi (YOLOv8s vs YOLOv8n)
- [ ] Performance profiling

**Dosyalar**:
- `backend/app/cv/detector.py` (Güncelle)
- `backend/app/config.py` (Güncelle - GPU settings)
- `backend/requirements.txt` (Güncelle - torch, torchvision)

#### Gün 5: Performans Raporu
**Yapılacaklar**:
- [ ] İşlem süresi ölçümü
- [ ] Doğruluk metrikleri
- [ ] GPU kullanımı
- [ ] Memory profiling
- [ ] Rapor oluştur

---

## FAZA 3: PRODUCTION DEPLOYMENT (3-4 gün)

### Gün 1: Final Testing

**Yapılacaklar**:
- [ ] Tüm sayfalar test et
- [ ] Mock veri kalmadığını doğrula
- [ ] API endpoints test et
- [ ] Error handling test et
- [ ] Performance test et

### Gün 2: Documentation

**Yapılacaklar**:
- [ ] API dokümantasyonu
- [ ] Deployment rehberi
- [ ] Troubleshooting rehberi
- [ ] Architecture dokümantasyonu

### Gün 3: Deployment

**Yapılacaklar**:
- [ ] Production build
- [ ] Database migration
- [ ] Environment setup
- [ ] Monitoring setup

### Gün 4: Verification

**Yapılacaklar**:
- [ ] Production test
- [ ] Smoke test
- [ ] Performance monitoring
- [ ] Error monitoring

---

## PARALEL ÇALIŞMA PLANI

### Backend Team (2 kişi)
- **Kişi 1**: Mock veri kaldırma + StatsBomb entegrasyonu
- **Kişi 2**: Doğrulama sistemi + YOLO optimizasyonu

### Frontend Team (1 kişi)
- Mock veri kaldırma + Fallback mekanizması
- Validation bileşenleri

### QA Team (1 kişi)
- Test suite yazma
- Regression testing
- Performance testing

---

## BAŞARI KRİTERLERİ

### Faz 1 Tamamlandı
- [ ] Frontend'de mock import'ları sıfır
- [ ] Tüm sayfalar gerçek API'den veri alıyor
- [ ] Fallback mekanizması çalışıyor
- [ ] TypeScript hata yok
- [ ] Build başarılı

### Faz 2 Tamamlandı
- [ ] StatsBomb verileri başarıyla yükleniyor
- [ ] Veri dönüştürme hatasız çalışıyor
- [ ] Doğrulama sistemi çalışıyor
- [ ] Tüm testler geçiyor
- [ ] Doğruluk > %70

### Faz 3 Tamamlandı
- [ ] Production deployment başarılı
- [ ] Tüm sayfalar çalışıyor
- [ ] Performance acceptable
- [ ] Monitoring aktif
- [ ] Dokümantasyon tamamlanmış

---

## RISK YÖNETIMI

### Yüksek Risk
| Risk | Çözüm |
|------|-------|
| StatsBomb API kapalı | Lokal JSON dosyaları kullan |
| YOLO doğruluğu düşük | Model fine-tuning yap |
| Performance düşüşü | GPU optimizasyonu yap |

### Orta Risk
| Risk | Çözüm |
|------|-------|
| Veri tutarsızlığı | Veri doğrulama ekle |
| API rate limiting | Caching ekle |
| Database performance | Index ekle |

---

## ZAMAN ÇIZELGESI

```
Hafta 1 (5-6 gün)
├─ Gün 1-2: /scouting sayfası
├─ Gün 3-4: /drills sayfası
├─ Gün 5: Diğer sayfalar
└─ Gün 6: Fallback + Temizlik

Hafta 2 (5-6 gün)
├─ Gün 1-2: StatsBomb loader
├─ Gün 3-4: StatsBomb converter
├─ Gün 5: StatsBomb API endpoints
└─ Gün 6: Doğrulama motoru

Hafta 3 (5-6 gün)
├─ Gün 1-2: Doğrulama API
├─ Gün 3-4: Frontend bileşenleri
├─ Gün 5: Test suite
└─ Gün 6: YOLO optimizasyonu

Hafta 4 (3-4 gün)
├─ Gün 1: Final testing
├─ Gün 2: Documentation
├─ Gün 3: Deployment
└─ Gün 4: Verification

TOPLAM: 3-4 hafta
```

---

## BAŞLAMAK İÇİN

### Adım 1: Backend Setup
```bash
# Bağımlılıkları yükle
pip install statsbomb-python pandas numpy requests torch torchvision

# Yeni modülleri oluştur
touch backend/app/data/statsbomb_loader.py
touch backend/app/engine/statsbomb_converter.py
touch backend/app/engine/validation.py
touch backend/app/api/scouting.py
touch backend/app/api/drills.py
touch backend/app/api/statsbomb.py
touch backend/app/api/validation.py
```

### Adım 2: Frontend Setup
```bash
# Yeni hook oluştur
touch frontend/hooks/useDataWithFallback.ts

# Yeni bileşenler oluştur
mkdir -p frontend/components/validation
touch frontend/components/validation/ComparisonChart.tsx
touch frontend/components/validation/AccuracyMetrics.tsx
```

### Adım 3: Test Setup
```bash
# Test dosyaları oluştur
touch backend/tests/test_statsbomb.py
touch backend/tests/test_validation.py
```

---

## KONTROL LİSTESİ

### Faz 1
- [ ] `/scouting` sayfası tamamlandı
- [ ] `/drills` sayfası tamamlandı
- [ ] Diğer sayfalar tamamlandı
- [ ] Fallback mekanizması tamamlandı
- [ ] Mock veri dosyası silindi
- [ ] TypeScript hata yok
- [ ] Build başarılı

### Faz 2
- [ ] StatsBomb loader tamamlandı
- [ ] StatsBomb converter tamamlandı
- [ ] StatsBomb API endpoints tamamlandı
- [ ] Doğrulama motoru tamamlandı
- [ ] Doğrulama API endpoints tamamlandı
- [ ] Frontend bileşenleri tamamlandı
- [ ] Test suite tamamlandı

### Faz 3
- [ ] YOLO optimizasyonu tamamlandı
- [ ] Final testing tamamlandı
- [ ] Documentation tamamlandı
- [ ] Deployment başarılı
- [ ] Verification tamamlandı

---

**Hazırlayan**: AI Assistant  
**Tarih**: 20 Mayıs 2026  
**Durum**: 🟢 BAŞLAMAYA HAZIR

