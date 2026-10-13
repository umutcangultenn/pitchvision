# PitchVision Usage Guide

## 🚀 Quick Start

### 1. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 2. Create a New Match

#### Option A: Upload from YouTube
1. Go to http://localhost:3000/matches
2. Click "Yeni Maç Yükle" (New Match Upload)
3. Fill in the form:
   - **Opponent**: Name of the opposing team
   - **Match Date**: Date of the match
   - **Location**: Stadium or location name
   - **Video URL**: YouTube URL (e.g., https://www.youtube.com/watch?v=...)
4. Click "Yükle" (Upload)
5. The system will:
   - Download the video from YouTube
   - Create a match record
   - Queue the analysis job
   - Start processing

#### Option B: Upload from File
1. Go to http://localhost:3000/matches
2. Click "Yeni Maç Yükle"
3. Fill in the form and select a video file
4. Click "Yükle"

### 3. Monitor Analysis Progress

1. Go to http://localhost:3000/matches
2. Look for your newly created match
3. Status will show:
   - **Kalibrasyon bekliyor** (Waiting for calibration) - Initial state
   - **İşleniyor** (Processing) - Video is being analyzed
   - **Analiz tamamlandı** (Analysis complete) - Ready to view

### 4. View Analysis Results

1. Find your match in the matches list
2. Click "Analizi Aç" (Open Analysis) to view:
   - Video player with analysis overlay
   - Tactical metrics (possession, passes, shots)
   - Tactical alerts
   - Detected moments
   - Player tracking data

3. Click "Raporu Gör" (View Report) to see:
   - Match summary
   - Tactical alerts with details
   - Training suggestions
   - Drill recommendations

## 📊 Understanding the Data

### Match Status
- **Kalibrasyon bekliyor**: Match created, waiting for video processing
- **İşleniyor**: Video is being analyzed by YOLO and tactical engine
- **Analiz tamamlandı**: Analysis complete, results available
- **Hata**: Processing failed, check logs

### Analysis Metrics
- **Possession**: Ball possession percentage (home vs away)
- **Passes**: Completed passes (home vs away)
- **Shots**: Shots on goal (home vs away)
- **Takım boyu**: Team length in meters (defensive organization)
- **Kompaktlık**: Team compactness in meters (defensive cohesion)

### Tactical Alerts
Alerts are generated based on tactical patterns detected:
- **Savunma** (Defense): Defensive line issues, gaps, positioning
- **Hücum** (Offense): Attacking patterns, opportunities
- **Top Hakimiyeti** (Possession): Possession-related patterns
- **Geçiş Oyunu** (Transition): Transition play patterns
- **Duran Top** (Set Piece): Set piece patterns
- **Fiziksel** (Physical): Physical intensity patterns

### Training Suggestions
Suggestions are generated based on detected weaknesses:
- Specific drill recommendations
- Duration and focus areas
- Based on tactical alerts from the match

## 🔍 Filtering Matches

On the matches page, you can filter by:
- **Team**: Select which team to view
- **Age Category**: Filter by age group (U15, U13, etc.)
- **Status**: Filter by analysis status
- **Video Source**: Filter by upload method (YouTube, File, etc.)
- **Opponent**: Search by opponent name
- **Alert Count**: Filter by minimum number of alerts
- **Date Range**: Filter by match date

## 🎯 Workflow Examples

### Example 1: Analyze a YouTube Highlight Video
```
1. Go to /matches
2. Click "Yeni Maç Yükle"
3. Enter:
   - Opponent: "Fenerbahçe"
   - Date: "2026-05-19"
   - Location: "Ülker Stadyumu"
   - Video URL: "https://www.youtube.com/watch?v=..."
4. Click "Yükle"
5. Wait for processing (usually 4-5 seconds)
6. Refresh the page to see the completed analysis
7. Click "Analizi Aç" to view detailed results
```

### Example 2: Compare Multiple Matches
```
1. Upload multiple matches (as above)
2. Go to /matches
3. Use filters to view matches by:
   - Same opponent
   - Same date range
   - Same age category
4. Compare metrics and alerts across matches
```

### Example 3: Generate Training Plan
```
1. View a completed match analysis
2. Click "Raporu Gör" (View Report)
3. Review the tactical alerts
4. Check the training suggestions
5. Use the drill recommendations to create a training session
```

## 🔧 System Configuration

### Change Demo Team
To change the demo team, edit `backend/setup_demo_data.py`:
```python
# Change this line:
team = Team(id=3, name="Anadolu Akademi", age_group="U15")
# To:
team = Team(id=3, name="Your Team Name", age_group="U17")
```

Then run:
```bash
cd backend
python setup_demo_data.py
```

### Enable/Disable Mock Mode
To use mock CV detection instead of real YOLO:
```python
# In backend/app/config.py:
CV_MOCK_MODE: bool = True  # Set to True for mock mode
```

### Change API URL
To change the backend API URL:
```bash
# In frontend/.env.local:
NEXT_PUBLIC_API_URL=http://your-backend-url:8000
```

## 📱 API Usage

### Get All Matches
```bash
curl http://localhost:8000/api/matches
```

### Create a Match
```bash
curl -X POST http://localhost:8000/api/matches \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": 3,
    "opponent_name": "Fenerbahçe",
    "match_date": "2026-05-19T15:00:00",
    "location": "Ülker Stadyumu",
    "duration_minutes": 90
  }'
```

### Upload Video from URL
```bash
curl -X POST http://localhost:8000/api/matches/16/upload-url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=...",
    "title": "Match Highlights"
  }'
```

### Get Analysis Results
```bash
curl http://localhost:8000/api/analysis/16
```

### Get Tactical Alerts
```bash
curl http://localhost:8000/api/analysis/16/alerts
```

### Get Training Suggestions
```bash
curl http://localhost:8000/api/analysis/16/training
```

## 🐛 Troubleshooting

### Issue: "Video download failed"
**Solution**: 
- Check if the YouTube URL is valid and public
- Ensure `yt-dlp` is installed: `pip install yt-dlp`
- Check internet connection

### Issue: "Analysis not found"
**Solution**:
- Wait for the worker to process the video (check worker logs)
- Refresh the page
- Check if the match status is "completed"

### Issue: "No alerts generated"
**Solution**:
- This is normal for some videos
- Alerts are only generated if tactical patterns are detected
- Check the analysis metrics to see if data was processed

### Issue: "Worker not processing jobs"
**Solution**:
- Check if worker is running: `ps aux | grep worker`
- Check Redis connection: `redis-cli ping`
- Check worker logs for errors
- Restart worker: `python -m app.worker`

### Issue: "Frontend not loading"
**Solution**:
- Check if frontend is running: `npm run dev`
- Check if backend API is accessible: `curl http://localhost:8000/health`
- Clear browser cache and refresh
- Check browser console for errors

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **System Status**: See `SYSTEM_STATUS.md`
- **Verification Report**: See `VERIFICATION_REPORT.md`
- **Architecture**: See `ARCHITECTURE.md`

## 🎓 Learning Resources

### Understanding Tactical Metrics
- **Possession**: Higher possession doesn't always mean better performance
- **Compactness**: Lower compactness (more spread out) can indicate defensive issues
- **Passes**: More passes doesn't always mean better play quality
- **Shots**: Quality of shots matters more than quantity

### Understanding Alerts
- **Critical**: Immediate tactical issues that need attention
- **Warning**: Patterns that should be monitored
- **Info**: Informational patterns for reference

### Understanding Training Suggestions
- Suggestions are based on detected weaknesses
- Each suggestion includes specific drill recommendations
- Drills are designed to address the identified issues
- Duration and focus areas are provided for each drill

## 🚀 Next Steps

1. **Upload your first video**: Try uploading a YouTube highlight video
2. **Explore the analysis**: View the detailed analysis results
3. **Review alerts**: Check the tactical alerts generated
4. **Plan training**: Use the training suggestions to create a training session
5. **Compare matches**: Upload multiple matches and compare results

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the system logs
3. Check the API documentation at http://localhost:8000/docs
4. Review the verification report for system status
