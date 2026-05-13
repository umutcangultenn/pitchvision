# PitchVision Lite

Futbol Analiz SaaS Platformu (MVP) - Amatör kulüpler ve akademiler için video tabanlı performans takibi.

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

### Kurulum ve Çalıştırma

1. **Repoyu klonlayın ve dizine girin:**
   ```bash
   cd pitchvision-lite
   ```

2. **Çevre değişkenlerini ayarlayın:**
   ```bash
   cp .env.example .env
   ```

3. **Docker ile tüm sistemi ayağa kaldırın:**
   ```bash
   docker-compose up --build
   ```

Sistem şu adreslerde çalışacaktır:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 🛠️ Teknoloji Yığını

- **Backend:** FastAPI, SQLModel, PostgreSQL, Redis, RQ, OpenCV
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, Recharts
- **DevOps:** Docker, Alembic

## 📂 Proje Yapısı

- `backend/`: Python tabanlı API ve CV motoru.
- `frontend/`: Next.js tabanlı kullanıcı arayüzü.

## 🧪 Test

Backend testlerini çalıştırmak için:
```bash
cd backend
pytest
```
