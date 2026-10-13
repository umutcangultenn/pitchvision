# PitchVision - Quick Reference Guide

## 🚀 Running the Application

### **Start Backend** (if not already running)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Start Frontend** (if not already running)
```bash
cd frontend
npm run dev
```

## 🌐 Access Points

| Service | URL | Status |
|---------|-----|--------|
| Frontend | http://localhost:3000 | ✅ Running |
| Backend API | http://localhost:8000 | ✅ Running |
| Dashboard | http://localhost:3000/dashboard | ✅ Ready |
| Matches | http://localhost:3000/matches | ✅ Ready |
| Players | http://localhost:3000/players | ✅ Ready |

## 📊 Current Configuration

### **Frontend Mode**
- **Mock Data**: Enabled (`NEXT_PUBLIC_USE_MOCKS=true`)
- **API URL**: `http://localhost:8000`
- **Port**: `3000`

### **Backend Mode**
- **AI Model**: GLM-5.1 (NVIDIA NIM API)
- **Database**: PostgreSQL (pitchvision_lite)
- **Cache**: Redis
- **Port**: `8000`

## 🎯 Key Features Available

### **Dashboard**
- Team statistics and metrics
- Recent matches overview
- Top players ranking
- Quick navigation to all features

### **Matches**
- Match list with status
- Match detail page with:
  - Video player
  - Tactical timeline
  - AI analysis
  - Event tagging
  - Comparison view

### **Players**
- Player profiles
- Performance metrics
- Development velocity tracking
- Scouting notes

### **Analysis**
- Tactical alerts
- Video clips
- Performance metrics
- Drill recommendations

## 🔧 Configuration Files

### **Frontend**
- `.env.local` - Environment variables
- `tailwind.config.ts` - Tailwind CSS configuration
- `next.config.js` - Next.js configuration

### **Backend**
- `.env` - Backend environment variables
- `backend/app/config.py` - Python configuration
- `backend/requirements.txt` - Python dependencies

## 📝 Common Tasks

### **Enable Real API Integration**
1. Set `NEXT_PUBLIC_USE_MOCKS=false` in `frontend/.env.local`
2. Create demo user: `python backend/create_demo_user.py`
3. Implement login flow

### **Add New API Endpoint**
1. Create route in `backend/app/api/`
2. Add function in `frontend/lib/api.ts`
3. Create hook in `frontend/hooks/`
4. Use hook in component

### **Add New Page**
1. Create file in `frontend/app/(app)/[page]/page.tsx`
2. Import components from `frontend/components/`
3. Use hooks for data fetching
4. Add navigation link in `frontend/components/layout/Sidebar.tsx`

## 🐛 Troubleshooting

### **Frontend not loading**
- Check if backend is running: `curl http://localhost:8000/health`
- Check frontend logs: `npm run dev` output
- Clear cache: `rm -rf frontend/.next`

### **API endpoints returning 404**
- Verify backend is running
- Check API URL in `.env.local`
- Verify endpoint path matches backend routes

### **Mock data not showing**
- Ensure `NEXT_PUBLIC_USE_MOCKS=true` in `.env.local`
- Check browser console for errors
- Verify `frontend/data/demo.ts` exists

## 📚 Documentation

- **Architecture**: See `ARCHITECTURE.md`
- **Implementation Status**: See `IMPLEMENTATION_STATUS.md`
- **Local Setup**: See `LOCAL_SETUP.md`
- **Frontend Migration**: See `FRONTEND_MIGRATION_SUMMARY.md`

## 🔐 Demo Credentials

### **Frontend (Mock)**
- Email: `coach@anadolu-akademi.demo`
- Password: `demo12345`
- Or click "Doğrudan panele git" to skip login

### **Backend (When Real Auth Enabled)**
- Email: `demo@pitchvision.com`
- Password: `demo123`

## 💡 Tips

1. **Use Mock Mode for Development**: Faster iteration without backend setup
2. **Check Browser Console**: For API errors and debugging
3. **Use React DevTools**: For component inspection
4. **Monitor Backend Logs**: For API issues
5. **Keep .env.local Updated**: When switching between mock/real API

## 🎨 UI Components

All components are in `frontend/components/`:
- **Analysis**: Video analysis components
- **Cards**: Reusable card components
- **Charts**: Data visualization
- **Layout**: Navigation and layout
- **Media**: Video player
- **Pitch**: Pitch visualization
- **UI**: Basic UI components

## 📞 Support

For issues or questions:
1. Check the documentation files
2. Review the component source code
3. Check browser console for errors
4. Review backend logs for API issues
