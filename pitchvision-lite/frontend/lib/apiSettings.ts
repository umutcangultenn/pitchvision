/**
 * Settings API — organizasyon, kullanıcı, takım, sezon, video işleme,
 * bildirimler, gizlilik, drone checklist, abonelik.
 */

import { mockOrganizations, mockTeams } from "@/data/demo";

const BASE =
  typeof process.env.NEXT_PUBLIC_API_URL === "string"
    ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "")
    : "http://localhost:8000";

const API_V1 = "/api/v1";

function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${BASE}${API_V1}${p}`;
}

const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS !== "false";

async function req<T>(path: string, options?: RequestInit & { body?: unknown }): Promise<T | null> {
  if (USE_MOCKS) return null;
  try {
    const hasBody = options?.body !== undefined;
    const res = await fetch(apiUrl(path), {
      ...options,
      headers: { ...(hasBody ? { "Content-Type": "application/json" } : {}), ...options?.headers },
      body: hasBody ? JSON.stringify(options!.body) : undefined,
      cache: "no-store",
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch { return null; }
}

// ── DTOs ──────────────────────────────────────────────────────────────────────

export type OrganizationSettingsDto = {
  id: number; name: string; city: string; logo_url: string | null;
  organization_type: string; contact_email: string | null;
  contact_phone: string | null; website: string | null;
};

export type SettingsUserDto = {
  id: number; email: string; full_name: string; role: string;
  is_active: boolean; created_at: string | null;
};

export type SettingsTeamDto = {
  id: number; name: string; age_category: string; game_format: string;
  default_formation: string; pitch_length: number; pitch_width: number;
  season: string; is_active: boolean;
};

export type SeasonDto = {
  id: number; name: string; start_date: string; end_date: string;
  is_active: boolean; teams_count: number;
};

export type VideoProcessingDto = {
  default_pitch_size: string; default_game_format: string;
  detection_confidence_threshold: number; alert_threshold_value: number;
  default_clip_duration: number;
};

export type NotificationSettingsDto = {
  notify_analysis_complete: boolean; notify_errors: boolean;
  notify_new_report: boolean; notify_scout_note: boolean;
  notify_player_development: boolean;
};

export type PrivacySettingsDto = {
  anonymize_player_data: boolean; gdpr_enabled: boolean;
  parental_consent_required: boolean; u8_u17_data_security_enabled: boolean;
};

export type DroneChecklistDto = {
  flight_permission_checked: boolean; pitch_safety_secured: boolean;
  parent_player_consents_checked: boolean; camera_angle_ok: boolean;
  pitch_lines_visible: boolean; wind_weather_ok: boolean;
};

export type SubscriptionDto = {
  plan_name: string; billing_cycle: string; next_renewal: string;
  seats_used: number; seats_limit: number; status: string;
};

// ── Mock defaults ─────────────────────────────────────────────────────────────

const MOCK_ORG: OrganizationSettingsDto = {
  id: mockOrganizations[0].id,
  name: mockOrganizations[0].name,
  city: mockOrganizations[0].city,
  logo_url: null,
  organization_type: mockOrganizations[0].organizationType,
  contact_email: "iletisim@anadolu-akademi.demo",
  contact_phone: "+90 212 000 00 00",
  website: "https://anadolu-akademi.demo",
};

const MOCK_USERS: SettingsUserDto[] = [
  { id: 1, email: "coach@anadolu-akademi.demo", full_name: "Mehmet Antrenör", role: "coach",  is_active: true, created_at: "2025-09-01T10:00:00Z" },
  { id: 2, email: "scout@anadolu-akademi.demo", full_name: "Selin Gözlemci",  role: "scout",  is_active: true, created_at: "2025-09-02T10:00:00Z" },
];

const MOCK_TEAMS: SettingsTeamDto[] = mockTeams.map((t) => ({
  id: t.id, name: t.name, age_category: t.ageCategory, game_format: t.gameFormat,
  default_formation: t.defaultFormation, pitch_length: t.pitchLength,
  pitch_width: t.pitchWidth, season: t.season, is_active: true,
}));

const MOCK_SEASONS: SeasonDto[] = [
  { id: 1, name: "2025/26", start_date: "2025-07-01", end_date: "2026-06-15", is_active: true,  teams_count: 4 },
  { id: 2, name: "2024/25", start_date: "2024-07-01", end_date: "2025-06-15", is_active: false, teams_count: 0 },
];

const MOCK_VIDEO: VideoProcessingDto = {
  default_pitch_size: "105x68m", default_game_format: "11v11",
  detection_confidence_threshold: 0.72, alert_threshold_value: 0.55,
  default_clip_duration: 12,
};

const MOCK_NOTIF: NotificationSettingsDto = {
  notify_analysis_complete: true, notify_errors: true,
  notify_new_report: true, notify_scout_note: true, notify_player_development: true,
};

const MOCK_PRIVACY: PrivacySettingsDto = {
  anonymize_player_data: false, gdpr_enabled: true,
  parental_consent_required: true, u8_u17_data_security_enabled: true,
};

const MOCK_DRONE: DroneChecklistDto = {
  flight_permission_checked: false, pitch_safety_secured: false,
  parent_player_consents_checked: false, camera_angle_ok: false,
  pitch_lines_visible: false, wind_weather_ok: false,
};

const MOCK_SUB: SubscriptionDto = {
  plan_name: "Academy", billing_cycle: "Yıllık", next_renewal: "2027-01-15",
  seats_used: 6, seats_limit: 12, status: "active",
};

// ── Exports ───────────────────────────────────────────────────────────────────

export async function apiGetSettingsOrganization(): Promise<OrganizationSettingsDto> {
  return (await req<OrganizationSettingsDto>("/settings/organization")) ?? MOCK_ORG;
}
export async function apiPutSettingsOrganization(body: Omit<OrganizationSettingsDto, "id">): Promise<OrganizationSettingsDto | null> {
  return req<OrganizationSettingsDto>("/settings/organization", { method: "PUT", body });
}
export async function apiGetSettingsUsers(): Promise<SettingsUserDto[]> {
  return (await req<SettingsUserDto[]>("/settings/users")) ?? MOCK_USERS;
}
export async function apiInviteSettingsUser(body: { email: string; full_name: string; role: string }): Promise<{ status: string } | null> {
  return req("/settings/users/invite", { method: "POST", body });
}
export async function apiUpdateSettingsUserRole(userId: number, role: string): Promise<SettingsUserDto | null> {
  return req<SettingsUserDto>(`/settings/users/${userId}/role?role=${encodeURIComponent(role)}`, { method: "PUT" });
}
export async function apiDeactivateSettingsUser(userId: number): Promise<SettingsUserDto | null> {
  return req<SettingsUserDto>(`/settings/users/${userId}/deactivate`, { method: "PATCH" });
}
export async function apiGetSettingsTeams(): Promise<SettingsTeamDto[]> {
  return (await req<SettingsTeamDto[]>("/settings/teams")) ?? MOCK_TEAMS;
}
export async function apiCreateSettingsTeam(body: Omit<SettingsTeamDto, "id" | "is_active">): Promise<SettingsTeamDto | null> {
  return req<SettingsTeamDto>("/settings/teams", { method: "POST", body });
}
export async function apiGetSettingsSeasons(): Promise<SeasonDto[]> {
  return (await req<SeasonDto[]>("/settings/seasons")) ?? MOCK_SEASONS;
}
export async function apiActivateSettingsSeason(seasonId: number): Promise<SeasonDto | null> {
  return req<SeasonDto>(`/settings/seasons/${seasonId}/activate`, { method: "PUT" });
}
export async function apiGetVideoProcessing(): Promise<VideoProcessingDto> {
  return (await req<VideoProcessingDto>("/settings/video-processing")) ?? MOCK_VIDEO;
}
export async function apiPutVideoProcessing(body: VideoProcessingDto): Promise<VideoProcessingDto | null> {
  return req<VideoProcessingDto>("/settings/video-processing", { method: "PUT", body });
}
export async function apiGetNotificationSettings(): Promise<NotificationSettingsDto> {
  return (await req<NotificationSettingsDto>("/settings/notifications")) ?? MOCK_NOTIF;
}
export async function apiPutNotificationSettings(body: NotificationSettingsDto): Promise<NotificationSettingsDto | null> {
  return req<NotificationSettingsDto>("/settings/notifications", { method: "PUT", body });
}
export async function apiGetPrivacySettings(): Promise<PrivacySettingsDto> {
  return (await req<PrivacySettingsDto>("/settings/privacy")) ?? MOCK_PRIVACY;
}
export async function apiPutPrivacySettings(body: PrivacySettingsDto): Promise<PrivacySettingsDto | null> {
  return req<PrivacySettingsDto>("/settings/privacy", { method: "PUT", body });
}
export async function apiGetDroneChecklist(): Promise<DroneChecklistDto> {
  return (await req<DroneChecklistDto>("/settings/drone-checklist")) ?? MOCK_DRONE;
}
export async function apiPutDroneChecklist(body: DroneChecklistDto): Promise<DroneChecklistDto | null> {
  return req<DroneChecklistDto>("/settings/drone-checklist", { method: "PUT", body });
}
export async function apiGetSubscription(): Promise<SubscriptionDto> {
  return (await req<SubscriptionDto>("/settings/subscription")) ?? MOCK_SUB;
}
export async function apiPostSettingsDataExport(): Promise<{ status: string } | null> {
  return req("/settings/data/export", { method: "POST" });
}
export async function apiPostSettingsDataAnonymize(playerId: number): Promise<{ status: string } | null> {
  return req(`/settings/data/anonymize?player_id=${playerId}`, { method: "POST" });
}
export async function apiPostSettingsDataDeleteRequest(playerId: number): Promise<{ status: string } | null> {
  return req(`/settings/data/delete-request?player_id=${playerId}`, { method: "POST" });
}
