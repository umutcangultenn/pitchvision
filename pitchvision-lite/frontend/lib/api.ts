const apiBase =
  typeof process.env.NEXT_PUBLIC_API_URL === "string"
    ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")
    : "";

export async function fetchHealth(): Promise<{ status?: string } | null> {
  if (!apiBase) return null;
  try {
    const res = await fetch(`${apiBase}/health`, { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as { status?: string };
  } catch {
    return null;
  }
}

async function apiReq<T>(
  path: string,
  options?: { method?: string; body?: unknown }
): Promise<T | null> {
  if (!apiBase) return null;
  try {
    const method = options?.method ?? "GET";
    const hasBody = options?.body !== undefined;
    const res = await fetch(`${apiBase}${path}`, {
      method,
      headers: hasBody ? { "Content-Type": "application/json" } : undefined,
      body: hasBody ? JSON.stringify(options.body) : undefined,
      cache: "no-store",
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

// Mock-first API facade (backend bağlanınca sadece bu dosyayı güncelleyeceğiz).
import {
  mockAlerts,
  mockClips,
  mockDrills,
  mockMatches,
  mockMetrics,
  mockPerformances,
  mockPlayers,
  mockReports,
  mockScoutingNotes,
  mockVideos,
} from "@/data/demo";
import type { Clip, DrillRecommendation, Match, Player, Report, VideoAsset } from "@/types/domain";

export async function apiGetMatches(): Promise<Match[]> {
  return mockMatches;
}

export async function apiGetMatchById(matchId: number): Promise<Match | undefined> {
  return mockMatches.find((m) => m.id === matchId);
}

export async function apiGetPlayers(): Promise<Player[]> {
  return mockPlayers;
}

export async function apiGetPlayerById(playerId: number): Promise<Player | undefined> {
  return mockPlayers.find((p) => p.id === playerId);
}

export async function apiGetPlayerPassport(playerId: number): Promise<any> {
  // Passport data with trends and tactical profile
  const player = mockPlayers.find((p) => p.id === playerId);
  if (!player) return null;

  const performances = mockPerformances.filter((x) => x.playerId === playerId);
  const matches_played = performances.length;
  const average_max_speed =
    matches_played > 0
      ? +(
          performances.reduce((s, p) => s + (p.maxSpeed ?? 0), 0) / matches_played
        ).toFixed(1)
      : 0;
  const average_speed =
    matches_played > 0
      ? +(
          performances.reduce((s, p) => s + (p.averageSpeed ?? 0), 0) / matches_played
        ).toFixed(1)
      : 0;
  const total_positive_actions = performances.reduce(
    (s, p) => s + (p.positiveActions ?? 0),
    0
  );
  const total_alerts_involved = performances.reduce(
    (s, p) => s + (p.alertsInvolved ?? 0),
    0
  );

  // Build trend data
  const trend_data = [];
  const base = {
    technical: player.technicalScore ?? 5,
    tactical: player.tacticalScore ?? 5,
    physical: player.physicalScore ?? 5,
    decision: player.decisionScore ?? 5,
  };
  for (let week = 1; week <= 8; week++) {
    const d = (week - 4.5) * 0.04;
    trend_data.push({
      x: `H${week}`,
      technical: +Math.min(10, Math.max(1, base.technical + d)).toFixed(1),
      tactical: +Math.min(10, Math.max(1, base.tactical + d * 0.8)).toFixed(1),
      physical: +Math.min(10, Math.max(1, base.physical + d * 0.6)).toFixed(1),
      decision: +Math.min(10, Math.max(1, base.decision + d * 0.9)).toFixed(1),
    });
  }

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
    team_name: "U15 Kırmızı Takım",
    technical_score: player.technicalScore,
    tactical_score: player.tacticalScore,
    physical_score: player.physicalScore,
    decision_score: player.decisionScore,
    development_velocity: player.developmentVelocity,
    matches_played,
    average_max_speed,
    average_speed,
    total_positive_actions,
    total_alerts_involved,
    trend_data,
    tactical_profile: {
      group: "Genel",
      metrics: [
        { label: "Teknik", value: player.technicalScore ?? 5 },
        { label: "Taktik", value: player.tacticalScore ?? 5 },
        { label: "Fiziksel", value: player.physicalScore ?? 5 },
        { label: "Karar", value: player.decisionScore ?? 5 },
      ],
    },
  };
}

export async function apiGetReports(): Promise<Report[]> {
  return mockReports;
}

export async function apiGetReportById(reportId: number): Promise<Report | undefined> {
  return mockReports.find((r) => r.id === reportId);
}

export async function apiGetMatchAlerts(matchId: number): Promise<typeof mockAlerts> {
  return mockAlerts.filter((a) => a.matchId === matchId) as any;
}

export async function apiGetMatchClips(matchId: number): Promise<typeof mockClips> {
  return (mockClips as any).filter((c: Clip) => c.matchId === matchId);
}

export async function apiGetMatchMetrics(matchId: number): Promise<typeof mockMetrics> {
  return mockMetrics.filter((m) => m.matchId === matchId) as any;
}

export async function apiGetMatchVideo(matchId: number): Promise<VideoAsset | undefined> {
  return mockVideos.find((v) => v.matchId === matchId);
}

export async function apiGetDrills(): Promise<DrillRecommendation[]> {
  return mockDrills;
}

export async function apiGetMatchDrills(matchId: number): Promise<DrillRecommendation[]> {
  // Return drills related to a specific match
  // In real backend: GET /matches/{matchId}/drill-recommendations
  return mockDrills.slice(0, 3);
}

export async function apiMarkDrillApplied(drillId: number): Promise<{ status: string }> {
  // Mark a drill as applied/implemented
  // In real backend: POST /drills/{drillId}/mark-applied
  return { status: "success" };
}

export async function apiGetScoutingPlayers(): Promise<Player[]> {
  return mockPlayers.slice().sort((a, b) => (b.developmentVelocity ?? 0) - (a.developmentVelocity ?? 0));
}

export async function apiGetHiddenGems(): Promise<Player[]> {
  return mockPlayers.filter((p) => (p.developmentVelocity ?? 0) > 0.5);
}

export async function apiGetPlayerScoutingNotes(playerId: number): Promise<typeof mockScoutingNotes> {
  return mockScoutingNotes.filter((n) => n.playerId === playerId) as any;
}

export async function apiUploadMatchVideo(): Promise<void> {
  // MVP: mock only.
  return;
}

export async function apiCreateMockReport(): Promise<void> {
  return;
}

// --- Ayarlar / organizasyon (backend şemasıyla uyumlu alan adları) ---

export type OrganizationSettingsDto = {
  id: number;
  name: string;
  city: string;
  logo_url: string | null;
  organization_type: string;
  contact_email: string | null;
  contact_phone: string | null;
  website: string | null;
};

export type SettingsUserDto = {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string | null;
};

export type SettingsTeamDto = {
  id: number;
  name: string;
  age_category: string;
  game_format: string;
  default_formation: string;
  pitch_length: number;
  pitch_width: number;
  season: string;
  is_active: boolean;
};

export type SeasonDto = {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
  teams_count: number;
};

export type VideoProcessingDto = {
  default_pitch_size: string;
  default_game_format: string;
  detection_confidence_threshold: number;
  alert_threshold_value: number;
  default_clip_duration: number;
};

export type NotificationSettingsDto = {
  notify_analysis_complete: boolean;
  notify_errors: boolean;
  notify_new_report: boolean;
  notify_scout_note: boolean;
  notify_player_development: boolean;
};

export type PrivacySettingsDto = {
  anonymize_player_data: boolean;
  gdpr_enabled: boolean;
  parental_consent_required: boolean;
  u8_u17_data_security_enabled: boolean;
};

export type DroneChecklistDto = {
  flight_permission_checked: boolean;
  pitch_safety_secured: boolean;
  parent_player_consents_checked: boolean;
  camera_angle_ok: boolean;
  pitch_lines_visible: boolean;
  wind_weather_ok: boolean;
};

export type SubscriptionDto = {
  plan_name: string;
  billing_cycle: string;
  next_renewal: string;
  seats_used: number;
  seats_limit: number;
  status: string;
};

const mockOrganization: OrganizationSettingsDto = {
  id: 1,
  name: "Demo Akademi SK",
  city: "İstanbul",
  logo_url: null,
  organization_type: "academy",
  contact_email: "iletisim@demo.pitchvision.local",
  contact_phone: "+90 212 000 00 00",
  website: "https://demo.pitchvision.local",
};

const mockSettingsUsers: SettingsUserDto[] = [
  {
    id: 1,
    email: "admin@demo.pitchvision.local",
    full_name: "Demo Yönetici",
    role: "admin",
    is_active: true,
    created_at: "2025-09-01T10:00:00+00:00",
  },
  {
    id: 2,
    email: "coach@demo.pitchvision.local",
    full_name: "Demo Antrenör",
    role: "coach",
    is_active: true,
    created_at: "2025-09-02T10:00:00+00:00",
  },
  {
    id: 3,
    email: "scout@demo.pitchvision.local",
    full_name: "Demo Scout",
    role: "scout",
    is_active: true,
    created_at: "2025-10-01T10:00:00+00:00",
  },
];

const mockSettingsTeams: SettingsTeamDto[] = [
  {
    id: 1,
    name: "U15 Kırmızı",
    age_category: "U15",
    game_format: "11v11",
    default_formation: "4-3-3",
    pitch_length: 105,
    pitch_width: 68,
    season: "2025-26",
    is_active: true,
  },
  {
    id: 2,
    name: "U17 Beyaz",
    age_category: "U17",
    game_format: "11v11",
    default_formation: "4-2-3-1",
    pitch_length: 100,
    pitch_width: 64,
    season: "2025-26",
    is_active: true,
  },
];

const mockSeasons: SeasonDto[] = [
  {
    id: 1,
    name: "2025-26",
    start_date: "2025-07-01",
    end_date: "2026-06-15",
    is_active: true,
    teams_count: 2,
  },
  {
    id: 2,
    name: "2024-25",
    start_date: "2024-07-01",
    end_date: "2025-06-15",
    is_active: false,
    teams_count: 0,
  },
];

const mockVideo: VideoProcessingDto = {
  default_pitch_size: "105x68m",
  default_game_format: "11v11",
  detection_confidence_threshold: 0.72,
  alert_threshold_value: 0.55,
  default_clip_duration: 12,
};

const mockNotifications: NotificationSettingsDto = {
  notify_analysis_complete: true,
  notify_errors: true,
  notify_new_report: true,
  notify_scout_note: true,
  notify_player_development: true,
};

const mockPrivacy: PrivacySettingsDto = {
  anonymize_player_data: false,
  gdpr_enabled: true,
  parental_consent_required: true,
  u8_u17_data_security_enabled: true,
};

const mockDrone: DroneChecklistDto = {
  flight_permission_checked: false,
  pitch_safety_secured: false,
  parent_player_consents_checked: false,
  camera_angle_ok: false,
  pitch_lines_visible: false,
  wind_weather_ok: false,
};

const mockSubscription: SubscriptionDto = {
  plan_name: "Academy",
  billing_cycle: "Yıllık",
  next_renewal: "2027-01-15",
  seats_used: 6,
  seats_limit: 12,
  status: "active",
};

export async function apiGetSettingsOrganization(): Promise<OrganizationSettingsDto> {
  const remote = await apiReq<OrganizationSettingsDto>("/settings/organization");
  return remote ?? mockOrganization;
}

export async function apiPutSettingsOrganization(
  body: Omit<OrganizationSettingsDto, "id">
): Promise<OrganizationSettingsDto | null> {
  const remote = await apiReq<OrganizationSettingsDto>("/settings/organization", {
    method: "PUT",
    body,
  });
  return remote;
}

export async function apiGetSettingsUsers(): Promise<SettingsUserDto[]> {
  const remote = await apiReq<SettingsUserDto[]>("/settings/users");
  return remote ?? mockSettingsUsers;
}

export async function apiInviteSettingsUser(body: {
  email: string;
  full_name: string;
  role: string;
}): Promise<{ status: string; message?: string } | null> {
  return apiReq("/settings/users/invite", { method: "POST", body });
}

export async function apiUpdateSettingsUserRole(
  userId: number,
  role: string
): Promise<SettingsUserDto | null> {
  return apiReq<SettingsUserDto>(`/settings/users/${userId}/role?role=${encodeURIComponent(role)}`, {
    method: "PUT",
  });
}

export async function apiDeactivateSettingsUser(userId: number): Promise<SettingsUserDto | null> {
  return apiReq<SettingsUserDto>(`/settings/users/${userId}/deactivate`, { method: "PATCH" });
}

export async function apiGetSettingsTeams(): Promise<SettingsTeamDto[]> {
  const remote = await apiReq<SettingsTeamDto[]>("/settings/teams");
  return remote ?? mockSettingsTeams;
}

export async function apiCreateSettingsTeam(body: {
  name: string;
  age_category: string;
  game_format: string;
  default_formation: string;
  pitch_length: number;
  pitch_width: number;
  season?: string | null;
}): Promise<SettingsTeamDto | null> {
  return apiReq<SettingsTeamDto>("/settings/teams", { method: "POST", body });
}

export async function apiGetSettingsSeasons(): Promise<SeasonDto[]> {
  const remote = await apiReq<SeasonDto[]>("/settings/seasons");
  return remote ?? mockSeasons;
}

export async function apiActivateSettingsSeason(seasonId: number): Promise<SeasonDto | null> {
  return apiReq<SeasonDto>(`/settings/seasons/${seasonId}/activate`, { method: "PUT" });
}

export async function apiGetVideoProcessing(): Promise<VideoProcessingDto> {
  const remote = await apiReq<VideoProcessingDto>("/settings/video-processing");
  return remote ?? mockVideo;
}

export async function apiPutVideoProcessing(
  body: VideoProcessingDto
): Promise<VideoProcessingDto | null> {
  return apiReq<VideoProcessingDto>("/settings/video-processing", { method: "PUT", body });
}

export async function apiGetNotificationSettings(): Promise<NotificationSettingsDto> {
  const remote = await apiReq<NotificationSettingsDto>("/settings/notifications");
  return remote ?? mockNotifications;
}

export async function apiPutNotificationSettings(
  body: NotificationSettingsDto
): Promise<NotificationSettingsDto | null> {
  return apiReq<NotificationSettingsDto>("/settings/notifications", { method: "PUT", body });
}

export async function apiGetPrivacySettings(): Promise<PrivacySettingsDto> {
  const remote = await apiReq<PrivacySettingsDto>("/settings/privacy");
  return remote ?? mockPrivacy;
}

export async function apiPutPrivacySettings(
  body: PrivacySettingsDto
): Promise<PrivacySettingsDto | null> {
  return apiReq<PrivacySettingsDto>("/settings/privacy", { method: "PUT", body });
}

export async function apiGetDroneChecklist(): Promise<DroneChecklistDto> {
  const remote = await apiReq<DroneChecklistDto>("/settings/drone-checklist");
  return remote ?? mockDrone;
}

export async function apiPutDroneChecklist(
  body: DroneChecklistDto
): Promise<DroneChecklistDto | null> {
  return apiReq<DroneChecklistDto>("/settings/drone-checklist", { method: "PUT", body });
}

export async function apiGetSubscription(): Promise<SubscriptionDto> {
  const remote = await apiReq<SubscriptionDto>("/settings/subscription");
  return remote ?? mockSubscription;
}

export async function apiPostSettingsDataExport(): Promise<{ status: string; message?: string } | null> {
  return apiReq("/settings/data/export", { method: "POST" });
}

export async function apiPostSettingsDataAnonymize(
  playerId: number
): Promise<{ status: string; message?: string } | null> {
  return apiReq(`/settings/data/anonymize?player_id=${playerId}`, { method: "POST" });
}

export async function apiPostSettingsDataDeleteRequest(
  playerId: number
): Promise<{ status: string; message?: string } | null> {
  return apiReq(`/settings/data/delete-request?player_id=${playerId}`, { method: "POST" });
}

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
  body: DemoRequestPayload
): Promise<{ status: string; reference?: string } | null> {
  const remote = await apiReq<{ status: string; reference?: string }>("/demo-requests", {
    method: "POST",
    body,
  });
  if (remote) return remote;
  return { status: "received", reference: "DEMO-LOCAL" };
}
