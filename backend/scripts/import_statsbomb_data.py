#!/usr/bin/env python3
"""
StatsBomb Data Import Script.

Imports StatsBomb open-data matches into the PitchVision database.

Usage examples:
    # List available competitions
    python scripts/import_statsbomb_data.py --list-competitions

    # Import first 5 matches from La Liga 2015/16 (competition=11, season=27)
    python scripts/import_statsbomb_data.py --competition 11 --season 27 --team-id 1 --max 5

    # Import a single match by StatsBomb match_id
    python scripts/import_statsbomb_data.py --match-id 3788741 --team-id 1

    # Import all matches from a competition (may take several minutes)
    python scripts/import_statsbomb_data.py --competition 11 --season 27 --team-id 1
"""
import argparse
import json
import logging
import sys
from pathlib import Path

# Add backend root to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("import_statsbomb")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import StatsBomb open-data into PitchVision DB")
    parser.add_argument("--list-competitions", action="store_true", help="List available competitions and exit")
    parser.add_argument("--competition", type=int, help="StatsBomb competition_id")
    parser.add_argument("--season", type=int, help="StatsBomb season_id")
    parser.add_argument("--match-id", type=int, help="Import a single StatsBomb match_id")
    parser.add_argument("--team-id", type=int, default=1, help="Local team_id to associate matches with (default: 1)")
    parser.add_argument("--max", type=int, default=None, help="Max number of matches to import")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="Skip already-imported matches")
    parser.add_argument("--output", type=str, default=None, help="Write results JSON to this file")
    args = parser.parse_args()

    from app.database import engine
    from app.services.statsbomb_loader import StatsBombLoader
    from app.services.statsbomb_importer import StatsBombImporter
    from sqlmodel import Session

    loader = StatsBombLoader()

    # ── List competitions ──────────────────────────────────────────────────────
    if args.list_competitions:
        competitions = loader.get_competitions()
        print(f"\n{'ID':>6}  {'Season ID':>10}  {'Competition':<30}  {'Season':<20}  {'Country'}")
        print("-" * 90)
        for c in sorted(competitions, key=lambda x: (x["competition_name"], x["season_name"])):
            print(
                f"{c['competition_id']:>6}  {c['season_id']:>10}  "
                f"{c['competition_name']:<30}  {c['season_name']:<20}  {c.get('country_name', '')}"
            )
        print(f"\nTotal: {len(competitions)} competition-seasons")
        return

    # ── Single match import ────────────────────────────────────────────────────
    if args.match_id:
        with Session(engine) as session:
            importer = StatsBombImporter(session, loader)
            result = importer.import_match(
                statsbomb_match_id=args.match_id,
                team_id=args.team_id,
                skip_existing=args.skip_existing,
            )
        _print_result(result.to_dict())
        if args.output:
            _write_json([result.to_dict()], args.output)
        return

    # ── Competition import ─────────────────────────────────────────────────────
    if args.competition:
        if not args.season:
            # Find available seasons for this competition
            competitions = loader.get_competitions()
            seasons = [c for c in competitions if c["competition_id"] == args.competition]
            if not seasons:
                logger.error("Competition %d not found", args.competition)
                sys.exit(1)
            if len(seasons) > 1:
                print(f"\nMultiple seasons available for competition {args.competition}:")
                for s in seasons:
                    print(f"  season_id={s['season_id']}  {s['season_name']}")
                print("\nPlease specify --season <season_id>")
                sys.exit(1)
            args.season = seasons[0]["season_id"]

        logger.info(
            "Importing competition=%d season=%d (max=%s) → team_id=%d",
            args.competition, args.season, args.max, args.team_id,
        )

        with Session(engine) as session:
            importer = StatsBombImporter(session, loader)
            results = importer.import_competition(
                competition_id=args.competition,
                season_id=args.season,
                team_id=args.team_id,
                max_matches=args.max,
            )

        # Summary
        total = len(results)
        ok = sum(1 for r in results if r.success)
        total_events = sum(r.events_imported for r in results)
        print(f"\n{'='*60}")
        print(f"Import complete: {ok}/{total} matches successful")
        print(f"Total events imported: {total_events:,}")
        print(f"{'='*60}")

        for r in results:
            _print_result(r.to_dict())

        if args.output:
            _write_json([r.to_dict() for r in results], args.output)
        return

    parser.print_help()


def _print_result(r: dict) -> None:
    status = "✅" if r["success"] else "❌"
    skipped = " (already imported)" if r.get("events_skipped") == -1 else f" skipped={r['events_skipped']}"
    errors = f" errors={r['errors']}" if r.get("errors") else ""
    print(
        f"  {status} sb_match={r['statsbomb_match_id']} → match_id={r['match_id']} "
        f"imported={r['events_imported']}{skipped}{errors}"
    )


def _write_json(data: list, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    logger.info("Results written to %s", path)


if __name__ == "__main__":
    main()
