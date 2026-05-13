# PitchVision Lite - Mimari Dokümantasyon

## 🏗️ Genel Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Login   │  │Dashboard │  │ Matches  │  │ Players  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │  Teams   │  │ Matches  │  │ Analysis │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Redis     │    │    MinIO     │
│  (Database)  │    │ (Job Queue)  │    │  (Storage)   │
└──────────────┘    └──────────────┘    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │    Worker    │
                    │  (CV + AI)   │
                    └──────────────┘
```

## 📦 Modül Yapısı

### Backend Modülleri

#### 1. **Core** (`app/`)
- `main.py` - FastAPI application
- `config.py` - Configuration management
- `database.py` - Database connection
- `auth.py` - Authentication & authorization

#### 2. **Models** (`app/models/`)
- `user.py` - Kullanıcı modeli
- `team.py` - Takım modeli
- `player.py` - Oyuncu modeli
- `match.py` - Maç modeli
- `analysis.py` - Analiz modeli
- `tactical_alert.py` - Taktiksel uyarılar
- `player_metric.py` - Oyuncu metrikleri
- `training_suggestion.py` - Antrenman önerileri

#### 3. **API Routes** (`app/api/`)
- `auth.py` - Authentication endpoints
- `teams.py` - Team management
- `matches.py` - Match management
- `players.py` - Player management
- `analysis.py` - Analysis endpoints

#### 4. **Computer Vision** (`app/cv/`)
- `detector.py` - Player/ball detection (Mock + YOLO)
- `tracker.py` - Object tracking
- `calibration.py` - Pitch calibration

#### 5. **Analytics** (`app/analytics/`)
- `metrics.py` - Tactical metrics calculation
- `alerts.py` - Alert generation
- `training.py` - Training suggestions

#### 6. **Worker** (`app/worker.py`)
- Background job processing
- Video analysis pipeline
- Metric calculation

### Frontend Modülleri

#### 1. **Pages** (`src/app/`)
- `login/` - Giriş sayfası
- `dashboard/` - Ana dashboard
- `matches/` - Maç yönetimi
- `players/` - Oyuncu yönetimi
- `analysis/` - Analiz görüntüleme
- `reports/` - Raporlar
- `settings/` - Ayarlar

#### 2. **Components** (`src/components/`)
- `Layout/` - Layout components
- `Match/` - Match-related components
- `Player/` - Player components
- `Charts/` - Data visualization
- `Video/` - Video player

#### 3. **Stores** (`src/stores/`)
- `authStore.ts` - Authentication state
- `matchStore.ts` - Match state
- `playerStore.ts` - Player state

#### 4. **Services** (`src/services/`)
- `api.ts` - API client
- `auth.ts` - Auth service
- `matches.ts` - Match service

## 🔄 Veri Akışı

### 1. Maç Analizi Pipeline

```
1. Video Upload
   ↓
2. Queue Job (Redis)
   ↓
3. Worker Picks Job
   ↓
4. Detection (YOLO/Mock)
   ↓
5. Tracking (DeepSORT/Simple)
   ↓
6. Calibration (Homography)
   ↓
7. Metric Calculation
   ↓
8. Alert Generation
   ↓
9. Training Suggestions
   ↓
10. Save to Database
```

### 2. Authentication Flow

```
1. User Login (email/password)
   ↓
2. Verify Credentials
   ↓
3. Generate JWT Token
   ↓
4. Return Token + User Info
   ↓
5. Store in LocalStorage
   ↓
6. Include in API Requests
```

## 🗄️ Database Schema

### Users
- id, email, full_name, role, hashed_password
- organization, phone, is_active
- created_at, updated_at

### Teams
- id, name, age_group, season
- owner_id (FK → users)
- logo_url, colors
- created_at, updated_at

### Players
- id, jersey_number, full_name, birth_date
- team_id (FK → teams)
- position, preferred_foot, height, weight
- photo_url, notes
- created_at, updated_at

### Matches
- id, opponent_name, match_date, location
- team_id (FK → teams)
- status, scores, video_url
- calibration_data (JSON)
- created_at, updated_at

### Analyses
- id, match_id (FK → matches)
- status, tracking_data (JSON)
- possession, passes, shots
- distance_covered, heatmap_data
- processing_time
- created_at, updated_at

### Tactical Alerts
- id, match_id (FK → matches)
- category, severity, title, description
- timestamp_seconds, video_clip_url
- metadata (JSON)
- is_reviewed, coach_notes
- created_at

### Player Metrics
- id, player_id (FK → players), match_id
- minutes_played, distance_covered
- passes, shots, tackles
- heatmap_data, position_zones
- development_scores
- created_at

### Training Suggestions
- id, match_id (FK → matches)
- category, priority, title, description
- target_players, drill_suggestions
- expected_improvement, duration
- is_completed, coach_feedback
- created_at

## 🔐 Security

### Authentication
- JWT tokens (HS256)
- Password hashing (bcrypt)
- Token expiration (30 minutes)

### Authorization
- Role-based access control
- Resource ownership validation
- API endpoint protection

### Data Protection
- CORS configuration
- SQL injection prevention (SQLModel)
- Input validation (Pydantic)

## 🚀 Deployment

### Development
```bash
docker-compose up -d
```

### Production Considerations
1. Use production-grade secrets
2. Enable HTTPS
3. Configure proper CORS origins
4. Set up database backups
5. Monitor worker processes
6. Scale workers horizontally
7. Use CDN for video storage
8. Implement rate limiting

## 📊 Performance

### Optimization Strategies
1. **Database**: Connection pooling, indexes
2. **API**: Response caching, pagination
3. **Worker**: Parallel processing, batch operations
4. **Frontend**: Code splitting, lazy loading
5. **Video**: Adaptive streaming, compression

## 🧪 Testing Strategy

### Backend
- Unit tests (pytest)
- Integration tests (API endpoints)
- CV pipeline tests (mock data)

### Frontend
- Component tests (Jest + React Testing Library)
- E2E tests (Playwright)
- Visual regression tests

## 📈 Monitoring

### Metrics to Track
- API response times
- Worker job processing time
- Database query performance
- Video upload success rate
- Analysis completion rate
- User engagement metrics

### Logging
- Application logs (structured JSON)
- Error tracking (Sentry)
- Performance monitoring (APM)
