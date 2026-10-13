# 🎬 YouTube Video Upload & Analysis Test Workflow

## ✅ System Status

- ✅ Backend API: http://localhost:8000
- ✅ Frontend: http://localhost:3000
- ✅ Auth Bypass: Enabled (development mode)
- ✅ Worker: Running
- ✅ Redis: Connected
- ✅ Database: Connected

## 🎯 Test Steps

### Step 1: Access Frontend
1. Open http://localhost:3000
2. You'll be redirected to /dashboard
3. Click "Yeni Maç Yükle" button

### Step 2: Create Match with YouTube URL
1. Fill in match details:
   - **Takım seç**: Anadolu Akademi (or any team)
   - **Rakip takım adı**: Test Opponent
   - **Maç tarihi**: Today's date
   - **Yaş kategorisi**: U15
   - **Oyun formatı**: 11v11
   - **Saha tipi**: Tam saha
   - **İlk yarı hücum yönü**: Sol → Sağ

2. Select "YouTube / URL" as video source

3. Paste YouTube URL (10-15 min match video):
   ```
   https://www.youtube.com/watch?v=...
   ```
   
   **Recommended test videos:**
   - Search for "football match highlights 10 minutes"
   - Or use any public football video

4. Click "Kaydet ve İşlemeye Gönder"

### Step 3: Monitor Processing
1. Frontend will:
   - Create match in database
   - Download video from YouTube
   - Queue analysis job
   - Redirect to processing page

2. Backend will:
   - Download video using yt-dlp
   - Save to ./uploads/
   - Queue job in Redis

3. Worker will:
   - Pick up job from Redis queue
   - Run CV pipeline (mock mode)
   - Generate segments
   - Detect moments
   - Calculate metrics
   - Generate alerts
   - Generate training suggestions

### Step 4: View Results
1. Check processing page for status
2. View generated analysis:
   - Tactical alerts
   - Performance metrics
   - Training suggestions
   - Video timeline

## 📊 Expected Output

### Backend Logs
```
INFO: Downloading video from: https://www.youtube.com/watch?v=...
INFO: Video downloaded successfully: ./uploads/video_title.mp4
INFO: Match 1: running in MOCK CV mode (100 synthetic frames)
INFO: Match 1: extracted 100 tracking frames
INFO: Match 1 analysis completed successfully
```

### Frontend Display
- Match created with status "processing"
- Video player shows downloaded video
- Timeline shows detected moments
- Alerts and metrics displayed
- Training suggestions shown

## 🔧 Troubleshooting

### Video Download Fails
- Check YouTube URL is valid
- Check internet connection
- Check yt-dlp is installed: `pip list | grep yt-dlp`
- Check ./uploads/ directory exists

### Worker Not Processing
- Check Redis is running: `redis-cli ping`
- Check worker logs: `tail -f worker.log`
- Check queue: `redis-cli LLEN analysis_queue`

### API Errors
- Check backend logs for errors
- Verify database connection
- Check CORS settings

## 📝 API Endpoints Used

### Create Match
```bash
POST /api/matches
{
  "teamId": 1,
  "opponentName": "Test Opponent",
  "matchDate": "2026-05-19",
  "ageCategory": "U15",
  "gameFormat": "11v11",
  "status": "processing",
  "durationMinutes": 90
}
```

### Upload Video from URL
```bash
POST /api/matches/{match_id}/upload-url
{
  "url": "https://www.youtube.com/watch?v=...",
  "title": "Test Opponent"
}
```

### Get Match
```bash
GET /api/matches/{match_id}
```

### Get Analysis
```bash
GET /api/segments?match_id={match_id}
GET /api/engine-events?match_id={match_id}
GET /api/ai-summary?match_id={match_id}
```

## 🎉 Success Criteria

✅ Video downloads from YouTube  
✅ Match created in database  
✅ Analysis job queued  
✅ Worker processes job  
✅ Metrics calculated  
✅ Alerts generated  
✅ Frontend displays results  
✅ AI summary generated  

## 📚 Files Modified

- `backend/app/auth.py` - Auth bypass for development
- `backend/app/api/matches.py` - YouTube URL upload endpoint
- `backend/app/cv/video_download.py` - Video download utility
- `backend/requirements.txt` - Added yt-dlp
- `frontend/.env.local` - Switched to real API mode
- `frontend/lib/api.ts` - Added YouTube upload function
- `frontend/app/(app)/matches/new/page.tsx` - YouTube URL input

## 🚀 Next Steps After Test

1. **Verify AI Summary Generation**
   - Check GLM-5.1 model is called
   - Verify reasoning output
   - Check summary quality

2. **Optimize Performance**
   - Profile CV pipeline
   - Optimize metric calculation
   - Cache results

3. **Add Real Video Processing**
   - Set CV_MOCK_MODE=false
   - Test with real YOLOv8 detection
   - Verify tracking accuracy

4. **Production Deployment**
   - Remove auth bypass
   - Implement proper JWT auth
   - Set up monitoring
   - Configure logging

---

**Ready to test!** 🎬 Go to http://localhost:3000/matches/new and try uploading a YouTube video!
