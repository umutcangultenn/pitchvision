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
   - **REST ön eki:** `http://localhost:8000/api/v1` (örnek: `GET /api/v1/matches`). Kök sağlık: `GET /health`, `GET /db-check`.

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

Demo organizasyon **Anadolu Akademi** ile birlikte 4 takım, 6 oyuncu, 4 maç, taktiksel alertler, klipler, raporlar ve antrenman önerileri yüklenir.

### Demo login

| Rol   | E-posta                        | Şifre       |
|-------|--------------------------------|-------------|
| Coach | `coach@anadolu-akademi.demo`   | `demo12345` |
| Scout | `scout@anadolu-akademi.demo`   | `demo12345` |

### Seed komutu

**Docker Compose ile (önerilen):**

```bash
docker compose exec backend python scripts/seed_demo.py
```

**Yerel kurulumda:**

```bash
cd backend
python scripts/seed_demo.py
```

> Seed idempotent'tir — aynı e-posta zaten varsa tekrar çalıştırmak güvenlidir.

### Demo veri özeti

| Varlık            | Adet | Detay                                                    |
|-------------------|------|----------------------------------------------------------|
| Organizasyon      | 1    | Anadolu Akademi, İstanbul                                |
| Takım             | 4    | U15 Kırmızı, U13 Akademi, U17 Gelişim, U11 Futbol Okulu |
| Oyuncu            | 6    | Arda, Emir, Kerem, Can (U15) · Efe (U13) · Mert (U17)   |
| Maç               | 4    | Mavi Spor, Kartal Akademi, Anadolu FK, Kuzey Gençlik     |
| Taktiksel alert   | 8    | Savunma hattı, blok kopukluğu, geçiş, derin koşu vb.    |
| Klip              | 4    | Alert'lere bağlı video klipler                           |
| Rapor             | 4    | Maç özeti, oyuncu gelişim, scouting, akademi özeti       |
| Antrenman önerisi | 5    | Kompakt blok, karşı pres, üçüncü adam koşusu vb.         |

## Testler

### Backend (pytest)

```bash
cd backend

# Test bağımlılıklarını yükle
pip install -r requirements-test.txt

# Tüm testler
pytest

# Sadece analytics unit testleri (DB gerektirmez)
pytest tests/test_team_shape.py tests/test_defensive_line.py \
       tests/test_transitions.py tests/test_calibration.py \
       tests/test_alerts_and_drills.py -v

# API smoke testleri
pytest tests/test_api_smoke.py -v

# Coverage raporu
pytest --cov=app --cov-report=term-missing
```

### Frontend (Jest + React Testing Library)

```bash
cd frontend

# Bağımlılıkları yükle (ilk seferinde)
npm install

# Tüm testler
npm test

# Watch modu (geliştirme sırasında)
npm run test:watch

# Coverage raporu
npm run test:coverage
```

### E2E (Playwright)

```bash
cd e2e

# Bağımlılıkları yükle
npm install
npx playwright install chromium

# Frontend'i ayrı terminalde başlat
# cd ../frontend && npm run dev

# Testleri çalıştır
npm test

# UI modu (interaktif debug)
npm run test:ui

# Headed mod (tarayıcı görünür)
npm run test:headed
```

> E2E testleri çalışan bir frontend gerektirir (varsayılan: `http://localhost:3000`).
> Mock mod için `frontend/.env.local` dosyasında `NEXT_PUBLIC_USE_MOCKS=true` olmalıdır.

## Proje yapısı (özet)

```
pitchvision-lite/
├── README.md
├── docker-compose.yml
├── .env.example
├── backend/          # FastAPI, SQLModel, Alembic
│   ├── app/
│   ├── tests/        # pytest unit + smoke testleri
│   ├── pytest.ini
│   └── requirements-test.txt
├── frontend/         # Next.js App Router, Tailwind, Zustand, Recharts
│   ├── __tests__/    # Jest + React Testing Library
│   ├── jest.config.js
│   └── jest.setup.ts
└── e2e/              # Playwright E2E testleri
    ├── playwright.config.ts
    └── tests/
```

## MVP durumu (kalite özeti)

Bu bölüm, monorepo içi kalite kontrolünün özetidir; ayrıntılı kod incelemesi için test ve `docker compose` akışını kullanın.

### Mimari

- **Monorepo:** `backend/`, `frontend/`, `e2e/` ayrımı net; kök `README` ve Compose ile hizalı.
- **API:** FastAPI router’ı `/api/v1` ön eki altında; Next.js `lib/api.ts` ve `lib/apiSettings.ts` aynı önekle çağrı yapar. Kök `GET /health` değişmedi.
- **Bileşenler:** Kartlar (`StatCard`, `MatchCard`, …) ve `EmptyState` / `ErrorState` ile tekrar azaltılmış; analiz sekmeleri modüler.

### Frontend

- **Rotalar:** App Router altında dashboard, maç akışı (`new`, `processing`, `calibration`, `analysis`, `report`), oyuncular, scouting, drills, raporlar, ayarlar vb. tanımlı.
- **Sidebar:** “Oyuncular” yalnızca liste (`/players`); “Oyuncu Pasaportları” oyuncu detayına (`/players/:id`) gider; video analiz ve maçlar için aktif durum kuralları güncellendi.
- **Akış CTA’ları:** Dashboard ve maç raporu `Antrenman planına ekle` → `/drills`; oyuncu pasaportunda `Scouting panosu` → `/scouting`.
- **Durumlar:** Dashboard ve API kullanan sayfalarda yükleme / hata / boş durumları kullanılıyor; demo veri ile dolduruluyor.
- **Marka / dil:** Arayüz metinleri Türkçe; “PitchVision Lite” kullanımı tutarlı; “Tactical Performance System” vb. eski ürün adı aranmıyor.

### Backend

- **FastAPI:** `app.main:app`; `GET /health` kökte.
- **Veri:** SQLModel + Alembic; başlangıçta `create_all` ve idempotent `seed_demo_data`.
- **Analytics:** `app/analytics/*` (takım şekli, savunma hattı, geçiş, uyarı, drill eşlemesi) ve `app/cv/calibration.PitchCalibrator` (NumPy ile homografi; OpenCV olmadan test edilebilir) eklendi; `pytest tests/test_*.py` (analytics + smoke) ile doğrulanır.
- **Video işleme:** `start_match_processing` maç durumunu günceller; gerçek YOLO/ByteTrack pipeline’ı MVP dışı — arayüzde işlem adımları demo açıklamasıyla işaretlenir.

### Ürün akışı (hedeflenen MVP yolculuğu)

1. **Dashboard** → yeni maç veya son maçlar.  
2. **Yükleme / işleme / kalibrasyon** → video analiz ekranı.  
3. **Rapor** → taktik uyarılar ve antrenman önerisi eşlemesi (rapor sayfasında drill kartları; CTA ile `/drills`).  
4. **Oyuncu pasaportu** → gelişim odaklı metinler; scouting sekmesi ve panoya bağlantı.

### Bilinen sınırlamalar

- **Auth:** `get_current_user` demo için token yoksa ilk kullanıcıya düşer; üretim için sıkılaştırılmalı.
- **Smoke testler:** PostgreSQL erişilemezse bazı uçlar 500 dönebilir; testler bu durumu tolere eder (`tests/test_api_smoke.py`).
- **Windows / Python 3.13:** `psycopg2-binary` kurulumu ortam bağımlıdır; tam kurulum için Docker veya Python 3.11 önerilir.

## Lisans / durum

MVP iskeleti — iş mantığı ve gerçek auth henüz eklenmemiştir.
