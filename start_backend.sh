#!/bin/bash

# PitchVision Backend Starter Script

echo "🚀 PitchVision Backend başlatılıyor..."

# Virtual environment'ı aktif et
source backend/venv/bin/activate

# Backend dizinine git
cd backend

# Uvicorn ile FastAPI'yi başlat
echo "✅ FastAPI server başlatılıyor: http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
