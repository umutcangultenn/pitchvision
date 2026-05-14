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

const API_V1 = "/api/v1";

function apiUrl(path: string): string {
  if (path === "/health") return `${BASE}${path}`;
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${BASE}${API_V1}${p}`;
}

const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS !== "false";

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
  options?: Omit<RequestInit, "body"> & { body?: unknown },
): Promise<ApiResult<T>> {
  try {
    const hasBody = options?.body !== undefined;
    const res = await fetch(apiUrl(path), {
      ...options,
      headers: {
        ...(hasBody ? { "Content-Type": "application/json" } : {}),
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

// ── Matches ───────────────────────────────────────────────────────────────────

export async function apiGetMatches(orgId?: number): Promise<ApiResult<Match[]>> {
  if (USE_MOCKS) return ok(mockMatches as Match[]);
  const r = await req<Match[]>("/matches");
  return r.ok ? r : ok(mockMatches as Match[]);
}

export async function apiGetMatchById(matchId: number): Promise<ApiResult<Match>> {
  if (USE_MOCKS) {
    const m = mockMatches.find((x) => x.id === matchId);
    return m ? ok(m as Match) : { ok: false, data: null, error: { status: 404, message: "Maç bulunamadı" } };
  }
  const r = await req<Match>(`/matches/${matchId}`);
  if (r.ok) return r;
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

// ── Alerts ────────────────────────────────────────────────────────────────────

export async function apiGetAlerts(matchId: number): Promise<ApiResult<TacticalAlert[]>> {
  if (USE_MOCKS) return ok(mockAlerts.filter((a) => a.matchId === matchId) as TacticalAlert[]);
  const r = await req<TacticalAlert[]>(`/matches/${matchId}/alerts`);
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

export async function apiGetScoutingPlayers(): Promise<ApiResult<Player[]>> {
  if (USE_MOCKS) return ok([...mockPlayers].sort((a, b) => (b.developmentVelocity ?? 0) - (a.developmentVelocity ?? 0)) as Player[]);
  const r = await req<Player[]>("/scouting/players");
  return r.ok ? r : ok(mockPlayers as Player[]);
}

export async function apiGetHiddenGems(): Promise<ApiResult<Player[]>> {
  if (USE_MOCKS) return ok(mockPlayers.filter((p) => (p.developmentVelocity ?? 0) > 0.5) as Player[]);
  const r = await req<Player[]>("/scouting/hidden-gems");
  return r.ok ? r : ok(mockPlayers.filter((p) => (p.developmentVelocity ?? 0) > 0.5) as Player[]);
}

export async function apiGetScoutNotes(playerId: number): Promise<ApiResult<ScoutNote[]>> {
  if (USE_MOCKS) return ok(mockScoutingNotes.filter((n) => n.playerId === playerId) as ScoutNote[]);
  const r = await req<ScoutNote[]>(`/scouting/players/${playerId}/scout-notes`);
  return r.ok ? r : ok(mockScoutingNotes.filter((n) => n.playerId === playerId) as ScoutNote[]);
}

export async function apiCreateScoutNote(payload: {
  player_id: number;
  scout_id: number;
  note: string;
  rating?: number;
  tags_json?: Record<string, unknown>;
}): Promise<ApiResult<ScoutNote>> {
  if (USE_MOCKS) return ok({ id: Date.now(), playerId: payload.player_id, scoutId: payload.scout_id, note: payload.note, rating: payload.rating, tagsJson: [], createdAt: new Date().toISOString() } as ScoutNote);
  return req<ScoutNote>("/scouting/notes", { method: "POST", body: payload });
}

// ── Drills ────────────────────────────────────────────────────────────────────

export async function apiGetDrills(): Promise<ApiResult<DrillRecommendation[]>> {
  if (USE_MOCKS) return ok(mockDrills as DrillRecommendation[]);
  const r = await req<DrillRecommendation[]>("/drills");
  return r.ok ? r : ok(mockDrills as DrillRecommendation[]);
}

export async function apiGetMatchDrills(matchId: number): Promise<ApiResult<DrillRecommendation[]>> {
  if (USE_MOCKS) {
    const alertTypes = new Set(mockAlerts.filter((a) => a.matchId === matchId).map((a) => a.alertType as string));
    const relevant = mockDrills.filter((d) => alertTypes.has(d.alertType as string));
    return ok((relevant.length ? relevant : mockDrills.slice(0, 3)) as DrillRecommendation[]);
  }
  const r = await req<DrillRecommendation[]>(`/matches/${matchId}/drills`);
  return r.ok ? r : ok(mockDrills.slice(0, 3) as DrillRecommendation[]);
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
