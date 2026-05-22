"""
StatsBomb Open Data Loader.

Fetches data from the StatsBomb open-data GitHub repository with local
file-system caching so repeated calls don't hit the network.

Usage:
    loader = StatsBombLoader()
    competitions = loader.get_competitions()
    matches = loader.get_matches(competition_id=11, season_id=90)
    events = loader.get_events(statsbomb_match_id=3788741)
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

_BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
_DEFAULT_CACHE = Path(__file__).parent.parent.parent / "statsbomb_cache"


class StatsBombLoader:
    """Fetch and cache StatsBomb open-data JSON files."""

    def __init__(self, cache_dir: Optional[Path] = None, timeout: int = 30):
        self.cache_dir = Path(cache_dir) if cache_dir else _DEFAULT_CACHE
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout

    # ── Public API ────────────────────────────────────────────────────────────

    def get_competitions(self) -> List[Dict[str, Any]]:
        """Return all available competitions."""
        return self._fetch("competitions.json", "competitions.json")

    def get_matches(
        self,
        competition_id: int,
        season_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Return matches for a competition, optionally filtered by season."""
        url_path = f"matches/{competition_id}/{season_id}.json" if season_id else f"matches/{competition_id}.json"
        cache_name = f"matches_{competition_id}_{season_id or 'all'}.json"
        matches = self._fetch(url_path, cache_name)
        return matches

    def get_events(self, statsbomb_match_id: int) -> List[Dict[str, Any]]:
        """Return all events for a single match."""
        url_path = f"events/{statsbomb_match_id}.json"
        cache_name = f"events_{statsbomb_match_id}.json"
        return self._fetch(url_path, cache_name)

    def get_lineups(self, statsbomb_match_id: int) -> List[Dict[str, Any]]:
        """Return lineup data for a match."""
        url_path = f"lineups/{statsbomb_match_id}.json"
        cache_name = f"lineups_{statsbomb_match_id}.json"
        return self._fetch(url_path, cache_name)

    def list_available_matches(self) -> List[Dict[str, Any]]:
        """
        Return a flat list of all matches across all competitions/seasons.
        Useful for the import script to discover what's available.
        """
        competitions = self.get_competitions()
        all_matches: List[Dict[str, Any]] = []

        for comp in competitions:
            cid = comp["competition_id"]
            sid = comp["season_id"]
            try:
                matches = self.get_matches(cid, sid)
                for m in matches:
                    m["_competition"] = comp  # attach competition context
                all_matches.extend(matches)
            except Exception as exc:
                logger.warning("Could not load matches for comp=%s season=%s: %s", cid, sid, exc)

        return all_matches

    def clear_cache(self) -> None:
        """Delete all cached files."""
        for f in self.cache_dir.glob("*.json"):
            f.unlink()
        logger.info("StatsBomb cache cleared")

    # ── Internal ──────────────────────────────────────────────────────────────

    def _fetch(self, url_path: str, cache_name: str) -> Any:
        cache_path = self.cache_dir / cache_name

        if cache_path.exists():
            logger.debug("Cache hit: %s", cache_name)
            with open(cache_path, "r", encoding="utf-8") as fh:
                return json.load(fh)

        url = f"{_BASE_URL}/{url_path}"
        logger.info("Downloading: %s", url)

        try:
            response = httpx.get(url, timeout=self.timeout, follow_redirects=True)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"HTTP {exc.response.status_code} fetching {url}") from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"Network error fetching {url}: {exc}") from exc

        with open(cache_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

        return data
