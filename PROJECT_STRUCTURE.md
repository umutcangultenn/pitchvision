# PitchVision Lite - Proje Yapısı

```
pitchvision-lite/
│
├── README.md                      # Ana dokümantasyon
├── ARCHITECTURE.md                # Mimari detayları
├── QUICKSTART.md                  # Hızlı başlangıç kılavuzu
├── PROJECT_STRUCTURE.md           # Bu dosya
├── .env.example                   # Environment değişkenleri şablonu
├── .gitignore                     # Git ignore kuralları
├── docker-compose.yml             # Docker orchestration
│
├── backend/                       # FastAPI Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini               # Database migration config
│   ├── uploads/                  # Video upload directory
│   ├── models/                   # ML model directory
│   │
│   └── app/
│       ├── __init__.py
│       ├── main.py               # FastAPI application
│       ├── config.py             # Configuration
│       ├── database.py           # Database setup
│       ├── auth.py               # Authentication
│       ├── worker.py             # Background worker
│       │
│       ├── models/               # SQLModel schemas
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── team.py
│       │   ├── player.py
│       │   ├── match.py
│       │   ├── analysis.py
│       │   ├── tactical_alert.py
│       │   ├── player_metric.py
│       │   └── training_suggestion.py
│       │
│       ├── api/                  # API Routes
│       │   ├── __init__.py
│       │   ├── auth.py           # Auth endpoints
│       │   ├── teams.py          # Team management
│       │   ├── matches.py        # Match management
│       │   ├── players.py        # Player management (TODO)
│       │   └── analysis.py       # Analysis endpoints (TODO)
│       │
│       ├── cv/                   # Computer Vision
│       │   ├── __init__.py
│       │   ├── detector.py       # Player/ball detection
│       │   ├── tracker.py        # Object tracking
│       │   └── calibration.py   # Pitch calibration
│       │
│       └── analytics/            # Analytics Engine
│           ├── __init__.py
│           ├── metrics.py        # Tactical metrics
│           ├── alerts.py         # Alert generation
│           └── training.py       # Training suggestions
│
├── frontend/                     # Next.js Frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .eslintrc.json
│   │
│   └── src/
│       ├── app/                  # Next.js App Router
│       │   ├── layout.tsx        # Root layout
│       │   ├── page.tsx          # Home page (redirect)
│       │   ├── globals.css       # Global styles
│       │   │
│       │   ├── login/            # Login page
│       │   │   └── page.tsx
│       │   │
│       │   ├── dashboard/        # Dashboard
│       │   │   └── page.tsx
│       │   │
│       │   ├── matches/          # Match management (TODO)
│       │   │   ├── page.tsx      # Match list
│       │   │   ├── new/          # New match
│       │   │   └── [id]/         # Match detail
│       │   │
│       │   ├── players/          # Player management (TODO)
│       │   │   ├── page.tsx
│       │   │   └── [id]/
│       │   │
│       │   ├── analysis/         # Analysis viewer (TODO)
│       │   │   └── [id]/
│       │   │
│       │   ├── reports/          # Reports (TODO)
│       │   │   └── [id]/
│       │   │
│       │   └── settings/         # Settings (TODO)
│       │       └── page.tsx
│       │
│       ├── components/           # React Components (TODO)
│       │   ├── Layout/
│       │   │   ├── Header.tsx
│       │   │   ├── Sidebar.tsx
│       │   │   └── Footer.tsx
│       │   │
│       │   ├── Match/
│       │   │   ├── MatchCard.tsx
│       │   │   ├── MatchList.tsx
│       │   │   └── MatchForm.tsx
│       │   │
│       │   ├── Player/
│       │   │   ├── PlayerCard.tsx
│       │   │   ├── PlayerList.tsx
│       │   │   └── PlayerPassport.tsx
│       │   │
│       │   ├── Analysis/
│       │   │   ├── VideoPlayer.tsx
│       │   │   ├── PitchView.tsx
│       │   │   ├── Heatmap.tsx
│       │   │   └── Timeline.tsx
│       │   │
│       │   ├── Charts/
│       │   │   ├── PossessionChart.tsx
│       │   │   ├── PassingChart.tsx
│       │   │   └── DistanceChart.tsx
│       │   │
│       │   └── Common/
│       │       ├── Button.tsx
│       │       ├── Card.tsx
│       │       ├── Modal.tsx
│       │       └── Loading.tsx
│       │
│       ├── stores/               # Zustand Stores (TODO)
│       │   ├── authStore.ts
│       │   ├── matchStore.ts
│       │   └── playerStore.ts
│       │
│       ├── services/             # API Services (TODO)
│       │   ├── api.ts            # Base API client
│       │   ├── auth.ts
│       │   ├── matches.ts
│       │   ├── players.ts
│       │   └── analysis.ts
│       │
│       ├── types/                # TypeScript Types (TODO)
│       │   ├── user.ts
│       │   ├── team.ts
│       │   ├── match.ts
│       │   └── analysis.ts
│       │
│       └── utils/                # Utility Functions (TODO)
│           ├── format.ts
│           ├── validation.ts
│           └── constants.ts
│
└── docs/                         # Additional Documentation (TODO)
    ├── api.md                    # API documentation
    ├── cv-pipeline.md            # CV pipeline details
    ├── deployment.md             # Deployment guide
    └── contributing.md           # Contribution guide
```

