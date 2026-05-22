/**
 * PitchVision Lite — API client
 *
 * NEXT_PUBLIC_USE_MOCKS=true  → mock data (default, backend hazır değilse)
 * NEXT_PUBLIC_USE_MOCKS=false → gerçek backend (NEXT_PUBLIC_API_URL gerekli)
 *
 * Her fonksiyon: real API → başarısız olursa mock fallback döner.
 */

import type {
  Clip,
  DrillRecommendation,
  Match,
  Player,
  Report,
  ScoutNote,
  TacticalAlert,
  TacticalMetric,
  VideoAsset,
} from "@/types/domain";

import {
  DEMO_TEAM_METRICS,
  mockAlerts,
  mockClips,
  mockDrills,
  mockMatches,
  mockMetrics,
  mockPerformances,
  mockPlayers,
  mockReports,
  mockScoutingNotes,
  mockTeams,
  mockVideos,
} from "@/data/demo";

// ── Config ────────────────────────────────────────────────────────────────────

const BASE =
  typeof process.env.NEXT_PUBLIC_API_URL === "string"
    ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")
    : "http://localhost:8000";

const API_V1 = "/api";

function apiUrl(path: string): string {
  if (path === "/health") return `${BASE}${path}`;
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${BASE}${API_V1}${p}`;
}

const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS === "true";

// ── Auth token helpers ────────────────────────────────────────────────────────

const TOKEN_KEY = "pv_access_token";

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  if (typeof window !== "undefined") localStorage.setItem(TOKEN_KEY, token);
}

export function clearAuthToken(): void {
  if (typeof window !== "undefined") localStorage.removeItem(TOKEN_KEY);
}

// ── Core types ────────────────────────────────────────────────────────────────

export type ApiResult<T> =
  | { ok: true;  data: T;     error: null }
  | { ok: false; data: null;  error: ApiError };

export type ApiError = {
  status: number | "network" | "parse";
  message: string;
};

// ── Low-level fetch ───────────────────────────────────────────────────────────

async function req<T>(
  path: string,
  options?: Omit<RequestInit, "body"> & { body?: any },
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
      try { const j = await res.json(); message = j?.detail ?? message; } catch { /* ignore */ }
      return { ok: false, data: null, error: { status: res.status, message } };
    }

    const data = (await res.json()) as T;
    return { ok: true, data, error: null };
  } catch (e) {
    const message = e instanceof Error ? e.message : "Network error";
    return { ok: false, data: null, error: { status: "network", message } };
  }
}

/** Mock'u gerçek API sonucu gibi sarmalar */
function ok<T>(data: T): ApiResult<T> {
  return { ok: true, data, error: null };
}

// ── Health ────────────────────────────────────────────────────────────────────

export async function apiHealth(): Promise<ApiResult<{ status: string }>> {
  if (USE_MOCKS) return ok({ status: "ok (mock)" });
  return req("/health");
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export type AuthUser = {
  id: number;
  email: string;
  full_name: string;
  role: string;
  organization?: string;
  is_active: boolean;
  created_at: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export async function apiLogin(
  email: string,
  password: string,
): Promise<ApiResult<LoginResponse>> {
  // Backend uses OAuth2PasswordRequestForm (form-encoded, not JSON)
  const body = new URLSearchParams({ username: email, password });
  try {
    const res = await fetch(apiUrl("/auth/login"), {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
      cache: "no-store",
    });
    if (!res.ok) {
      let message = `HTTP ${res.status}`;
      try { const j = await res.json(); message = j?.detail ?? message; } catch { /* ignore */ }
      return { ok: false, data: null, error: { status: res.status, message } };
    }
    const data = (await res.json()) as LoginResponse;
    return { ok: true, data, error: null };
  } catch (e) {
    const message = e instanceof Error ? e.message : "Network error";
    return { ok: false, data: null, error: { status: "network", message } };
  }
}

export async function apiRegister(payload: {
  email: string;
  password: string;
  full_name: string;
  role?: string;
  organization?: string;
}): Promise<ApiResult<AuthUser>> {
  return req<AuthUser>("/auth/register", { method: "POST", body: payload });
}

export async function apiGetMe(): Promise<ApiResult<AuthUser>> {
  return req<AuthUser>("/auth/me");
}

// ── Matches ───────────────────────────────────────────────────────────────────

/** Transform API response (snake_case) to frontend format (camelCase) */
function transformMatch(raw: any): Match {
  return {
    id: raw.id,
    organizationId: raw.organization_id || 1,
    teamId: raw.team_id,
    opponentName: raw.opponent_name,
    matchDate: raw.match_date,
    ageCategory: raw.age_category || "U15",
    gameFormat: raw.game_format || "11v11",
    pitchLength: raw.pitch_length || 105,
    pitchWidth: raw.pitch_width || 68,
    firstHalfAttackDirection: raw.first_half_attack_direction || "left",
    scoreFor: raw.final_score_home || 0,
    scoreAgainst: raw.final_score_away || 0,
    videoSource: raw.video_source || "file_upload",
    status: raw.status || "scheduled",
    createdAt: raw.created_at,
  };
}

export async function apiGetMatches(orgId?: number): Promise<ApiResult<Match[]>> {
  if (USE_MOCKS) return ok(mockMatches as Match[]);
  const r = await req<any[]>("/matches");
  if (r.ok) {
    return ok(r.data.map(transformMatch));
  }
  return ok(mockMatches as Match[]);
}

export async function apiGetMatchById(matchId: number): Promise<ApiResult<Match>> {
  if (USE_MOCKS) {
    const m = mockMatches.find((x) => x.id === matchId);
    return m ? ok(m as Match) : { ok: false, data: null, error: { status: 404, message: "Maç bulunamadı" } };
  }
  const r = await req<any>(`/matches/${matchId}`);
  if (r.ok) {
    return ok(transformMatch(r.data));
  }
  const fallback = mockMatches.find((x) => x.id === matchId);
  return fallback ? ok(fallback as Match) : r;
}

export async function apiCreateMatch(payload: Partial<Match>): Promise<ApiResult<Match>> {
  if (USE_MOCKS) return ok({ ...mockMatches[0], ...payload } as Match);
  return req<Match>("/matches", { method: "POST", body: payload });
}

export async function apiGetMatchSummary(matchId: number): Promise<ApiResult<Record<string, unknown>>> {
  if (USE_MOCKS) return ok({ match_id: matchId, ...DEMO_TEAM_METRICS });
  const r = await req<{ data: Record<string, unknown> }>(`/matches/${matchId}/summary`);
  return r.ok ? ok(r.data.data) : ok({ match_id: matchId, ...DEMO_TEAM_METRICS });
}

// ── Video / Processing ────────────────────────────────────────────────────────

export async function apiGetMatchVideo(matchId: number): Promise<ApiResult<VideoAsset>> {
  if (USE_MOCKS) {
    const v = mockVideos.find((x) => x.matchId === matchId);
    return v ? ok(v as VideoAsset) : { ok: false, data: null, error: { status: 404, message: "Video bulunamadı" } };
  }
  const r = await req<VideoAsset>(`/matches/${matchId}/video`);
  if (r.ok) return r;
  const fallback = mockVideos.find((x) => x.matchId === matchId);
  return fallback ? ok(fallback as VideoAsset) : r;
}

export async function apiUploadVideoFromURL(
  matchId: number,
  url: string,
  title?: string
): Promise<ApiResult<{ message: string; match_id: number; video_path?: string }>> {
  if (USE_MOCKS) return ok({ message: "Video yüklendi (mock)", match_id: matchId });
  return req(`/matches/${matchId}/upload-url`, {
    method: "POST",
    body: { url, title }
  });
}

export async function apiUploadVideoFile(
  matchId: number,
  file: File
): Promise<ApiResult<{ message: string; match_id: number; video_path?: string }>> {
  if (USE_MOCKS) return ok({ message: "Video yüklendi (mock)", match_id: matchId });
  
  const formData = new FormData();
  formData.append("file", file);
  
  try {
    const response = await fetch(`${BASE}/api/matches/${matchId}/upload`, {
      method: "POST",
      body: formData,
      cache: "no-store",
    });
    
    if (!response.ok) {
      let message = `HTTP ${response.status}`;
      try {
        const j = await response.json();
        message = j?.detail ?? message;
      } catch {}
      return { ok: false, data: null, error: { status: response.status, message } };
    }
    
    const data = await response.json();
    return { ok: true, data, error: null };
  } catch (e) {
    const message = e instanceof Error ? e.message : "Network error";
    return { ok: false, data: null, error: { status: "network", message } };
  }
}

export type ProcessingStatus = { status: string };

export async function apiGetProcessingStatus(matchId: number): Promise<ApiResult<ProcessingStatus>> {
  if (USE_MOCKS) {
    const v = mockVideos.find((x) => x.matchId === matchId);
    return ok({ status: v?.status ?? "not_uploaded" });
  }
  const r = await req<{ data: ProcessingStatus }>(`/matches/${matchId}/processing-status`);
  return r.ok ? ok(r.data.data) : ok({ status: "unknown" });
}

export async function apiStartProcessing(matchId: number): Promise<ApiResult<{ message: string }>> {
  if (USE_MOCKS) return ok({ message: "İşleme başlatıldı (mock)" });
  return req(`/matches/${matchId}/process`, { method: "POST" });
}

// ── Calibration ───────────────────────────────────────────────────────────────

export type CalibrationPayload = {
  match_id?: number;
  frame_time: number;
  points_json: Record<string, unknown>;
  homography_json: Record<string, unknown>;
  average_error_m?: number;
  quality?: number;
};

export type CalibrationRead = CalibrationPayload & {
  id: number;
  created_at: string;
};

const MOCK_CALIBRATION: CalibrationRead = {
  id: 1,
  match_id: 1001,
  frame_time: 0,
  points_json: {},
  homography_json: {},
  average_error_m: DEMO_TEAM_METRICS.calibrationError,
  quality: 0.92,
  created_at: new Date().toISOString(),
};

export async function apiGetCalibration(matchId: number): Promise<ApiResult<CalibrationRead>> {
  if (USE_MOCKS) return ok({ ...MOCK_CALIBRATION, match_id: matchId });
  const r = await req<CalibrationRead>(`/matches/${matchId}/calibration`);
  return r.ok ? r : ok({ ...MOCK_CALIBRATION, match_id: matchId });
}

export async function apiSaveCalibration(
  matchId: number,
  payload: CalibrationPayload,
): Promise<ApiResult<CalibrationRead>> {
  if (USE_MOCKS) return ok({ ...MOCK_CALIBRATION, ...payload, match_id: matchId });
  return req<CalibrationRead>(`/matches/${matchId}/calibration`, { method: "POST", body: payload });
}

export async function apiTestCalibration(matchId: number): Promise<ApiResult<{ result: string }>> {
  if (USE_MOCKS) return ok({ result: "ok" });
  const r = await req<{ data: { result: string } }>(`/matches/${matchId}/calibration/test`, { method: "POST" });
  return r.ok ? ok(r.data.data) : ok({ result: "ok" });
}

// ── Metrics ───────────────────────────────────────────────────────────────────

export async function apiGetMetrics(matchId: number): Promise<ApiResult<TacticalMetric[]>> {
  if (USE_MOCKS) return ok(mockMetrics.filter((m) => m.matchId === matchId) as TacticalMetric[]);
  const r = await req<TacticalMetric[]>(`/matches/${matchId}/metrics`);
  return r.ok ? r : ok(mockMetrics.filter((m) => m.matchId === matchId) as TacticalMetric[]);
}

export async function apiRecalculateMetrics(matchId: number): Promise<ApiResult<{ status: string }>> {
  if (USE_MOCKS) return ok({ status: "recalculated (mock)" });
  const r = await req<{ data: { status: string } }>(`/matches/${matchId}/metrics/recalculate`, { method: "POST" });
  return r.ok ? ok(r.data.data) : ok({ status: "error" });
}

// ── Analysis ──────────────────────────────────────────────────────────────────

export type AnalysisData = {
  id: number;
  match_id: number;
  status: string;
  possession_home: number;
  possession_away: number;
  passes_completed_home: number;
  passes_completed_away: number;
  shots_home: number;
  shots_away: number;
  tracking_data?: Record<string, unknown>;
  progress_percentage?: number;
};

export async function apiGetAnalysis(matchId: number): Promise<ApiResult<AnalysisData>> {
  if (USE_MOCKS) return ok({
    id: 1,
    match_id: matchId,
    status: "completed",
    possession_home: 57,
    possession_away: 43,
    passes_completed_home: 244,
    passes_completed_away: 338,
    shots_home: 16,
    shots_away: 11,
    progress_percentage: 100,
  });
  const r = await req<AnalysisData>(`/analysis/${matchId}`);
  if (r.ok) return r;
  return ok({
    id: 1,
    match_id: matchId,
    status: "pending",
    possession_home: 50,
    possession_away: 50,
    passes_completed_home: 0,
    passes_completed_away: 0,
    shots_home: 0,
    shots_away: 0,
    progress_percentage: 0,
  });
}

// ── Alerts ────────────────────────────────────────────────────────────────────

export async function apiGetAlerts(matchId: number): Promise<ApiResult<TacticalAlert[]>> {
  if (USE_MOCKS) return ok(mockAlerts.filter((a) => a.matchId === matchId) as TacticalAlert[]);
  const r = await req<TacticalAlert[]>(`/analysis/${matchId}/alerts`);
  return r.ok ? r : ok(mockAlerts.filter((a) => a.matchId === matchId) as TacticalAlert[]);
}

export async function apiApproveAlert(alertId: number): Promise<ApiResult<TacticalAlert>> {
  if (USE_MOCKS) return ok(mockAlerts[0] as TacticalAlert);
  return req<TacticalAlert>(`/alerts/${alertId}/approve`, { method: "POST" });
}

export async function apiRejectAlert(alertId: number): Promise<ApiResult<TacticalAlert>> {
  if (USE_MOCKS) return ok(mockAlerts[0] as TacticalAlert);
  return req<TacticalAlert>(`/alerts/${alertId}/reject`, { method: "POST" });
}

// ── Reports ───────────────────────────────────────────────────────────────────

export type MatchReport = {
  id: number;
  match_id: number;
  match_summary: string;
  key_findings: string[];
  tactical_recommendations: string[];
  next_match_focus: string[];
  status: "pending" | "generating" | "completed" | "failed";
  generated_by: string;
  generated_at?: string;
  created_at: string;
  disclaimer: string;
};

export async function apiGetReport(matchId: number): Promise<ApiResult<MatchReport>> {
  if (USE_MOCKS) {
    return ok({
      id: 1,
      match_id: matchId,
      match_summary: "Mock report summary",
      key_findings: ["Finding 1", "Finding 2"],
      tactical_recommendations: ["Recommendation 1"],
      next_match_focus: ["Focus 1"],
      status: "completed",
      generated_by: "ai_mock",
      created_at: new Date().toISOString(),
      disclaimer: "Bu rapor otomatik analiz adayıdır.",
    } as MatchReport);
  }
  const r = await req<MatchReport>(`/reports/${matchId}`);
  if (r.ok) return r;
  return {
    ok: false,
    data: null,
    error: { status: 404, message: "Rapor bulunamadı" },
  };
}

// ── Clips ─────────────────────────────────────────────────────────────────────

export async function apiGetClips(matchId: number): Promise<ApiResult<Clip[]>> {
  if (USE_MOCKS) return ok(mockClips.filter((c) => c.matchId === matchId) as Clip[]);
  const r = await req<Clip[]>(`/matches/${matchId}/clips`);
  return r.ok ? r : ok(mockClips.filter((c) => c.matchId === matchId) as Clip[]);
}

export async function apiCreateClip(
  matchId: number,
  payload: Partial<Clip>,
): Promise<ApiResult<Clip>> {
  if (USE_MOCKS) return ok({ ...mockClips[0], ...payload, matchId } as Clip);
  return req<Clip>(`/matches/${matchId}/clips`, { method: "POST", body: payload });
}

export async function apiGetPlayerClips(playerId: number): Promise<ApiResult<Clip[]>> {
  if (USE_MOCKS) return ok(mockClips.filter((c) => c.playerId === playerId) as Clip[]);
  const r = await req<{ items: Clip[] }>(`/players/${playerId}/clips`);
  return r.ok ? ok(r.data.items) : ok(mockClips.filter((c) => c.playerId === playerId) as Clip[]);
}

// ── Reports ───────────────────────────────────────────────────────────────────

export async function apiGetReports(): Promise<ApiResult<Report[]>> {
  if (USE_MOCKS) return ok(mockReports as Report[]);
  const r = await req<Report[]>("/reports");
  return r.ok ? r : ok(mockReports as Report[]);
}

export async function apiGetReportById(reportId: number): Promise<ApiResult<Report>> {
  if (USE_MOCKS) {
    const rep = mockReports.find((r) => r.id === reportId);
    return rep ? ok(rep as Report) : { ok: false, data: null, error: { status: 404, message: "Rapor bulunamadı" } };
  }
  const r = await req<Report>(`/reports/${reportId}`);
  if (r.ok) return r;
  const fallback = mockReports.find((x) => x.id === reportId);
  return fallback ? ok(fallback as Report) : r;
}

export async function apiGetMatchReport(matchId: number): Promise<ApiResult<Report>> {
  if (USE_MOCKS) {
    const rep = mockReports.find((r) => r.matchId === matchId);
    return rep ? ok(rep as Report) : { ok: false, data: null, error: { status: 404, message: "Rapor bulunamadı" } };
  }
  const r = await req<Report>(`/matches/${matchId}/report`);
  if (r.ok) return r;
  const fallback = mockReports.find((x) => x.matchId === matchId);
  return fallback ? ok(fallback as Report) : r;
}

export async function apiCreateMatchReport(matchId: number): Promise<ApiResult<Report>> {
  if (USE_MOCKS) return ok(mockReports[0] as Report);
  return req<Report>(`/matches/${matchId}/report`, { method: "POST" });
}

export async function apiExportReportPdf(reportId: number): Promise<ApiResult<{ pdf_path: string }>> {
  if (USE_MOCKS) return ok({ pdf_path: `reports/${reportId}.pdf` });
  const r = await req<{ data: { pdf_path: string } }>(`/reports/${reportId}/export-pdf`, { method: "POST" });
  return r.ok ? ok(r.data.data) : { ok: false, data: null, error: r.error };
}

// ── Players ───────────────────────────────────────────────────────────────────

export async function apiGetPlayers(orgId?: number): Promise<ApiResult<Player[]>> {
  if (USE_MOCKS) return ok(mockPlayers as Player[]);
  const r = await req<Player[]>("/players");
  return r.ok ? r : ok(mockPlayers as Player[]);
}

export async function apiGetPlayerById(playerId: number): Promise<ApiResult<Player>> {
  if (USE_MOCKS) {
    const p = mockPlayers.find((x) => x.id === playerId);
    return p ? ok(p as Player) : { ok: false, data: null, error: { status: 404, message: "Oyuncu bulunamadı" } };
  }
  const r = await req<Player>(`/players/${playerId}`);
  if (r.ok) return r;
  const fallback = mockPlayers.find((x) => x.id === playerId);
  return fallback ? ok(fallback as Player) : r;
}

export type PlayerPassport = {
  player_id: number;
  first_name: string;
  last_name: string;
  birth_date: string;
  position: string;
  dominant_foot: string;
  height_cm?: number;
  weight_kg?: number;
  photo_url?: string;
  team_name: string;
  technical_score?: number;
  tactical_score?: number;
  physical_score?: number;
  decision_score?: number;
  development_velocity?: number;
  matches_played: number;
  average_max_speed: number;
  average_speed: number;
  total_positive_actions: number;
  total_alerts_involved: number;
  trend_data: { x: string; technical: number; tactical: number; physical: number; decision: number }[];
  tactical_profile: { group: string; metrics: { label: string; value: number }[] };
};

function buildPassportMock(playerId: number): PlayerPassport | null {
  const player = mockPlayers.find((p) => p.id === playerId);
  if (!player) return null;
  const perfs = mockPerformances.filter((x) => x.playerId === playerId);
  const n = perfs.length || 1;
  const team = mockTeams.find((t) => t.id === player.teamId);
  const trend = Array.from({ length: 8 }, (_, i) => {
    const d = (i - 3.5) * 0.04;
    return {
      x: `H${i + 1}`,
      technical: +Math.min(10, Math.max(1, (player.technicalScore ?? 5) + d)).toFixed(1),
      tactical:  +Math.min(10, Math.max(1, (player.tacticalScore  ?? 5) + d * 0.8)).toFixed(1),
      physical:  +Math.min(10, Math.max(1, (player.physicalScore  ?? 5) + d * 0.6)).toFixed(1),
      decision:  +Math.min(10, Math.max(1, (player.decisionScore  ?? 5) + d * 0.9)).toFixed(1),
    };
  });
  return {
    player_id: player.id,
    first_name: player.firstName,
    last_name: player.lastName,
    birth_date: player.birthDate,
    position: player.position,
    dominant_foot: player.dominantFoot,
    height_cm: player.heightCm,
    weight_kg: player.weightKg,
    photo_url: player.photoUrl,
    team_name: team?.name ?? "—",
    technical_score: player.technicalScore,
    tactical_score: player.tacticalScore,
    physical_score: player.physicalScore,
    decision_score: player.decisionScore,
    development_velocity: player.developmentVelocity,
    matches_played: perfs.length,
    average_max_speed: +(perfs.reduce((s, p) => s + (p.maxSpeed ?? 0), 0) / n).toFixed(1),
    average_speed:     +(perfs.reduce((s, p) => s + (p.averageSpeed ?? 0), 0) / n).toFixed(1),
    total_positive_actions: perfs.reduce((s, p) => s + (p.positiveActions ?? 0), 0),
    total_alerts_involved:  perfs.reduce((s, p) => s + (p.alertsInvolved ?? 0), 0),
    trend_data: trend,
    tactical_profile: { group: "Genel", metrics: [
      { label: "Teknik",   value: player.technicalScore ?? 5 },
      { label: "Taktik",   value: player.tacticalScore  ?? 5 },
      { label: "Fiziksel", value: player.physicalScore  ?? 5 },
      { label: "Karar",    value: player.decisionScore  ?? 5 },
    ]},
  };
}

export async function apiGetPlayerPassport(playerId: number): Promise<ApiResult<PlayerPassport>> {
  if (USE_MOCKS) {
    const p = buildPassportMock(playerId);
    return p ? ok(p) : { ok: false, data: null, error: { status: 404, message: "Oyuncu bulunamadı" } };
  }
  const r = await req<PlayerPassport>(`/players/${playerId}/passport`);
  if (r.ok) return r;
  const fallback = buildPassportMock(playerId);
  return fallback ? ok(fallback) : r;
}

export async function apiGetPlayerPerformances(playerId: number): Promise<ApiResult<typeof mockPerformances>> {
  if (USE_MOCKS) return ok(mockPerformances.filter((x) => x.playerId === playerId));
  const r = await req<{ items: typeof mockPerformances }>(`/players/${playerId}/performances`);
  return r.ok ? ok(r.data.items) : ok(mockPerformances.filter((x) => x.playerId === playerId));
}

// ── Scouting ──────────────────────────────────────────────────────────────────

export async function apiGetScoutingPlayers(teamId?: number): Promise<ApiResult<Player[]>> {
  if (USE_MOCKS) return ok(mockPlayers as Player[]);
  const params = new URLSearchParams();
  if (teamId) params.append("team_id", teamId.toString());
  const r = await req<Player[]>(`/scouting/players${params.toString() ? `?${params.toString()}` : ""}`);
  return r.ok ? r : ok(mockPlayers as Player[]);
}

export async function apiGetScoutingNotes(playerId: number): Promise<ApiResult<ScoutNote[]>> {
  if (USE_MOCKS) return ok(mockScoutingNotes.filter(n => n.playerId === playerId) as ScoutNote[]);
  const r = await req<ScoutNote[]>(`/scouting/players/${playerId}/notes`);
  return r.ok ? r : ok(mockScoutingNotes.filter(n => n.playerId === playerId) as ScoutNote[]);
}

export async function apiCreateScoutNote(
  playerId: number,
  note: string,
  rating?: number,
  tagsJson?: string[]
): Promise<ApiResult<ScoutNote>> {
  if (USE_MOCKS) return ok({ id: Date.now(), playerId, scoutId: 1, note, rating, tagsJson: tagsJson || [], createdAt: new Date().toISOString() } as ScoutNote);
  return req<ScoutNote>(`/scouting/players/${playerId}/notes`, {
    method: "POST",
    body: { note, rating, tags_json: tagsJson }
  });
}

export async function apiGetHiddenGems(minVelocity: number = 0.5): Promise<ApiResult<Player[]>> {
  if (USE_MOCKS) return ok(mockPlayers.filter(p => (p.developmentVelocity ?? 0) > minVelocity) as Player[]);
  const r = await req<Player[]>(`/scouting/hidden-gems?min_velocity=${minVelocity}`);
  return r.ok ? r : ok(mockPlayers.filter(p => (p.developmentVelocity ?? 0) > minVelocity) as Player[]);
}

export async function apiGetScoutingStats(teamId?: number): Promise<ApiResult<any>> {
  if (USE_MOCKS) return ok({
    total_players: mockPlayers.length,
    high_potential: mockPlayers.filter(p => (p.developmentVelocity ?? 0) > 1.0).length,
    high_velocity: mockPlayers.filter(p => (p.developmentVelocity ?? 0) > 0.5).length,
    average_velocity: mockPlayers.reduce((s, p) => s + (p.developmentVelocity ?? 0), 0) / mockPlayers.length,
  });
  const params = new URLSearchParams();
  if (teamId) params.append("team_id", teamId.toString());
  const r = await req<any>(`/scouting/stats${params.toString() ? `?${params.toString()}` : ""}`);
  return r.ok ? r : ok({});
}

// ── Drills ────────────────────────────────────────────────────────────────────

export async function apiGetDrills(
  alertType?: string,
  problemType?: string,
  difficulty?: string
): Promise<ApiResult<DrillRecommendation[]>> {
  if (USE_MOCKS) return ok(mockDrills as DrillRecommendation[]);
  
  const params = new URLSearchParams();
  if (alertType) params.append("alert_type", alertType);
  if (problemType) params.append("problem_type", problemType);
  if (difficulty) params.append("difficulty", difficulty);
  
  const r = await req<DrillRecommendation[]>(`/drills${params.toString() ? `?${params.toString()}` : ""}`);
  return r.ok ? r : ok(mockDrills as DrillRecommendation[]);
}

export async function apiGetDrill(drillId: number): Promise<ApiResult<DrillRecommendation>> {
  if (USE_MOCKS) {
    const d = mockDrills.find(x => x.id === drillId);
    return d ? ok(d as DrillRecommendation) : { ok: false, data: null, error: { status: 404, message: "Antrenman bulunamadı" } };
  }
  const r = await req<DrillRecommendation>(`/drills/${drillId}`);
  return r.ok ? r : ok(mockDrills[0] as DrillRecommendation);
}

export async function apiGetMatchDrills(matchId: number): Promise<ApiResult<DrillRecommendation[]>> {
  if (USE_MOCKS) {
    const alertTypes = new Set(mockAlerts.filter((a) => a.matchId === matchId).map((a) => a.alertType as string));
    const relevant = mockDrills.filter((d) => alertTypes.has(d.alertType as string));
    return ok((relevant.length ? relevant : mockDrills.slice(0, 3)) as DrillRecommendation[]);
  }
  const r = await req<DrillRecommendation[]>(`/drills/match/${matchId}`);
  return r.ok ? r : ok(mockDrills.slice(0, 3) as DrillRecommendation[]);
}

export async function apiGetDrillsByDifficulty(difficulty: string): Promise<ApiResult<DrillRecommendation[]>> {
  if (USE_MOCKS) return ok(mockDrills.filter(d => d.difficulty === difficulty) as DrillRecommendation[]);
  const r = await req<DrillRecommendation[]>(`/drills/difficulty/${difficulty}`);
  return r.ok ? r : ok(mockDrills as DrillRecommendation[]);
}

export async function apiGetDrillsByDuration(durationMinutes: number, tolerance: number = 5): Promise<ApiResult<DrillRecommendation[]>> {
  if (USE_MOCKS) return ok(mockDrills as DrillRecommendation[]);
  const r = await req<DrillRecommendation[]>(`/drills/duration/${durationMinutes}?tolerance=${tolerance}`);
  return r.ok ? r : ok(mockDrills as DrillRecommendation[]);
}

export async function apiGetDrillsStats(): Promise<ApiResult<any>> {
  if (USE_MOCKS) return ok({
    total_drills: mockDrills.length,
    by_difficulty: {
      easy: mockDrills.filter(d => d.difficulty === "easy").length,
      medium: mockDrills.filter(d => d.difficulty === "medium").length,
      hard: mockDrills.filter(d => d.difficulty === "hard").length,
    },
    average_duration: mockDrills.reduce((s, d) => s + (d.durationMinutes || 0), 0) / mockDrills.length,
  });
  const r = await req<any>(`/drills/stats`);
  return r.ok ? r : ok({});
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

export type DashboardData = {
  total_matches: number;
  completed_matches: number;
  total_players: number;
  total_alerts: number;
  recent_matches: Match[];
  top_players: Player[];
  team_metrics: typeof DEMO_TEAM_METRICS;
};

export async function apiGetDashboard(orgId?: number): Promise<ApiResult<DashboardData>> {
  if (USE_MOCKS) {
    return ok({
      total_matches:     mockMatches.length,
      completed_matches: mockMatches.filter((m) => m.status === "completed").length,
      total_players:     mockPlayers.length,
      total_alerts:      mockAlerts.length,
      recent_matches:    mockMatches.slice(0, 3) as Match[],
      top_players:       [...mockPlayers].sort((a, b) => (b.developmentVelocity ?? 0) - (a.developmentVelocity ?? 0)).slice(0, 3) as Player[],
      team_metrics:      DEMO_TEAM_METRICS,
    });
  }
  // Backend'de dedicated dashboard endpoint yoksa parçaları birleştir
  const [matchesR, playersR] = await Promise.all([
    req<Match[]>("/matches"),
    req<Player[]>("/players"),
  ]);
  const matches = matchesR.ok ? matchesR.data : (mockMatches as Match[]);
  const players = playersR.ok ? playersR.data : (mockPlayers as Player[]);
  return ok({
    total_matches:     matches.length,
    completed_matches: matches.filter((m) => m.status === "completed").length,
    total_players:     players.length,
    total_alerts:      mockAlerts.length,
    recent_matches:    matches.slice(0, 3),
    top_players:       [...players].sort((a, b) => (b.developmentVelocity ?? 0) - (a.developmentVelocity ?? 0)).slice(0, 3),
    team_metrics:      DEMO_TEAM_METRICS,
  });
}

// ── Settings ──────────────────────────────────────────────────────────────────
// Settings fonksiyonları apiSettings.ts'de tanımlıdır.
// Mevcut import'ları kırmamak için buradan re-export edilir.
export type {
  OrganizationSettingsDto,
  SettingsUserDto,
  SettingsTeamDto,
  SeasonDto,
  VideoProcessingDto,
  NotificationSettingsDto,
  PrivacySettingsDto,
  DroneChecklistDto,
  SubscriptionDto,
} from "@/lib/apiSettings";

export {
  apiGetSettingsOrganization,
  apiPutSettingsOrganization,
  apiGetSettingsUsers,
  apiInviteSettingsUser,
  apiUpdateSettingsUserRole,
  apiDeactivateSettingsUser,
  apiGetSettingsTeams,
  apiCreateSettingsTeam,
  apiGetSettingsSeasons,
  apiActivateSettingsSeason,
  apiGetVideoProcessing,
  apiPutVideoProcessing,
  apiGetNotificationSettings,
  apiPutNotificationSettings,
  apiGetPrivacySettings,
  apiPutPrivacySettings,
  apiGetDroneChecklist,
  apiPutDroneChecklist,
  apiGetSubscription,
  apiPostSettingsDataExport,
  apiPostSettingsDataAnonymize,
  apiPostSettingsDataDeleteRequest,
} from "@/lib/apiSettings";

// ── Demo request ──────────────────────────────────────────────────────────────

export type DemoRequestPayload = {
  full_name: string;
  club_name: string;
  role: string;
  email: string;
  phone: string;
  age_categories: string;
  interest_module: string;
  notes: string;
  plan_interest?: string | null;
  intent?: string | null;
};

export async function apiPostDemoRequest(
  body: DemoRequestPayload,
): Promise<ApiResult<{ status: string; reference?: string }>> {
  const r = await req<{ status: string; reference?: string }>("/demo-requests", { method: "POST", body });
  return r.ok ? r : ok({ status: "received", reference: "DEMO-LOCAL" });
}
