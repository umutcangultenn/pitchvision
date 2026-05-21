# PitchVision System - Test Plan

## Overview
This document outlines the testing procedures for the fixed file upload and report generation features.

---

## TEST 1: File Upload Flow

### Prerequisites
- Backend API running on port 8000
- Frontend running on port 3000
- Redis queue running
- Worker process running
- PostgreSQL database running

### Test Steps

1. **Navigate to New Match Page**
   - Go to http://localhost:3000/matches/new
   - Verify page loads without errors
   - Verify form fields are visible

2. **Fill Match Information**
   - Enter opponent name: "Test Opponent"
   - Select match date: Today's date
   - Keep other fields as default
   - Verify all fields are filled

3. **Test File Selection Button**
   - Click "Dosya Seç" button
   - File dialog should open
   - Select a video file (MP4 or MOV)
   - Verify file name appears in the component

4. **Verify Upload Progress**
   - After file selection, progress bar should appear
   - Progress should increment from 0 to 100%
   - Toast notification should show "Yükleniyor: [filename]"

5. **Verify Upload Completion**
   - Progress bar should reach 100%
   - Toast notification should show "Video yüklendi, analiz başlatıldı"
   - Page should redirect to processing page after 1.5 seconds

6. **Verify Backend Processing**
   - Check backend logs for:
     - Match creation confirmation
     - Video file saved to uploads directory
     - Analysis job queued in Redis
   - Verify match appears in database

### Expected Results
- ✅ File upload completes successfully
- ✅ Progress bar displays correctly
- ✅ Toast notifications appear
- ✅ Redirect to processing page occurs
- ✅ Backend logs show all steps completed
- ✅ Video file saved to `./uploads/` directory
- ✅ Analysis job queued in Redis

### Failure Scenarios

**Scenario 1: Invalid File Type**
- Select a non-video file (e.g., .txt)
- Expected: Error toast "Video yükleme başarısız"
- Backend should reject the file

**Scenario 2: Network Error**
- Simulate network error (e.g., disconnect backend)
- Expected: Error toast with network error message
- Progress bar should reset to 0

**Scenario 3: Large File**
- Select a large video file (>500MB)
- Expected: Upload should still work (may take longer)
- Progress bar should show realistic progress

---

## TEST 2: Report Generation

### Prerequisites
- Analysis job completed successfully
- Worker process running
- NVIDIA API key configured

### Test Steps

1. **Wait for Analysis Completion**
   - Upload a video and wait for analysis to complete
   - Check backend logs for all 9 steps
   - Verify Step 9 (Report Generation) appears in logs

2. **Check Report Generation Logs**
   - Look for: "Generating report with NVIDIA AI"
   - Look for: "Report generated successfully" or timeout message
   - Verify timeout is 30 seconds (not 120)

3. **Navigate to Report Page**
   - Go to match report page
   - Verify page loads without errors

4. **Verify Report Content**
   - If NVIDIA API succeeded:
     - Report should show AI-generated content
     - Should include: Summary, Findings, Recommendations, Focus Areas
   - If NVIDIA API timed out:
     - Report should show mock content generated from analysis
     - Should still include all sections

5. **Verify Report Sections**
   - Match Summary: Should describe the match
   - Key Findings: Should list 3+ findings
   - Tactical Recommendations: Should list 3+ recommendations
   - Next Match Focus: Should list 3+ focus areas

### Expected Results
- ✅ Report page loads successfully
- ✅ Report content displays correctly
- ✅ All sections are populated
- ✅ No errors in browser console
- ✅ Backend logs show report generation attempt

### Failure Scenarios

**Scenario 1: NVIDIA API Timeout**
- Expected: Timeout logged after 30 seconds
- Expected: Analysis still completes successfully
- Expected: Mock report displayed to user
- Expected: No worker process hang

**Scenario 2: NVIDIA API Connection Error**
- Expected: Connection error logged
- Expected: Analysis still completes successfully
- Expected: Mock report displayed to user

**Scenario 3: Invalid NVIDIA API Key**
- Expected: 401 error logged
- Expected: Analysis still completes successfully
- Expected: Mock report displayed to user

---

## TEST 3: YouTube URL Upload

### Prerequisites
- Backend API running
- Frontend running
- yt-dlp installed

### Test Steps

