# PitchVision Lite - Hızlı Başlangıç

## 🚀 5 Dakikada Başlat

### 1. Gereksinimler
- Docker & Docker Compose
- Git

### 2. Projeyi Klonla ve Başlat

```bash
# Projeyi klonla
git clone <repo-url>
cd pitchvision-lite

# Environment dosyasını oluştur
cp .env.example .env

# Docker ile başlat
docker-compose up -d

# Logları izle
docker-compose logs -f
```

### 3. İlk Kullanıcıyı Oluştur

```bash
# Backend container'a gir
docker-compose exec backend python

# Python shell'de:
from app.database import engine
from sqlmodel import Session
from app.models.user import User
from app.auth import get_password_hash

with Session(engine) as session:
    user = User(
        email="admin@pitchvision.com",
        full_name="Admin User",
        role="admin",
        organization="Demo Kulübü",
        hashed_password=get_password_hash("demo123")
    )
    session.add(user)
    session.commit()
    print(f"User created: {user.email}")
```

### 4. Uygulamaya Eriş

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001

**Demo Giriş:**
- Email: `admin@pitchvision.com`
- Şifre: `demo123`

## 📝 İlk Maç Analizi

### 1. Takım Oluştur
1. Dashboard'a git
2. "Yeni Takım" butonuna tıkla
3. Takım bilgilerini gir:
   - İsim: "U15 Takımı"
   - Yaş Grubu: "U15"
   - Sezon: "2024-2025"

### 2. Oyuncu Ekle
1. Takım detayına git
2. "Oyuncu Ekle" butonuna tıkla
3. Oyuncu bilgilerini gir

### 3. Maç Oluştur ve Video Yükle
1. "Yeni Maç" butonuna tıkla
2. Maç bilgilerini gir:
   - Rakip: "Örnek Spor Kulübü"
   - Tarih: Bugün
   - Lokasyon: "Ana Saha"
3. Video yükle (veya mock analiz başlat)

### 4. Analiz Sonuçlarını Görüntüle
1. Maç listesinden maçı seç
2. Analiz tamamlanınca:
   - Taktiksel metrikleri gör
   - Uyarıları incele
   - Antrenman önerilerini oku
   - Oyuncu pasaportlarını kontrol et

## 🛠️ Development Mode

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000

# Start worker
python -m app.worker
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## 🧪 Mock vs Real CV Pipeline

### Mock Mode (Default)
- `CV_MOCK_MODE=true` in `.env`
- Generates realistic fake tracking data
- No YOLO model needed
- Fast processing for demo

### Real Mode
1. Download YOLO model
2. Place in `backend/models/yolov8n.pt`
3. Set `CV_MOCK_MODE=false`
4. Restart services

## 📊 API Kullanımı

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@pitchvision.com&password=demo123"

# Response: {"access_token": "...", "token_type": "bearer"}
```

### Create Team

```bash
curl -X POST http://localhost:8000/api/teams \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "U15 Takımı",
    "age_group": "U15",
    "season": "2024-2025"
  }'
```

### List Matches

```bash
curl http://localhost:8000/api/matches?team_id=1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Stop conflicting services
docker-compose down
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:8000 | xargs kill -9  # Backend
```

### Database Connection Error
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
# Wait 10 seconds
docker-compose up -d
```

### Worker Not Processing
```bash
# Check worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker

# Check Redis
docker-compose exec redis redis-cli ping
```

### Frontend Build Error
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

## 📚 Sonraki Adımlar

1. **Stitch Tasarımlarını İncele**: `stitch_pitchvision_lite.zip` dosyasındaki HTML/CSS'leri incele
2. **UI Bileşenlerini Geliştir**: Frontend component'lerini Stitch tasarımlarına göre güncelle
3. **Gerçek CV Pipeline**: YOLO modelini entegre et
4. **Saha Kalibrasyonu**: Canvas tabanlı kalibrasyon arayüzü ekle
5. **Video Player**: Video analiz görüntüleme ekranını tamamla
6. **Raporlama**: PDF rapor oluşturma özelliği ekle
7. **Scouting**: Scouting modülünü geliştir

## 💡 İpuçları

- **Mock Data**: Hızlı test için mock data generator'ları kullan
- **Hot Reload**: Development mode'da kod değişiklikleri otomatik yüklenir
- **API Docs**: http://localhost:8000/docs adresinden interaktif API dokümantasyonuna eriş
- **Database**: PostgreSQL'e `psql -h localhost -U pitchvision -d pitchvision_lite` ile bağlan
- **Redis**: `docker-compose exec redis redis-cli` ile Redis'e bağlan

## 🎯 Demo Senaryosu

1. ✅ Kullanıcı girişi yap
2. ✅ Takım oluştur
3. ✅ 3-4 oyuncu ekle
4. ✅ Maç oluştur
5. ✅ Mock analiz başlat
6. ✅ Analiz sonuçlarını görüntüle
7. ✅ Taktiksel uyarıları incele
8. ✅ Antrenman önerilerini oku
9. ✅ Oyuncu pasaportunu kontrol et

Toplam süre: ~10 dakika
