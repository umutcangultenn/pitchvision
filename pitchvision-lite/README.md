# PitchVision Lite (monorepo MVP iskeleti)

Video tabanlı maç analizi, hafif scouting ve oyuncu gelişim pasaportu için **PitchVision Lite** ürününün production’a yakın MVP monorepo yapısı.

## Gereksinimler

- **Docker** ve Docker Compose *veya*
- **Python** 3.11+, **Node.js** 20+, **PostgreSQL** 16, **Redis** 7

## Hızlı başlangıç (Docker Compose)

1. Proje kökünde ortam dosyasını oluşturun:

   ```bash
   cp .env.example .env
   ```

2. Tüm servisleri ayağa kaldırın:

   ```bash
   docker compose up --build
   ```

3. Uygulama adresleri:

   - **Frontend:** http://localhost:3000 (ana sayfa → `/dashboard` yönlendirir)
   - **Backend API:** http://localhost:8000  
   - **Sağlık:** http://localhost:8000/health  
   - **API dokümantasyonu:** http://localhost:8000/docs  

> **Not:** Compose dosyası `env_file: .env` kullanır; `.env` yoksa `cp .env.example .env` ile oluşturun.

## Yerel kurulum (Docker olmadan)

### Veritabarı ve Redis

PostgreSQL ve Redis’in çalıştığından emin olun. `.env` içindeki `DATABASE_URL` ve `REDIS_URL` değerlerini kendi ortamınıza göre düzenleyin.

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

`NEXT_PUBLIC_API_URL` tarayıcıdan erişilebilir API adresi olmalıdır (varsayılan: `http://localhost:8000`).

## Veritabanı migration’ları (Alembic)

Migration’lar `backend/` dizininden çalıştırılır; `DATABASE_URL` ortam değişkeni Alembic tarafından kullanılır.

```bash
cd backend
# İlk revizyon örneği (modeller eklendikten sonra anlamlıdır)
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

**Önemli:** `alembic/env.py` içinde `SQLModel.metadata` kullanılıyor. Yeni tablolar için modelleri `app/models/` altında tanımlayıp `app/models/__init__.py` içinde import edin; böylece autogenerate tabloları görür.

## Testler

### Backend (pytest)

```bash
cd backend
pytest
```

### Frontend (lint)

```bash
cd frontend
npm run lint
```

## Demo veri (seed)

Bu iskelette **hazır bir seed script’i yoktur**; bilerek minimal tutulmuştur. Demo kulüp / oyuncu / maç verisi eklemek için önerilen yaklaşım:

1. SQLModel modelleri ve Alembic migration’ları tamamlayın.
2. `backend/app/jobs/` veya `backend/scripts/seed_demo.py` benzeri tek seferlik bir script yazın; `Session` ile kayıt ekleyin.
3. Üretimde seed’i yalnızca geliştirme ortamında çalıştırın (`if settings.debug` veya ayrı CLI komutu).

İleride `python -m app.scripts.seed_demo` gibi bir giriş noktası eklenebilir.

## Proje yapısı (özet)

```
pitchvision-lite/
├── README.md
├── docker-compose.yml
├── .env.example
├── backend/          # FastAPI, SQLModel, Alembic
└── frontend/         # Next.js App Router, Tailwind, Zustand, Recharts
```

## Lisans / durum

MVP iskeleti — iş mantığı ve gerçek auth henüz eklenmemiştir.