1. **Navigate to New Match Page**
   - Go to http://localhost:3000/matches/new
   - Select "YouTube / URL" as video source

2. **Enter YouTube URL**
   - Paste a valid YouTube URL
   - Example: https://www.youtube.com/watch?v=...

3. **Submit Form**
   - Click "Kaydet ve İşlemeye Gönder"
   - Verify toast notification appears

4. **Verify Backend Processing**
   - Check backend logs for:
     - Video download started
     - Video saved to uploads directory
     - Analysis job queued

5. **Verify Processing Page**
   - Should redirect to processing page
   - Should show analysis progress

### Expected Results
- ✅ YouTube video downloads successfully
- ✅ Video saved to uploads directory
- ✅ Analysis job queued
- ✅ Processing page displays

---

## TEST 4: Error Handling

### Test Cases

1. **Missing Required Fields**
   - Leave opponent name empty
   - Try to submit
   - Expected: Form validation error or API error

2. **Invalid Date**
   - Enter invalid date
   - Expected: Date picker prevents invalid dates

3. **Backend Unavailable**
   - Stop backend API
   - Try to upload file
   - Expected: Error toast "Maç oluşturulamadı"

4. **Redis Queue Unavailable**
   - Stop Redis
   - Upload file
   - Expected: Backend error when queuing job

5. **Database Unavailable**
   - Stop PostgreSQL
   - Try to upload file
   - Expected: Database connection error

---

## TEST 5: Performance

### Test Cases

1. **File Upload Speed**
   - Upload 100MB video file
   - Measure upload time
   - Expected: Reasonable upload speed (depends on network)

2. **Report Generation Speed**
   - Measure time from analysis completion to report display
   - Expected: < 30 seconds (NVIDIA API timeout)

3. **Worker Processing Speed**
   - Measure time from job queued to analysis complete
   - Expected: ~4-5 seconds for 500 frames

4. **Memory Usage**
   - Monitor memory during video processing
   - Expected: No memory leaks
   - Expected: Memory released after processing

---

## TEST 6: Integration Tests

### Test Case 1: Full Workflow
1. Create new match
2. Upload video file
3. Wait for analysis
4. View analysis results
5. View report
6. Expected: All steps complete successfully

### Test Case 2: Multiple Uploads
1. Upload first video
2. While processing, upload second video
3. Expected: Both jobs process correctly
4. Expected: No interference between jobs

### Test Case 3: Concurrent Requests
1. Upload multiple videos simultaneously
2. Expected: All uploads complete
3. Expected: All analyses complete
4. Expected: No data corruption

---

## Monitoring and Logging

### Backend Logs to Monitor
```
Match {id}: ▶ Starting analysis pipeline
Match {id}: [1/8] Generating segments...
Match {id}: [2/8] Running CV pipeline...
Match {id}: [3/8] Detecting tactical moments...
Match {id}: [4/8] Updating segment metrics...
Match {id}: [5/8] Calculating metrics...
Match {id}: [6/8] Persisting analysis...
Match {id}: [7/8] Generating tactical alerts...
Match {id}: [8/8] Generating training suggestions...
Match {id}: [9/9] Queuing AI report generation...
Match {id}: ✅ Analysis completed successfully!
```

### Frontend Console to Monitor
- No errors in browser console
- Network requests complete successfully
- API responses contain expected data

### Database to Monitor
- Match record created
- Analysis record created
- Report record created (if successful)
- Alerts and suggestions created

---

## Rollback Procedure

If critical issues are found:

```bash
# Revert all changes
git checkout backend/app/worker.py
git checkout backend/app/engine/report_generator.py
git checkout frontend/app/(app)/matches/new/page.tsx

# Restart services
docker-compose restart
```

---

## Sign-Off Checklist

- [ ] File upload works correctly
- [ ] Progress bar displays
- [ ] Report generation completes
- [ ] Error handling works
- [ ] No memory leaks
- [ ] No database corruption
- [ ] All logs are clean
- [ ] Performance is acceptable
- [ ] Integration tests pass
- [ ] Ready for production

---

## Notes

- NVIDIA API timeout is set to 30 seconds (reduced from 120)
- Report generation is non-blocking (won't fail analysis if it times out)
- Mock reports are generated if NVIDIA API fails
- All errors are logged for debugging
- Worker process won't hang on API timeouts

