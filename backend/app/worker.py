import redis
import time
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

redis_client = redis.from_url(settings.REDIS_URL)
engine = create_engine(settings.DATABASE_URL)


def process_match_analysis(match_id: int):
    """Process match analysis"""
    with Session(engine) as session:
        match = session.get(Match, match_id)
        if not match:
            return
        
        # Create analysis
        analysis = Analysis(match_id=match_id, status=AnalysisStatus.DETECTING)
        session.add(analysis)
        match.status = MatchStatus.ANALYZING
        session.commit()
        
        # Mock detection and tracking
        detector = get_detector()
        tracker = SimpleTracker()
        tracking_data = []
        
        # Simulate processing 100 frames
        for i in range(100):
            detections = detector.detect_frame(None, i)
            tracked = tracker.update(detections)
            tracking_data.append(tracked)
            time.sleep(0.1)  # Simulate processing time
        
        # Calculate metrics
        calculator = TacticalMetricsCalculator(tracking_data)
        metrics = calculator.get_all_metrics()
        
        # Update analysis
        analysis.status = AnalysisStatus.COMPLETED
        analysis.possession_home = metrics["possession"]["home"]
        analysis.possession_away = metrics["possession"]["away"]
        analysis.passes_completed_home = metrics["passes"]["home_completed"]
        analysis.passes_completed_away = metrics["passes"]["away_completed"]
        analysis.shots_home = metrics["shots"]["home"]
        analysis.shots_away = metrics["shots"]["away"]
        analysis.tracking_data = {"frames": tracking_data[:10]}  # Store sample
        
        # Generate alerts
        alert_gen = TacticalAlertGenerator(metrics, match_id)
        alerts = alert_gen.generate_alerts()
        for alert_data in alerts:
            alert = TacticalAlert(**alert_data)
            session.add(alert)
        
        # Generate training suggestions
        training_gen = TrainingSuggestionGenerator(metrics, alerts, match_id)
        suggestions = training_gen.generate_suggestions()
        for suggestion_data in suggestions:
            suggestion = TrainingSuggestion(**suggestion_data)
            session.add(suggestion)
        
        match.status = MatchStatus.COMPLETED
        session.commit()


def main():
    """Worker main loop"""
    print("Worker started, waiting for jobs...")
    
    while True:
        try:
            # Block and wait for job
            job = redis_client.blpop("analysis_queue", timeout=5)
            
            if job:
                _, match_id = job
                match_id = int(match_id)
                print(f"Processing match {match_id}")
                process_match_analysis(match_id)
                print(f"Completed match {match_id}")
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
