# 🚀 PitchVision - Hızlı Başlangıç

## ✅ Hazırlık Tamamlandı

- ✅ Redis kuruldu ve çalışıyor
- ✅ PostgreSQL kuruldu ve çalışıyor
- ✅ Database `pitchvision_lite` oluşturuldu
- ✅ User `pitchvision` oluşturuldu
- ✅ Virtual environment oluşturuldu: `backend/venv`

---

## 📦 Kalan Adımlar

### 1. Backend Dependencies (Devam Ediyor)

Terminal'de şu komut çalışıyor (arka planda devam edebilir):
```bash
source backend/venv/bin/activate && pip install -r backend/requirements.txt
```

**Alternatif:** Yeni terminal'de manuel çalıştır:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Database Migration

Dependencies kurulumu bittikten sonra:
```bash
cd backend
source venv/bin/activate

# Alembic migration oluştur
alembic revision --autogenerate -m "Add tactical engine models"

# Migration'ı uygula
alembic upgrade head
```

### 3. Backend'i Başlat

**Otomatik (Script ile):**
```bash
./start_backend.sh
```

**Manuel:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Test et:**
```bash
curl http://localhost:8000/health
# Beklenen: {"status":"healthy"}
```

### 4. Worker'ı Başlat (Opsiyonel)

**Yeni terminal aç:**
```bash
./start_worker.sh
```

### 5. Frontend'i Başlat

**Yeni terminal aç:**
```bash
cd frontend

# İlk seferinde dependencies kur
npm install

# Development server'ı başlat
npm run dev
```

**Tarayıcıda aç:** http://localhost:3000

---

## 🎯 Test Senaryosu

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/api/ai/health
   ```

2. **Frontend'e Git:**
   - http://localhost:3000
   - Login yap (eğer auth varsa)
   - Maç listesine git
   - Yeni maç oluştur veya mevcut maçı aç

3. **Maç Detay Sayfası:**
   - `/matches/[id]` sayfasına git
   - **Genel Bakış** → Video player görünüyor mu?
   - **Yapay Zeka Analizi** → Segmentler yükleniyor mu?
   - **Notlarım** → Event tagger çalışıyor mu?
   - **Karşılaştırma** → Comparison data var mı?

---

## 🐛 Sorun Giderme

### Redis bağlantı hatası:
```bash
redis-cli ping  # PONG dönmeli
brew services restart redis
```

### PostgreSQL bağlantı hatası:
```bash
pg_isready  # accepting connections dönmeli
brew services restart postgresql@14
```

### NVIDIA API hatası:
API key'i test et:
```bash
curl -H "Authorization: Bearer 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" \
  https://integrate.api.nvidia.com/v1/models
```

### Frontend API bağlantı hatası:
`.env` dosyasında kontrol et:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📊 Servis Durumu

**Kontrol et:**
```bash
# Redis
brew services list | grep redis

# PostgreSQL
brew services list | grep postgresql

# Backend (çalışıyorsa)
curl http://localhost:8000/health

# Frontend (çalışıyorsa)
curl http://localhost:3000
```

---

## 🎬 Sonraki Adımlar

1. ✅ Dependencies kurulumunu tamamla
2. ✅ Database migration yap
3. ✅ Backend'i başlat
4. ✅ Frontend'i başlat
5. ✅ Test et
6. 🎉 Kullanmaya başla!

---

**Hazır olduğunda bana haber ver, birlikte test edelim! 🚀**
