# 🚀 Getting Started with PitchVision

## Welcome! 👋

PitchVision is now fully set up and running with a production-ready frontend and comprehensive UI components. This guide will help you get started.

---

## ⚡ Quick Start (2 minutes)

### **1. Access the Application**
Open your browser and go to:
```
http://localhost:3000
```

You'll be automatically redirected to the dashboard.

### **2. View the Dashboard**
You should see:
- Team statistics (matches, players, alerts)
- Recent matches
- Top players
- Quick navigation buttons

### **3. Explore Features**
Click on any of these in the sidebar:
- **Matches** - View all matches and details
- **Players** - View player profiles
- **Drills** - See drill recommendations
- **Teams** - Manage teams
- **Reports** - View match reports
- **Scouting** - Scouting interface

---

## 🎯 Main Features

### **Dashboard** 📊
- Overview of team statistics
- Recent matches
- Top performing players
- Quick action buttons

### **Matches** 🎬
- List of all matches
- Match details with:
  - Video player
  - Tactical timeline
  - AI analysis
  - Event tagging
  - Performance metrics

### **Players** 👥
- Player profiles
- Performance metrics
- Development velocity
- Scouting notes
- Trend analysis

### **Analysis** 📈
- Tactical alerts
- Video clips
- Performance metrics
- Drill recommendations

### **Reports** 📄
- Match reports
- PDF export
- Performance summaries

---

## 🔍 Exploring the UI

### **Navigation**
- **Sidebar** (left) - Main navigation menu
- **Topbar** (top) - User menu and settings
- **Cards** - Information containers
- **Buttons** - Actions and navigation

### **Color Scheme**
- **Emerald Green** - Primary actions and highlights
- **Dark Background** - Main interface
- **Light Text** - Content
- **Subtle Borders** - Separation

### **Responsive Design**
- Works on desktop, tablet, and mobile
- Sidebar collapses on mobile
- Touch-friendly buttons
- Optimized layouts

---

## 📊 Understanding the Data

### **Demo Data Includes**
- 5 sample matches
- 15 sample players
- Tactical alerts and metrics
- Performance data
- Team statistics

### **Data Structure**
```
Team: Anadolu Akademi (U15)
├── Matches (5)
│   ├── Match 1001 - vs Opponent A
│   ├── Match 1002 - vs Opponent B
│   └── ...
├── Players (15)
│   ├── Player 1 - Position: Forward
│   ├── Player 2 - Position: Midfielder
│   └── ...
└── Metrics
    ├── Team Compactness
    ├── Transition Speed
    └── Calibration Error
```

---

## 🎮 Interactive Features

### **Video Player**
- Play/pause video
- Seek to specific time
- Click events to jump to timestamp
- Full-screen mode

### **Timeline**
- Visual representation of events
- Click to jump to event
- Color-coded by type
- Time labels

### **Event Tagging**
- Add notes to events
- Tag event types
- Save and retrieve notes
- Filter by tags

### **Comparison View**
- Compare two matches
- Side-by-side analysis
- Metric comparison
- Performance trends

---

## 🔧 Customization

### **Change Mock Data**
Edit `frontend/data/demo.ts` to modify:
- Team information
- Player data
- Match results
- Metrics and alerts

### **Modify Styling**
Edit `frontend/tailwind.config.ts` to change:
- Colors
- Fonts
- Spacing
- Breakpoints

### **Add New Pages**
1. Create file in `frontend/app/(app)/[page]/page.tsx`
2. Import components
3. Add navigation link in sidebar

---

## 🔌 Connecting to Real Backend

### **Step 1: Enable Real API**
Edit `frontend/.env.local`:
```
NEXT_PUBLIC_USE_MOCKS=false
```

### **Step 2: Create Demo User**
```bash
cd backend
python create_demo_user.py
```

### **Step 3: Login**
- Email: `demo@pitchvision.com`
- Password: `demo123`

### **Step 4: Upload Video**
- Go to Matches → New Match
- Upload video file
- Wait for processing

---

## 📱 Mobile Experience

