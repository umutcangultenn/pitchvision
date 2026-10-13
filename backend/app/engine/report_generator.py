"""
AI-powered match report generation using NVIDIA API (GLM-5.1 with Reasoning)
"""
import logging
import requests
import json
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate match reports using NVIDIA GLM-5.1 API"""
    
    def __init__(self):
        self.base_url = settings.NVIDIA_BASE_URL
        self.api_key = settings.NVIDIA_API_KEY
        self.model = settings.NVIDIA_MODEL
        # Use shorter timeout for worker (30s instead of 120s)
        self.timeout = 30
    
    def generate_report(
        self,
        match_id: int,
        opponent_name: str,
        team_name: str,
        analysis_metrics: Dict[str, Any],
        alerts: list,
        suggestions: list,
        match_date: str,
        age_category: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a comprehensive match report using NVIDIA AI
        
        Args:
            match_id: Match ID
            opponent_name: Opponent team name
            team_name: Our team name
            analysis_metrics: Tactical metrics from analysis
            alerts: Tactical alerts
            suggestions: Training suggestions
            match_date: Match date
            age_category: Age category (U15, U13, etc.)
        
        Returns:
            Report data dict or None if failed
        """
        try:
            logger.info(f"Match {match_id}: Generating report with NVIDIA AI (timeout: {self.timeout}s)...")
            
            # Prepare context for AI
            context = self._prepare_context(
                opponent_name, team_name, analysis_metrics, alerts, suggestions, age_category
            )
            
            # Call NVIDIA API
            report_data = self._call_nvidia_api(context)
            
            if report_data:
                logger.info(f"Match {match_id}: ✓ Report generated successfully")
                return report_data
            else:
                logger.error(f"Match {match_id}: Failed to generate report")
                return None
                
        except Exception as e:
            logger.error(f"Match {match_id}: Report generation error: {e}")
            return None
    
    def _prepare_context(
        self,
        opponent_name: str,
        team_name: str,
        metrics: Dict[str, Any],
        alerts: list,
        suggestions: list,
        age_category: str,
    ) -> str:
        """Prepare context for AI analysis"""
        
        alerts_text = "\n".join([
            f"- {a.get('title', 'Alert')}: {a.get('description', '')}"
            for a in alerts[:5]  # Top 5 alerts
        ]) if alerts else "No alerts detected"
        
        suggestions_text = "\n".join([
            f"- {s.get('title', 'Suggestion')}: {s.get('description', '')}"
            for s in suggestions[:3]  # Top 3 suggestions
        ]) if suggestions else "No suggestions"
        
        context = f"""
Analiz et ve rapor oluştur:

Maç: {team_name} vs {opponent_name}
Yaş Kategorisi: {age_category}

Taktiksel Metrikler:
- Possession: {metrics.get('possession_home', 50)}% vs {metrics.get('possession_away', 50)}%
- Passes: {metrics.get('passes_completed_home', 0)} vs {metrics.get('passes_completed_away', 0)}
- Shots: {metrics.get('shots_home', 0)} vs {metrics.get('shots_away', 0)}

Taktiksel Uyarılar:
{alerts_text}

Antrenman Önerileri:
{suggestions_text}

Lütfen aşağıdakileri içeren bir maç raporu oluştur (Türkçe):
1. Maç özeti (2-3 cümle)
2. En önemli 3 bulgu
3. Takım şekli analizi
4. Taktiksel öneriler (3-4 madde)
5. Bir sonraki maçta takip edilecek göstergeler (3-4 madde)

Yanıt JSON formatında olmalı:
{{
    "match_summary": "...",
    "key_findings": ["...", "...", "..."],
    "tactical_recommendations": ["...", "...", "..."],
    "next_match_focus": ["...", "...", "..."]
}}
"""
        return context
    
    def _call_nvidia_api(self, context: str) -> Optional[Dict[str, Any]]:
        """Call NVIDIA GLM-5.1 API with timeout handling"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": context,
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1500,  # Reduced from 2000
            }
            
            logger.info(f"Calling NVIDIA API: {self.model} (timeout: {self.timeout}s)")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            
            if response.status_code != 200:
                logger.error(f"NVIDIA API error: {response.status_code} - {response.text[:200]}")
                return None
            
            result = response.json()
            
            # Extract content from response
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                
                # Parse JSON from response
                try:
                    # Try to extract JSON from the response
                    json_start = content.find("{")
                    json_end = content.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        report_data = json.loads(json_str)
                        return report_data
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON from NVIDIA response: {content[:200]}")
                    return None
            
            return None
            
        except requests.Timeout:
            logger.error(f"NVIDIA API timeout after {self.timeout}s - skipping report generation")
            return None
        except requests.ConnectionError as e:
            logger.error(f"NVIDIA API connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"NVIDIA API call error: {e}")
            return None


def generate_match_report(
    match_id: int,
    opponent_name: str,
    team_name: str,
    analysis_metrics: Dict[str, Any],
    alerts: list,
    suggestions: list,
    match_date: str,
    age_category: str,
) -> Optional[Dict[str, Any]]:
    """Convenience function to generate a report"""
    generator = ReportGenerator()
    return generator.generate_report(
        match_id, opponent_name, team_name, analysis_metrics, alerts, suggestions, match_date, age_category
    )
