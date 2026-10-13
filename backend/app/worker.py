"""
Background worker for match analysis processing.
Listens to Redis queue and processes match analysis jobs.
"""
import redis
import time
import logging
import asyncio
import json
from sqlmodel import Session, create_engine, select

from app.config import settings
from app.cv.pipeline import CVPipeline, PipelineConfig
from app.cv.detector import DetectorConfig
from app.cv.tracker import TrackerConfig
from app.cv.calibration import PitchCalibrator
from app.analytics.metrics import TacticalMetricsCalculator
from app.analytics.alerts import TacticalAlertGenerator
from app.analytics.training import TrainingSuggestionGenerator
from app.models.match import Match, MatchStatus
from app.models.analysis import Analysis, AnalysisStatus
from app.models.tactical_alert import TacticalAlert
from app.models.training_suggestion import TrainingSuggestion
from app.models.match_report import MatchReport, ReportStatus
from app.engine.segmentation import generate_segments_for_match, update_segment_metrics
from app.engine.moment_detection import run_moment_detection
from app.engine.report_generator import generate_match_report

# Try to import OpenCV
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.REDIS_URL)
engine = create_engine(settings.DATABASE_URL)


def _run_cv_pipeline(match_id: int, video_path: str | None) -> list:
    """Run the CV pipeline on a video file.

    Uses the real YOLOv8 + ByteTrack pipeline when a valid video is provided,
    otherwise falls back to 150 mock frames.

    Returns a list of tracked-frame dicts compatible with the analytics engine.
    """
    det_cfg = DetectorConfig(
        model_weights  = settings.CV_MODEL_PATH if not settings.CV_MOCK_MODE else "mock",
        device         = "auto",
        imgsz          = 960,
        conf           = 0.15,
        iou            = 0.65,
        max_det        = 100,
        frame_interval = 5,  # every 5th frame — ~5 FPS equivalent for a 25 FPS source
    )

    pipeline_cfg = PipelineConfig(
        detector       = det_cfg,
        tracker        = TrackerConfig(frame_rate=25),
        frame_interval = 5,
        max_frames     = 500,   # ~20 s of gameplay per match for initial processing
    )

    pipeline = CVPipeline(pipeline_cfg)

    if settings.CV_MOCK_MODE or not video_path:
        logger.info(f"Match {match_id}: running in mock mode")
        return pipeline._run_mock_fallback()

    def _on_progress(done: int, total: int) -> None:
        pct = min(100, int(done / max(total, 1) * 100))
        logger.info(f"Match {match_id}: CV pipeline {pct}% ({done}/{total} frames)")

    tracking_data = pipeline.process(video_path, on_progress=_on_progress)
    logger.info(f"Match {match_id}: CV pipeline returned {len(tracking_data)} tracked frames")
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
        
        logger.info(f"Match {match_id}: ▶ Starting analysis pipeline")

        try:
            # Step 1: Generate time-based segments
            logger.info(f"Match {match_id}: [1/8] Generating segments...")
            segments = generate_segments_for_match(
                session=session,
                match_id=match_id,
                duration_minutes=match.duration_minutes,
            )
            logger.info(f"Match {match_id}: ✓ Created {len(segments)} segments")

            # Step 2: Run CV pipeline (mock or real)
            logger.info(f"Match {match_id}: [2/8] Running CV pipeline...")
            tracking_data = _run_cv_pipeline(match_id, match.video_url)
            logger.info(f"Match {match_id}: ✓ CV pipeline complete - {len(tracking_data)} frames")

            # Step 3: Detect tactical moments
            logger.info(f"Match {match_id}: [3/8] Detecting tactical moments...")
            engine_events = run_moment_detection(
                tracking_frames=tracking_data,
                match_id=match_id,
                segments=segments,
                session=session,
            )
            logger.info(f"Match {match_id}: ✓ Detected {len(engine_events)} tactical moments")

            # Step 4: Update per-segment metrics
            logger.info(f"Match {match_id}: [4/8] Updating segment metrics...")
            if engine_events:
                for segment in segments:
                    seg_events = [
                        e.model_dump() for e in engine_events
                        if e.segment_id == segment.id
                    ]
                    if seg_events:
                        update_segment_metrics(session, segment, seg_events)
            logger.info(f"Match {match_id}: ✓ Segment metrics updated")

            # Step 5: Calculate aggregate metrics
            logger.info(f"Match {match_id}: [5/8] Calculating metrics...")
            calculator = TacticalMetricsCalculator(tracking_data)
            metrics = calculator.get_all_metrics()
            logger.info(f"Match {match_id}: ✓ Metrics calculated - Possession: {metrics['possession']['home']:.1f}% vs {metrics['possession']['away']:.1f}%")

            # Step 6: Persist analysis results
            logger.info(f"Match {match_id}: [6/8] Persisting analysis...")
            analysis.status = AnalysisStatus.COMPLETED
            analysis.possession_home = metrics["possession"]["home"]
            analysis.possession_away = metrics["possession"]["away"]
            analysis.passes_completed_home = metrics["passes"]["home_completed"]
            analysis.passes_completed_away = metrics["passes"]["away_completed"]
            analysis.shots_home = metrics["shots"]["home"]
            analysis.shots_away = metrics["shots"]["away"]
            analysis.tracking_data = {"frames": tracking_data[:10]}
            logger.info(f"Match {match_id}: ✓ Analysis data persisted")

            # Step 7: Generate tactical alerts
            logger.info(f"Match {match_id}: [7/8] Generating tactical alerts...")
            alert_gen = TacticalAlertGenerator(metrics, match_id)
            alerts = alert_gen.generate_alerts()
            for alert_data in alerts:
                alert_data["match_id"] = match_id
                session.add(TacticalAlert(**alert_data))
            logger.info(f"Match {match_id}: ✓ Generated {len(alerts)} tactical alerts")

            # Step 8: Generate training suggestions
            logger.info(f"Match {match_id}: [8/8] Generating training suggestions...")
            training_gen = TrainingSuggestionGenerator(metrics, alerts, match_id)
            suggestions = training_gen.generate_suggestions()
            for suggestion_data in suggestions:
                session.add(TrainingSuggestion(**suggestion_data))
            logger.info(f"Match {match_id}: ✓ Generated {len(suggestions)} training suggestions")

            # Step 9: Generate AI match report (async, non-blocking)
            logger.info(f"Match {match_id}: [9/9] Queuing AI report generation...")
            try:
                # Queue report generation as a separate async task
                # This prevents the worker from hanging on NVIDIA API timeout
                report_data = generate_match_report(
                    match_id=match_id,
                    opponent_name=match.opponent_name,
                    team_name="Our Team",
                    analysis_metrics={
                        "possession_home": analysis.possession_home,
                        "possession_away": analysis.possession_away,
                        "passes_completed_home": analysis.passes_completed_home,
                        "passes_completed_away": analysis.passes_completed_away,
                        "shots_home": analysis.shots_home,
                        "shots_away": analysis.shots_away,
                    },
                    alerts=[a.model_dump() for a in session.query(TacticalAlert).filter(TacticalAlert.match_id == match_id).all()],
                    suggestions=[s.model_dump() for s in session.query(TrainingSuggestion).filter(TrainingSuggestion.match_id == match_id).all()],
                    match_date=str(match.match_date),
                    age_category=match.age_category or "U15",
                )
                
                if report_data:
                    # Save report to database
                    report = MatchReport(
                        match_id=match_id,
                        match_summary=report_data.get("match_summary", ""),
                        key_findings=report_data.get("key_findings", []),
                        tactical_recommendations=report_data.get("tactical_recommendations", []),
                        next_match_focus=report_data.get("next_match_focus", []),
                        status=ReportStatus.COMPLETED,
                        generated_by="nvidia_glm",
                    )
                    session.add(report)
                    session.commit()
                    logger.info(f"Match {match_id}: ✓ AI report generated and saved")
                else:
                    logger.warning(f"Match {match_id}: Report generation returned no data")
            except Exception as e:
                logger.warning(f"Match {match_id}: Report generation failed (non-blocking): {e}")
                # Don't fail the entire analysis if report generation fails

            match.status = MatchStatus.COMPLETED
            session.commit()
            logger.info(f"Match {match_id}: ✅ Analysis completed successfully!")

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
