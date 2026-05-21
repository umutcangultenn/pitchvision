# 🚀 PitchVision Local Test Kurulum Rehberi

## Ön Gereksinimler

✅ PostgreSQL kurulu (tespit edildi: `/opt/homebrew/bin/psql`)  
❌ Redis kurulu değil  
❌ Docker kurulu değil

---

## 1️⃣ Redis Kurulumu (Gerekli)

```bash
# Homebrew ile Redis kur
brew install redis

# Redis'i başlat
brew services start redis

# Test et
redis-cli ping
# Beklenen çıktı: PONG
```

---

## 2️⃣ PostgreSQL Database Oluştur

```bash
# PostgreSQL'e bağlan
psql postgres

# Database oluştur
CREATE DATABASE pitchvision_lite;
CREATE USER pitchvision WITH PASSWORD 'pitchvision_dev_password';
GRANT ALL PRIVILEGES ON DATABASE pitchvision_lite TO pitchvision;
\q
```

---

## 3️⃣ Python Virtual Environment

```bash
# Backend dizinine git
cd backend

# Virtual environment oluştur
python3 -m venv venv

# Aktif et
source venv/bin/activate

# Dependencies kur
pip install -r requirements.txt
```

---

## 4️⃣ Database Migration (Alembic)

```bash
# Backend dizininde (venv aktif)
cd backend

# Migration dosyaları oluştur
alembic revision --autogenerate -m "Add tactical engine models"

# Migration'ları uygula
alembic upgrade head
```

**NOT:** Eğer Alembic kurulu değilse:
```bash
pip install alembic
```

---

## 5️⃣ Environment Variables (.env)

`.env` dosyası zaten oluşturuldu. Kontrol et:

```bash
cat .env
```

**Önemli:** NVIDIA API key'i zaten ekli:
```
NVIDIA_API_KEY="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"
```

---

## 6️⃣ Backend'i Başlat

```bash
# Backend dizininde (venv aktif)
cd backend

# FastAPI server'ı başlat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Beklenen çıktı:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Test et:**
```bash
curl http://localhost:8000/health
# Beklenen: {"status":"healthy"}
```

---

## 7️⃣ Worker'ı Başlat (Opsiyonel - Video İşleme İçin)

**Yeni terminal aç:**

```bash
cd backend
source venv/bin/activate
python app/worker.py
```

**Beklenen çıktı:**
```
PitchVision worker started, waiting for jobs...
```

---

## 8️⃣ Frontend'i Başlat

**Yeni terminal aç:**

```bash
cd frontend

# Dependencies kur (ilk seferinde)
npm install

# Development server'ı başlat
npm run dev
```

**Beklenen çıktı:**
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

---

## 9️⃣ Test Et

### Backend API Test:
```bash
# Health check
curl http://localhost:8000/health

# AI health check (NVIDIA API)
curl http://localhost:8000/api/ai/health
```

### Frontend Test:
Tarayıcıda aç: **http://localhost:3000**

---

## 🎯 Hızlı Test Senaryosu

1. **Frontend'e git:** http://localhost:3000
2. **Login yap** (eğer auth varsa)
3. **Yeni maç oluştur** veya mevcut maçı aç
4. **Maç detay sayfasına git:** `/matches/[id]`
5. **Sekmeleri test et:**
   - ✅ Genel Bakış → Video player görünüyor mu?
   - ✅ Yapay Zeka Analizi → Segmentler yükleniyor mu?
   - ✅ Notlarım → Event tagger çalışıyor mu?
   - ✅ Karşılaştırma → Comparison data var mı?

---

## 🐛 Sorun Giderme

### Redis bağlantı hatası:
```bash
# Redis çalışıyor mu kontrol et
redis-cli ping

# Çalışmıyorsa başlat
brew services start redis
```

### PostgreSQL bağlantı hatası:
```bash
# PostgreSQL çalışıyor mu kontrol et
pg_isready

# Çalışmıyorsa başlat
brew services start postgresql
```

### NVIDIA API hatası:
```bash
# API key'i test et
curl -H "Authorization: Bearer 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" \
  https://integrate.api.nvidia.com/v1/models
```

### Frontend API bağlantı hatası:
`.env` dosyasında kontrol et:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📦 Gerekli Paketler Özeti

### Backend:
- Python 3.9+
- PostgreSQL
- Redis
- FastAPI, SQLModel, Alembic, httpx

### Frontend:
- Node.js 18+
- Next.js 14
- React 18
- TailwindCSS

---

## 🎬 Video İşleme Test (Opsiyonel)

Gerçek video işleme test etmek için:

1. **YOLOv8 model indir:**
```bash
mkdir -p backend/models
cd backend/models
# YOLOv8n modelini indir (ultralytics'ten)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

2. **Test videosu yükle:**
```bash
mkdir -p backend/uploads
# Test videosu koy: backend/uploads/test_match.mp4
```

3. **Worker'da CV_MOCK_MODE=False olduğundan emin ol**

---

## ✅ Başarı Kriterleri

- [ ] Backend health check: `200 OK`
- [ ] NVIDIA API health check: `{"status":"online"}`
- [ ] Frontend açılıyor: `http://localhost:3000`
- [ ] Maç detay sayfası yükleniyor
- [ ] Segmentler görünüyor
- [ ] AI olayları listeleniyor
- [ ] Event tagger çalışıyor
- [ ] Video player render ediliyor

---

**Hazır olduğunda bana haber ver, adım adım ilerleyelim! 🚀**