### **Responsive Features**
- Sidebar collapses on mobile
- Touch-friendly buttons
- Optimized layouts
- Full functionality

### **Testing on Mobile**
```bash
# Get your local IP
ipconfig getifaddr en0

# Access from mobile
http://[YOUR_IP]:3000
```

---

## 🎨 UI Components

### **Available Components**
All components are in `frontend/components/`:

**Analysis**
- AlertsTab - Display tactical alerts
- MetricsTab - Show performance metrics
- NotesTab - Event notes and tagging
- VideoTimeline - Timeline of events

**Cards**
- StatCard - Display statistics
- MatchCard - Match information
- PlayerCard - Player information
- AlertCard - Alert information

**Charts**
- RadarChartCard - Radar chart visualization
- TrendChartCard - Trend analysis

**UI**
- StatusBadge - Status indicator
- Timeline - Event timeline
- Modal - Dialog boxes
- EmptyState - Empty state message
- ErrorState - Error message

---

## 🐛 Troubleshooting

### **Page Not Loading**
1. Check if backend is running: `curl http://localhost:8000/health`
2. Check browser console for errors
3. Clear cache: `rm -rf frontend/.next`
4. Restart frontend: `npm run dev`

### **Data Not Showing**
1. Verify `NEXT_PUBLIC_USE_MOCKS=true` in `.env.local`
2. Check browser console for errors
3. Verify `frontend/data/demo.ts` exists
4. Restart frontend

### **Styling Issues**
1. Clear cache: `rm -rf frontend/.next`
2. Rebuild Tailwind: `npm run dev`
3. Check `frontend/tailwind.config.ts`
4. Verify `frontend/app/globals.css`

### **API Errors**
1. Check backend is running
2. Verify API URL in `.env.local`
3. Check backend logs
4. Verify database connection

---

## 📚 Documentation

### **Quick Reference**
- `QUICK_REFERENCE.md` - Commands and shortcuts

### **Detailed Guides**
- `FRONTEND_MIGRATION_SUMMARY.md` - Migration details
- `MIGRATION_COMPLETE.md` - Completion summary
- `STATUS_REPORT.md` - Current status

### **Setup Guides**
- `LOCAL_SETUP.md` - Local development setup
- `ARCHITECTURE.md` - System architecture

---

## 🎯 Next Steps

### **For Development**
1. Explore all pages and features
2. Understand the component structure
3. Review the API client
4. Modify demo data
5. Add new components

### **For Integration**
1. Enable real API mode
2. Create demo user
3. Implement authentication
4. Connect real endpoints
5. Upload real videos

### **For Deployment**
1. Build frontend: `npm run build`
2. Configure environment
3. Deploy to hosting
4. Set up monitoring
5. Configure CI/CD

---

## 💡 Tips & Tricks

### **Development**
- Use browser DevTools for debugging
- Check React DevTools for component inspection
- Monitor network tab for API calls
- Use console for logging

### **Performance**
- Mock mode is faster for development
- Real API depends on backend
- Clear cache if experiencing issues
- Use production build for testing

### **Customization**
- All colors in `tailwind.config.ts`
- All fonts in `globals.css`
- All components in `components/`
- All pages in `app/(app)/`

---

## 🎉 You're Ready!

Everything is set up and ready to go. Start exploring PitchVision:

1. **Visit**: http://localhost:3000
2. **Explore**: Click around and discover features
3. **Customize**: Modify data and styling
4. **Integrate**: Connect to real backend
5. **Deploy**: Take it to production

---

## 📞 Need Help?

### **Check These Files**
1. `QUICK_REFERENCE.md` - Quick answers
2. `STATUS_REPORT.md` - Current status
3. Component source code - Implementation details
4. Browser console - Error messages
5. Backend logs - API issues

### **Common Issues**
- Frontend not loading → Check backend
- Data not showing → Check mock mode
- Styling broken → Clear cache
- API errors → Check backend logs

---

## 🚀 Happy Coding!

PitchVision is ready for development. Enjoy exploring and building!

---

**Version**: 1.0.0  
**Last Updated**: May 19, 2026  
**Status**: ✅ Ready to Use
