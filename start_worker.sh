#!/bin/bash

# PitchVision Worker Starter Script

echo "🔧 PitchVision Worker başlatılıyor..."

# Virtual environment'ı aktif et
source backend/venv/bin/activate

# Backend dizinine git
cd backend

# Worker'ı başlat
echo "✅ Worker başlatılıyor..."
python app/worker.py