## 📊 Dosya İstatistikleri

### Tamamlanan Dosyalar ✅
- Backend Core: 100%
- Database Models: 100%
- CV Pipeline: 100% (Mock mode)
- Analytics Engine: 100%
- API Routes: 60% (Auth, Teams, Matches)
- Worker: 100%
- Frontend Core: 40% (Login, Dashboard)
- Docker Setup: 100%
- Documentation: 80%

### Geliştirilmesi Gerekenler 🚧

#### Backend (Öncelik: Orta)
- [ ] `app/api/players.py` - Oyuncu CRUD endpoints
- [ ] `app/api/analysis.py` - Analiz endpoints
- [ ] `app/api/reports.py` - Rapor endpoints
- [ ] `alembic/versions/` - Database migrations
- [ ] Video upload handling (MinIO integration)
- [ ] WebSocket for real-time updates
- [ ] PDF report generation

#### Frontend (Öncelik: Yüksek)
- [ ] `src/app/matches/` - Maç sayfaları
- [ ] `src/app/players/` - Oyuncu sayfaları
- [ ] `src/app/analysis/` - Analiz görüntüleme
- [ ] `src/app/reports/` - Rapor sayfaları
- [ ] `src/components/` - Tüm UI bileşenleri
- [ ] `src/stores/` - State management
- [ ] `src/services/` - API client services
- [ ] Video player component
- [ ] Pitch calibration canvas
- [ ] Heatmap visualization
- [ ] Chart components (Recharts)

#### Stitch Entegrasyonu (Öncelik: Yüksek)
- [ ] Stitch HTML/CSS'lerini analiz et
- [ ] Tailwind ile component'leri yeniden oluştur
- [ ] Responsive design uyarlaması
- [ ] Color scheme ve typography
- [ ] Icon set entegrasyonu

#### CV Pipeline (Öncelik: Düşük)
- [ ] Real YOLO model integration
- [ ] DeepSORT tracker
- [ ] Homography calibration
- [ ] Video preprocessing
- [ ] Frame extraction optimization

#### Testing (Öncelik: Orta)
- [ ] Backend unit tests
- [ ] API integration tests
- [ ] Frontend component tests
- [ ] E2E tests
- [ ] CV pipeline tests

## 🎯 Geliştirme Öncelikleri

### Sprint 1: Core UI (1-2 hafta)
1. Stitch tasarımlarını analiz et
2. Component library oluştur
3. Maç listesi ve detay sayfaları
4. Oyuncu listesi ve pasaport
5. Basic video player

### Sprint 2: Analysis Features (1-2 hafta)
1. Analiz görüntüleme ekranı
2. Taktiksel metrik charts
3. Heatmap visualization
4. Alert listesi ve detayları
5. Training suggestions UI

### Sprint 3: Advanced Features (2-3 hafta)
1. Saha kalibrasyonu canvas
2. Video timeline ve clip generation
3. Scouting modülü
4. PDF rapor oluşturma
5. Real-time updates (WebSocket)

### Sprint 4: Polish & Production (1-2 hafta)
1. Performance optimization
2. Error handling
3. Loading states
4. Empty states
5. Mobile responsive
6. Testing
7. Documentation

## 📝 Notlar

- **Mock Mode**: Şu anda CV pipeline mock mode'da çalışıyor
- **Database**: SQLModel ile otomatik tablo oluşturma aktif
- **Authentication**: JWT token based auth hazır
- **Worker**: Redis queue ile background job processing hazır
- **Docker**: Tüm servisler containerize edilmiş

## 🔗 İlgili Dosyalar

- Mimari detaylar: `ARCHITECTURE.md`
- Hızlı başlangıç: `QUICKSTART.md`
- Ana README: `README.md`
- Environment config: `.env.example`
