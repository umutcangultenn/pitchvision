"""
Background worker for match analysis processing.
Listens to Redis queue and processes match analysis jobs.
"""
import redis
import time
import logging
import asyncio
from sqlmodel import Session, create_engine

from app.config import settings
from app.cv.detector import get_detector
from app.cv.tracker import SimpleTracker
from app.analytics.metrics import TacticalMetricsCalculator
from app.analytics.alerts import TacticalAlertGenerator
from app.analytics.training import TrainingSuggestionGenerator
from app.models.match import Match, MatchStatus
from app.models.analysis import Analysis, AnalysisStatus
from app.models.tactical_alert import TacticalAlert
from app.models.training_suggestion import TrainingSuggestion
from app.engine.segmentation import generate_segments_for_match, update_segment_metrics
from app.engine.moment_detection import run_moment_detection

logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.REDIS_URL)
engine = create_engine(settings.DATABASE_URL)


def _run_cv_pipeline(match_id: int, video_path: str | None) -> list:
    """
    Run the CV pipeline on a video file or fall back to mock mode.

    In CV_MOCK_MODE (or when no video path is provided), generates
    synthetic tracking frames using the MockDetector.
    In production mode, processes the actual video with OpenCV + YOLO.

    Returns a list of tracking frame dicts.
    """
    detector = get_detector()
    tracker = SimpleTracker()
    tracking_data = []

    if settings.CV_MOCK_MODE or not video_path:
        logger.info(f"Match {match_id}: running in MOCK CV mode (100 synthetic frames).")
        for i in range(100):
            detections = detector.detect_frame(None, i)
            tracked = tracker.update(detections)
            tracking_data.append(tracked)
        return tracking_data

    # --- Production: real video processing ---
    try:
        import cv2
    except ImportError:
        logger.error("OpenCV not available — falling back to mock mode.")
        for i in range(100):
            detections = detector.detect_frame(None, i)
            tracked = tracker.update(detections)
            tracking_data.append(tracked)
        return tracking_data

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path} — falling back to mock mode.")
        cap.release()
        for i in range(100):
            detections = detector.detect_frame(None, i)
            tracked = tracker.update(detections)
            tracking_data.append(tracked)
        return tracking_data

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_idx = 0
    sample_every = max(1, int(fps))  # Sample 1 frame per second

    logger.info(f"Match {match_id}: processing video at {fps:.1f} FPS, sampling every {sample_every} frames.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_every == 0:
            detections = detector.detect_frame(frame, frame_idx)
            tracked = tracker.update(detections)
            tracking_data.append(tracked)

        frame_idx += 1

    cap.release()
    logger.info(f"Match {match_id}: extracted {len(tracking_data)} tracking frames from {frame_idx} total frames.")
    return tracking_data


def process_match_analysis(match_id: int) -> None:
    """
    Full analysis pipeline for a single match.
    Orchestrates segmentation, CV tracking, moment detection,
    metric calculation, alert generation, and training suggestions.
    """
    with Session(engine) as session:
        match = session.get(Match, match_id)
        if not match:
            logger.error(f"Match {match_id} not found — skipping.")
            return

        analysis = Analysis(match_id=match_id, status=AnalysisStatus.DETECTING)
        session.add(analysis)
        match.status = MatchStatus.ANALYZING
        session.commit()

        try:
            # Step 1: Generate time-based segments
            segments = generate_segments_for_match(
                session=session,
                match_id=match_id,
                duration_minutes=match.duration_minutes,
            )

            # Step 2: Run CV pipeline (mock or real)
            tracking_data = _run_cv_pipeline(match_id, match.video_url)

            # Step 3: Detect tactical moments
            engine_events = run_moment_detection(
                tracking_frames=tracking_data,
                match_id=match_id,
                segments=segments,
                session=session,
            )

            # Step 4: Update per-segment metrics
            if engine_events:
                for segment in segments:
                    seg_events = [
                        e.model_dump() for e in engine_events
                        if e.segment_id == segment.id
                    ]
                    if seg_events:
                        update_segment_metrics(session, segment, seg_events)

            # Step 5: Calculate aggregate metrics
            calculator = TacticalMetricsCalculator(tracking_data)
            metrics = calculator.get_all_metrics()

            # Step 6: Persist analysis results
            analysis.status = AnalysisStatus.COMPLETED
            analysis.possession_home = metrics["possession"]["home"]
            analysis.possession_away = metrics["possession"]["away"]
            analysis.passes_completed_home = metrics["passes"]["home_completed"]
            analysis.passes_completed_away = metrics["passes"]["away_completed"]
            analysis.shots_home = metrics["shots"]["home"]
            analysis.shots_away = metrics["shots"]["away"]
            analysis.tracking_data = {"frames": tracking_data[:10]}

            # Step 7: Generate tactical alerts
            alert_gen = TacticalAlertGenerator(metrics, match_id)
            for alert_data in alert_gen.generate_alerts():
                session.add(TacticalAlert(**alert_data))

            # Step 8: Generate training suggestions
            training_gen = TrainingSuggestionGenerator(metrics, alert_gen.generate_alerts(), match_id)
            for suggestion_data in training_gen.generate_suggestions():
                session.add(TrainingSuggestion(**suggestion_data))

            match.status = MatchStatus.COMPLETED
            session.commit()
            logger.info(f"Match {match_id} analysis completed successfully.")

        except Exception as exc:
            logger.exception(f"Match {match_id} analysis failed: {exc}")
            analysis.status = AnalysisStatus.FAILED
            match.status = MatchStatus.FAILED
            session.commit()


def main() -> None:
    """Worker main loop — blocks on Redis queue."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logger.info("PitchVision worker started, waiting for jobs...")

    while True:
        try:
            job = redis_client.blpop("analysis_queue", timeout=5)
            if job:
                _, raw_match_id = job
                match_id = int(raw_match_id)
                logger.info(f"Received job: match_id={match_id}")
                process_match_analysis(match_id)
        except Exception as exc:
            logger.error(f"Worker loop error: {exc}")
            time.sleep(1)


if __name__ == "__main__":
    main()
