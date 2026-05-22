/**
 * StatsBomb API client functions.
 *
 * These functions call the Phase 3 StatsBomb endpoints on the backend.
 * They follow the same ApiResult pattern as the main api.ts.
 */

import type { ApiResult } from "@/lib/api";
import { getAuthToken } from "@/lib/api";

const BASE =
  typeof process.env.NEXT_PUBLIC_API_URL === "string"
    ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")
    : "http://localhost:8000";

const API_V1 = "/api";

function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${BASE}${API_V1}${p}`;
}

async function req<T>(
  path: string,
  options?: Omit<RequestInit, "body"> & { body?: unknown },
): Promise<ApiResult<T>> {
  try {
    const hasBody = options?.body !== undefined;
    const token = getAuthToken();
    const res = await fetch(apiUrl(path), {
      ...options,
      headers: {
        ...(hasBody ? { "Content-Type": "application/json" } : {}),
        ...(token ? { "Authorization": `Bearer ${token}` } : {}),
        ...options?.headers,
      },
      body: hasBody ? JSON.stringify(options!.body) : undefined,
      cache: "no-store",
    });

    if (!res.ok) {
      let message = `HTTP ${res.status}`;
      try {
        const j = await res.json();
        message = j?.detail ?? message;
      } catch { /* ignore */ }
      return { ok: false, data: null, error: { status: res.status, message } };
    }

    const data = (await res.json()) as T;
    return { ok: true, data, error: null };
  } catch (e) {
    const message = e instanceof Error ? e.message : "Network error";
    return { ok: false, data: null, error: { status: "network", message } };
  }
}

// ── Types ─────────────────────────────────────────────────────────────────────

export type StatsBombCompetition = {
  competition_id: number;
  competition_name: string;
  season_id: number;
  season_name: string;
  country_name: string;
};

export type StatsBombMatch = {
  match_id: number;
  match_date: string;
  kick_off: string;
  competition: { competition_id: number; competition_name: string };
  season: { season_id: number; season_name: string };
  home_team: { home_team_id: number; home_team_name: string };
  away_team: { away_team_id: number; away_team_name: string };
  home_score: number;
  away_score: number;
  match_status: string;
};

export type StatsBombEvent = {
  id: string;
  index: number;
  period: number;
  timestamp: string;
  minute: number;
  second: number;
  type: { id: number; name: string };
  possession: number;
  possession_team?: { id: number; name: string };
  play_pattern?: { id: number; name: string };
  player?: { id: number; name: string };
  team?: { id: number; name: string };
  position?: { id: number; name: string };
  location?: [number, number];
  duration?: number;
  [key: string]: unknown;
};

export type EventTimelineEntry = {
  id: string;
  type: string;
  category: string;
  timestamp: number;
  minute: number;
  second: number;
  period: number;
  player_id?: number;
  player_name?: string;
  team_id?: number;
  team_name?: string;
  location_x?: number;
  location_y?: number;
  outcome?: string;
  xg?: number;
  length?: number;
  end_x?: number;
  end_y?: number;
};

export type MatchMetrics = {
  possession_home: number;
  possession_away: number;
  passes_completed_home: number;
  passes_completed_away: number;
  passes_attempted_home: number;
  passes_attempted_away: number;
  shots_home: number;
  shots_away: number;
  shots_on_target_home: number;
  shots_on_target_away: number;
  tackles_home: number;
  tackles_away: number;
  pressures_home: number;
  pressures_away: number;
  duels_home: number;
  duels_away: number;
  clearances_home: number;
  clearances_away: number;
  interceptions_home: number;
  interceptions_away: number;
  home_team_id?: number;
  away_team_id?: number;
  total_events: number;
};

export type XgData = {
  total_xg: number;
  shot_count: number;
  xg_per_shot: number;
  shots: {
    player: string;
    minute: number;
    xg: number;
    outcome: string;
    technique?: string;
    body_part?: string;
    location_x?: number;
    location_y?: number;
  }[];
};

export type AdvancedMetrics = MatchMetrics & {
  advanced: {
    xg: { home: XgData; away: XgData };
    ppda: {
      home_ppda: number;
      away_ppda: number;
      home_def_actions: number;
      away_def_actions: number;
    };
    progressive_passes: {
      home: { total_progressive_passes: number; total_passes: number; progressive_pass_rate: number };
      away: { total_progressive_passes: number; total_passes: number; progressive_pass_rate: number };
    };
    field_tilt: {
      home_field_tilt: number;
      away_field_tilt: number;
      home_final_third_touches: number;
      away_final_third_touches: number;
    };
  };
};

export type PlayerMetrics = {
  player_id: number;
  player_name: string;
  total_events: number;
  passes_attempted: number;
  passes_completed: number;
  pass_accuracy: number;
  shots: number;
  xg: number;
  tackles: number;
  pressures: number;
  carries: number;
  dribbles_attempted: number;
  dribbles_completed: number;
  dribble_success_rate: number;
};

export type ImportResult = {
  statsbomb_match_id: number;
  match_id: number | null;
  events_imported: number;
  events_skipped: number;
  errors: string[];
  success: boolean;
};

// ── Competitions & Matches ────────────────────────────────────────────────────

export async function sbGetCompetitions(): Promise<ApiResult<StatsBombCompetition[]>> {
  return req<StatsBombCompetition[]>("/statsbomb/competitions");
}

export async function sbGetMatches(
  competitionId: number,
  seasonId?: number,
): Promise<ApiResult<StatsBombMatch[]>> {
  const params = seasonId ? `?season_id=${seasonId}` : "";
  return req<StatsBombMatch[]>(`/statsbomb/matches/${competitionId}${params}`);
}

// ── Events ────────────────────────────────────────────────────────────────────

export async function sbGetRawEvents(
  statsbombMatchId: number,
  eventType?: string,
): Promise<ApiResult<StatsBombEvent[]>> {
  const params = eventType ? `?event_type=${encodeURIComponent(eventType)}` : "";
  return req<StatsBombEvent[]>(`/statsbomb/events/${statsbombMatchId}${params}`);
}

export async function sbGetTimeline(
  statsbombMatchId: number,
): Promise<ApiResult<EventTimelineEntry[]>> {
  return req<EventTimelineEntry[]>(`/statsbomb/timeline/${statsbombMatchId}`);
}

// ── Metrics ───────────────────────────────────────────────────────────────────

export async function sbGetMetrics(
  statsbombMatchId: number,
): Promise<ApiResult<MatchMetrics>> {
  return req<MatchMetrics>(`/statsbomb/metrics/${statsbombMatchId}`);
}

export async function sbGetAdvancedMetrics(
  statsbombMatchId: number,
): Promise<ApiResult<AdvancedMetrics>> {
  return req<AdvancedMetrics>(`/statsbomb/advanced-metrics/${statsbombMatchId}`);
}

export async function sbGetPlayerMetrics(
  statsbombMatchId: number,
  playerId: number,
): Promise<ApiResult<PlayerMetrics>> {
  return req<PlayerMetrics>(`/statsbomb/player-metrics/${statsbombMatchId}/${playerId}`);
}

// ── Alerts ────────────────────────────────────────────────────────────────────

export async function sbGetAlerts(
  statsbombMatchId: number,
): Promise<ApiResult<Record<string, unknown>[]>> {
  return req<Record<string, unknown>[]>(`/statsbomb/alerts/${statsbombMatchId}`);
}

// ── Import ────────────────────────────────────────────────────────────────────

export async function sbImportMatch(
  statsbombMatchId: number,
  teamId: number,
  matchId?: number,
  skipExisting = true,
): Promise<ApiResult<ImportResult>> {
  const params = new URLSearchParams({ team_id: String(teamId), skip_existing: String(skipExisting) });
  if (matchId) params.append("match_id", String(matchId));
  return req<ImportResult>(`/statsbomb/import/${statsbombMatchId}?${params}`, { method: "POST" });
}

export async function sbImportCompetition(
  competitionId: number,
  seasonId: number,
  teamId: number,
  maxMatches?: number,
): Promise<ApiResult<ImportResult[]>> {
  const params = new URLSearchParams({
    competition_id: String(competitionId),
    season_id: String(seasonId),
    team_id: String(teamId),
  });
  if (maxMatches) params.append("max_matches", String(maxMatches));
  return req<ImportResult[]>(`/statsbomb/import-competition?${params}`, { method: "POST" });
}

// ── DB-backed queries ─────────────────────────────────────────────────────────

export async function sbGetDbEvents(
  matchId: number,
  eventType?: string,
  limit = 500,
  offset = 0,
): Promise<ApiResult<Record<string, unknown>[]>> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (eventType) params.append("event_type", eventType);
  return req<Record<string, unknown>[]>(`/statsbomb/db/events/${matchId}?${params}`);
}

export async function sbGetDbEventCount(
  matchId: number,
): Promise<ApiResult<{ match_id: number; total: number; by_type: Record<string, number> }>> {
  return req(`/statsbomb/db/events/${matchId}/count`);
}
