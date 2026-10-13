/**
 * Centralized API client for PitchVision backend.
 * All requests are authenticated via the JWT token stored in localStorage.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface MatchData {
  id: number;
  opponent_name: string;
  match_date: string;
  location: string;
  home_away: string;
  duration_minutes: number;
  status: string;
  video_url?: string | null;
  final_score_home?: number | null;
  final_score_away?: number | null;
  team_id: number;
  created_at: string;
}

export interface MatchSegment {
  id: number;
  match_id: number;
  segment_label: string;
  start_time: number;
  end_time: number;
  event_density: number;
  transition_count: number;
  dangerous_attacks: number;
  box_entries: number;
  attack_tendency?: Record<string, number> | null;
  pressure_tendency?: Record<string, number> | null;
  tactical_summary_ai?: string | null;
  analyst_summary?: string | null;
  analysis_confidence: number;
  created_at: string;
}

export interface EngineEvent {
  id: number;
  match_id: number;
  segment_id?: number | null;
  event_type: string;
  timestamp_seconds: number;
  duration_seconds?: number | null;
  confidence: number;
  description: string;
  evidence?: Record<string, unknown> | null;
  analyst_reviewed: boolean;
  analyst_verdict?: string | null;
  analyst_notes?: string | null;
  created_at: string;
}

export interface AnalystEvent {
  id: number;
  match_id: number;
  segment_id?: number | null;
  analyst_id: number;
  tag: string;
  timestamp_seconds: number;
  notes?: string | null;
  confidence: string;
  validates_engine_event_id?: number | null;
  validation_status?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AnalystEventCreate {
  match_id: number;
  tag: string;
  timestamp_seconds: number;
  notes?: string;
  confidence?: string;
  segment_id?: number;
  validates_engine_event_id?: number;
  validation_status?: string;
}

export interface ComparisonResult {
  id: number;
  match_id: number;
  total_engine_events: number;
  total_analyst_events: number;
  overlapping_events: number;
  engine_only_events: number;
  analyst_only_events: number;
  agreement_ratio: number;
  comparison_summary?: string | null;
  created_at: string;
}

export interface AISummaryResponse {
  match_id: number;
  draft: string;
}

// ── HTTP helpers ──────────────────────────────────────────────────────────────

function getAuthHeaders(): HeadersInit {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`API ${res.status}: ${errorBody}`);
  }

  return res.json() as Promise<T>;
}

// ── Match endpoints ───────────────────────────────────────────────────────────

export const matchApi = {
  getById: (matchId: number) =>
    request<MatchData>(`/api/matches/${matchId}`),
};

// ── Segment endpoints ─────────────────────────────────────────────────────────

export const segmentApi = {
  getByMatch: (matchId: number) =>
    request<MatchSegment[]>(`/api/segments/${matchId}`),
};

// ── Engine event endpoints ────────────────────────────────────────────────────

export const engineEventApi = {
  getByMatch: (matchId: number, segmentId?: number) => {
    const qs = segmentId != null ? `?segment_id=${segmentId}` : "";
    return request<EngineEvent[]>(`/api/engine-events/${matchId}${qs}`);
  },
  review: (eventId: number, verdict: string, notes?: string) =>
    request<EngineEvent>(`/api/engine-events/${eventId}/review`, {
      method: "PATCH",
      body: JSON.stringify({ verdict, notes }),
    }),
};

// ── Analyst event endpoints ───────────────────────────────────────────────────

export const analystEventApi = {
  getByMatch: (matchId: number) =>
    request<AnalystEvent[]>(`/api/analyst-events/${matchId}`),
  create: (payload: AnalystEventCreate) =>
    request<AnalystEvent>("/api/analyst-events/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  delete: (eventId: number) =>
    request<{ ok: boolean }>(`/api/analyst-events/${eventId}`, {
      method: "DELETE",
    }),
};

// ── Comparison endpoints ──────────────────────────────────────────────────────

export const comparisonApi = {
  getByMatch: (matchId: number) =>
    request<ComparisonResult>(`/api/comparison/${matchId}`),
  generate: (matchId: number) =>
    request<ComparisonResult>(`/api/comparison/${matchId}/generate`, {
      method: "POST",
    }),
};

// ── AI Summary endpoints ──────────────────────────────────────────────────────

export const aiApi = {
  matchSummary: (matchId: number) =>
    request<AISummaryResponse>(`/api/ai/match-summary/${matchId}`, {
      method: "POST",
    }),
  health: () => request<{ status: string }>("/api/ai/health"),
};
