"use client";

import Link from "next/link";
import React, { useCallback, useEffect, useState } from "react";
import { Modal } from "@/components/ui/Modal";
import { UploadDropzone } from "@/components/ui/UploadDropzone";
import { mockPlayers } from "@/data/demo";
import type { Player } from "@/types/domain";
import {
  apiActivateSettingsSeason,
  apiCreateSettingsTeam,
  apiDeactivateSettingsUser,
  apiGetDroneChecklist,
  apiGetNotificationSettings,
  apiGetPrivacySettings,
  apiGetSettingsOrganization,
  apiGetSettingsSeasons,
  apiGetSettingsTeams,
  apiGetSettingsUsers,
  apiGetSubscription,
  apiGetVideoProcessing,
  apiInviteSettingsUser,
  apiPostSettingsDataAnonymize,
  apiPostSettingsDataDeleteRequest,
  apiPostSettingsDataExport,
  apiPutDroneChecklist,
  apiPutNotificationSettings,
  apiPutPrivacySettings,
  apiPutSettingsOrganization,
  apiPutVideoProcessing,
  apiUpdateSettingsUserRole,
  type DroneChecklistDto,
  type NotificationSettingsDto,
  type OrganizationSettingsDto,
  type PrivacySettingsDto,
  type SeasonDto,
  type SettingsTeamDto,
  type SettingsUserDto,
  type SubscriptionDto,
  type VideoProcessingDto,
} from "@/lib/api";
import { BillingPanel } from "@/components/settings/BillingPanel";

type TabId =
  | "organization"
  | "users"
  | "teams"
  | "roster"
  | "privacy"
  | "video"
  | "drone"
  | "notifications"
  | "billing";

const TABS: { id: TabId; label: string }[] = [
  { id: "organization", label: "Organizasyon" },
  { id: "users", label: "Kullanıcılar ve Roller" },
  { id: "teams", label: "Takımlar ve Sezonlar" },
  { id: "roster", label: "Kadro Yönetimi" },
  { id: "privacy", label: "Veri ve Gizlilik" },
  { id: "video", label: "Video İşleme" },
  { id: "drone", label: "Drone / Çekim Checklist’i" },
  { id: "notifications", label: "Bildirimler" },
  { id: "billing", label: "Abonelik ve Faturalama" },
];

const ROLES = ["admin", "coach", "analyst", "scout", "viewer"] as const;

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block space-y-1.5 text-sm">
      <span className="text-text-muted">{label}</span>
      {children}
    </label>
  );
}

function inputClass(disabled?: boolean) {
  return `w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-emerald-500/50 ${
    disabled ? "opacity-60" : ""
  }`;
}

const TAB_IDS: TabId[] = TABS.map((t) => t.id);

export default function SettingsPage() {
  const [tab, setTab] = useState<TabId>("organization");
  const [toast, setToast] = useState<string | null>(null);

  const [org, setOrg] = useState<OrganizationSettingsDto | null>(null);
  const [users, setUsers] = useState<SettingsUserDto[]>([]);
  const [teams, setTeams] = useState<SettingsTeamDto[]>([]);
  const [seasons, setSeasons] = useState<SeasonDto[]>([]);
  const [video, setVideo] = useState<VideoProcessingDto | null>(null);
  const [notifications, setNotifications] = useState<NotificationSettingsDto | null>(null);
  const [privacy, setPrivacy] = useState<PrivacySettingsDto | null>(null);
  const [drone, setDrone] = useState<DroneChecklistDto | null>(null);
  const [subscription, setSubscription] = useState<SubscriptionDto | null>(null);

  const [roster, setRoster] = useState<Player[]>(() => mockPlayers.slice(0, 12));

  const [inviteOpen, setInviteOpen] = useState(false);
  const [invite, setInvite] = useState({ email: "", full_name: "", role: "viewer" });

  const [newTeam, setNewTeam] = useState({
    name: "",
    age_category: "U15",
    game_format: "11v11",
    default_formation: "4-3-3",
    pitch_length: 105,
    pitch_width: 68,
    season: "2025-26",
  });

  const [newSeasonName, setNewSeasonName] = useState("");

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    window.setTimeout(() => setToast(null), 3200);
  }, []);

  const loadAll = useCallback(async () => {
    try {
      const [o, u, t, s, v, n, p, d, sub] = await Promise.all([
        apiGetSettingsOrganization(),
        apiGetSettingsUsers(),
        apiGetSettingsTeams(),
        apiGetSettingsSeasons(),
        apiGetVideoProcessing(),
        apiGetNotificationSettings(),
        apiGetPrivacySettings(),
        apiGetDroneChecklist(),
        apiGetSubscription(),
      ]);
      setOrg(o);
      setUsers(u);
      setTeams(t);
      setSeasons(s);
      setVideo(v);
      setNotifications(n);
      setPrivacy(p);
      setDrone(d);
      setSubscription(sub);
    } catch {
      showToast("Veriler yüklenemedi.");
    }
  }, [showToast]);

  useEffect(() => {
    void loadAll();
  }, [loadAll]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const q = new URLSearchParams(window.location.search).get("tab");
    if (q && TAB_IDS.includes(q as TabId)) setTab(q as TabId);
  }, []);

  const saveOrganization = async () => {
    if (!org) return;
    const body = {
      name: org.name,
      city: org.city,
      logo_url: org.logo_url,
      organization_type: org.organization_type,
      contact_email: org.contact_email,
      contact_phone: org.contact_phone,
      website: org.website,
    };
    const res = await apiPutSettingsOrganization(body);
    if (res) setOrg(res);
    showToast(res ? "Organizasyon kaydedildi." : "Kayıt (demo): yerel olarak güncellendi.");
  };

  const onInvite = async () => {
    const r = await apiInviteSettingsUser(invite);
    setInviteOpen(false);
    setInvite({ email: "", full_name: "", role: "viewer" });
    showToast(r?.message ?? "Davet gönderildi (demo).");
  };

  const changeRole = async (userId: number, role: string) => {
    const r = await apiUpdateSettingsUserRole(userId, role);
    if (r) setUsers((prev) => prev.map((x) => (x.id === userId ? r : x)));
    else
      setUsers((prev) =>
        prev.map((x) => (x.id === userId ? { ...x, role } : x))
      );
    showToast("Rol güncellendi.");
  };

  const deactivate = async (userId: number) => {
    const r = await apiDeactivateSettingsUser(userId);
    if (r) setUsers((prev) => prev.map((x) => (x.id === userId ? r : x)));
    else
      setUsers((prev) =>
        prev.map((x) => (x.id === userId ? { ...x, is_active: false } : x))
      );
    showToast("Kullanıcı pasifleştirildi.");
  };

  const createTeam = async () => {
    const r = await apiCreateSettingsTeam(newTeam);
    if (r) setTeams((prev) => [...prev, r]);
    else
      setTeams((prev) => [
        ...prev,
        {
          id: Math.max(0, ...prev.map((x) => x.id)) + 1,
          ...newTeam,
          is_active: true,
        },
      ]);
    setNewTeam({
      name: "",
      age_category: "U15",
      game_format: "11v11",
      default_formation: "4-3-3",
      pitch_length: 105,
      pitch_width: 68,
      season: "2025-26",
    });
    showToast("Takım oluşturuldu.");
  };

  const activateSeason = async (id: number) => {
    const r = await apiActivateSettingsSeason(id);
    if (r) await loadAll();
    else
      setSeasons((prev) =>
        prev.map((s) => ({ ...s, is_active: s.id === id }))
      );
    showToast("Aktif sezon güncellendi.");
  };

  const addSeasonLocal = () => {
    const name = newSeasonName.trim();
    if (!name) return;
    const id = Math.max(0, ...seasons.map((s) => s.id), 0) + 1;
    setSeasons((prev) => [
      { id, name, start_date: "", end_date: "", is_active: false, teams_count: 0 },
      ...prev.map((s) => ({ ...s, is_active: false })),
    ]);
    setNewSeasonName("");
    showToast("Sezon listeye eklendi (demo; backend’e yazılmaz).");
  };

  const saveVideo = async () => {
    if (!video) return;
    const r = await apiPutVideoProcessing(video);
    if (r) setVideo(r);
    showToast("Video işleme ayarları kaydedildi.");
  };

  const saveNotifications = async () => {
    if (!notifications) return;
    const r = await apiPutNotificationSettings(notifications);
    if (r) setNotifications(r);
    showToast("Bildirim tercihleri kaydedildi.");
  };

  const savePrivacy = async () => {
    if (!privacy) return;
    const r = await apiPutPrivacySettings(privacy);
    if (r) setPrivacy(r);
    showToast("Gizlilik ayarları kaydedildi.");
  };

  const saveDrone = async () => {
    if (!drone) return;
    const r = await apiPutDroneChecklist(drone);
    if (r) setDrone(r);
    showToast("Checklist güncellendi.");
  };

  const toggleDrone = (key: keyof DroneChecklistDto) => {
    setDrone((d) => (d ? { ...d, [key]: !d[key] } : d));
  };

  const toggleNotify = (key: keyof NotificationSettingsDto) => {
    setNotifications((n) => (n ? { ...n, [key]: !n[key] } : n));
  };

  const togglePrivacy = (key: keyof PrivacySettingsDto) => {
    setPrivacy((p) => (p ? { ...p, [key]: !p[key] } : p));
  };

  return (
    <div className="space-y-6">
      {toast ? (
        <div className="fixed bottom-6 right-6 z-40 rounded-xl border border-emerald-500/30 bg-emerald-950/90 px-4 py-3 text-sm text-emerald-100 shadow-lg">
          {toast}
        </div>
      ) : null}

      <div>
        <div className="text-sm font-medium text-emerald-200/80">Ayarlar</div>
        <h1 className="mt-1 text-2xl font-semibold text-white">Organizasyon Yönetimi</h1>
        <p className="mt-2 max-w-3xl text-sm text-text-muted">
          Kulüp bilgileri, kullanıcılar, takımlar, veri gizliliği ve video işleme tercihlerini buradan
          yönetin. PitchVision Lite demo ortamında bazı işlemler yalnızca arayüzde simüle edilir.
        </p>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-white/10 pb-3">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${
              tab === t.id
                ? "bg-emerald-500/20 text-emerald-100 ring-1 ring-emerald-500/40"
                : "bg-white/5 text-text-muted hover:text-white"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "organization" && !org && (
        <div className="rounded-2xl pv-card p-8 text-center text-sm text-text-muted">Yükleniyor…</div>
      )}
      {tab === "organization" && org && (
        <div className="rounded-2xl pv-card p-6 space-y-5">
          <div className="text-sm font-semibold text-white">Organizasyon</div>
          <div className="grid gap-4 md:grid-cols-2">
            <Field label="Logo URL">
              <input
                className={inputClass()}
                value={org.logo_url ?? ""}
                onChange={(e) => setOrg({ ...org, logo_url: e.target.value || null })}
              />
            </Field>
            <Field label="Kulüp adı">
              <input
                className={inputClass()}
                value={org.name}
                onChange={(e) => setOrg({ ...org, name: e.target.value })}
              />
            </Field>
            <Field label="Şehir">
              <input
                className={inputClass()}
                value={org.city}
                onChange={(e) => setOrg({ ...org, city: e.target.value })}
              />
            </Field>
            <Field label="Kulüp tipi">
              <select
                className={inputClass()}
                value={org.organization_type}
                onChange={(e) => setOrg({ ...org, organization_type: e.target.value })}
              >
                <option value="academy">Akademi</option>
                <option value="club">Kulüp</option>
                <option value="school">Okul</option>
              </select>
            </Field>
            <Field label="İletişim e-postası">
              <input
                className={inputClass()}
                value={org.contact_email ?? ""}
                onChange={(e) => setOrg({ ...org, contact_email: e.target.value || null })}
              />
            </Field>
            <Field label="Telefon">
              <input
                className={inputClass()}
                value={org.contact_phone ?? ""}
                onChange={(e) => setOrg({ ...org, contact_phone: e.target.value || null })}
              />
            </Field>
            <Field label="Web sitesi">
              <input
                className={inputClass()}
                value={org.website ?? ""}
                onChange={(e) => setOrg({ ...org, website: e.target.value || null })}
              />
            </Field>
          </div>
          <div className="flex justify-end">
            <button
              type="button"
              onClick={() => void saveOrganization()}
              className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
            >
              Kaydet
            </button>
          </div>
        </div>
      )}

      {tab === "users" && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="text-sm font-semibold text-white">Kullanıcılar ve Roller</div>
            <button
              type="button"
              onClick={() => setInviteOpen(true)}
              className="rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-sm text-white hover:bg-white/10"
            >
              Kullanıcı davet et
            </button>
          </div>
          <div className="rounded-2xl pv-card overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-white/10 bg-white/[0.03] text-text-muted">
                <tr>
                  <th className="px-4 py-3 font-medium">Ad</th>
                  <th className="px-4 py-3 font-medium">E-posta</th>
                  <th className="px-4 py-3 font-medium">Rol</th>
                  <th className="px-4 py-3 font-medium">Durum</th>
                  <th className="px-4 py-3 font-medium text-right">İşlem</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-white/5">
                    <td className="px-4 py-3 text-white">{u.full_name}</td>
                    <td className="px-4 py-3 text-text-muted">{u.email}</td>
                    <td className="px-4 py-3">
                      <select
                        className={inputClass(!u.is_active)}
                        disabled={!u.is_active}
                        value={u.role}
                        onChange={(e) => void changeRole(u.id, e.target.value)}
                      >
                        {ROLES.map((r) => (
                          <option key={r} value={r}>
                            {r}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={
                          u.is_active ? "text-emerald-300/90" : "text-amber-200/80"
                        }
                      >
                        {u.is_active ? "Aktif" : "Pasif"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      {u.is_active ? (
                        <button
                          type="button"
                          onClick={() => void deactivate(u.id)}
                          className="text-xs text-amber-200 hover:underline"
                        >
                          Pasifleştir
                        </button>
                      ) : (
                        <span className="text-xs text-text-muted">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-text-muted">
            Roller: Admin, Coach, Analyst, Scout, Viewer. Davetler gerçek ortamda e-posta ile
            tamamlanır.
          </p>
        </div>
      )}

      {tab === "teams" && (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl pv-card p-6 space-y-4">
            <div className="text-sm font-semibold text-white">Takım oluştur</div>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Takım adı">
                <input
                  className={inputClass()}
                  value={newTeam.name}
                  onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })}
                />
              </Field>
              <Field label="Yaş kategorisi">
                <input
                  className={inputClass()}
                  value={newTeam.age_category}
                  onChange={(e) => setNewTeam({ ...newTeam, age_category: e.target.value })}
                />
              </Field>
              <Field label="Oyun formatı">
                <input
                  className={inputClass()}
                  value={newTeam.game_format}
                  onChange={(e) => setNewTeam({ ...newTeam, game_format: e.target.value })}
                />
              </Field>
              <Field label="Varsayılan diziliş">
                <input
                  className={inputClass()}
                  value={newTeam.default_formation}
                  onChange={(e) => setNewTeam({ ...newTeam, default_formation: e.target.value })}
                />
              </Field>
              <Field label="Saha uzunluk (m)">
                <input
                  type="number"
                  className={inputClass()}
                  value={newTeam.pitch_length}
                  onChange={(e) =>
                    setNewTeam({ ...newTeam, pitch_length: Number(e.target.value) })
                  }
                />
              </Field>
              <Field label="Saha genişlik (m)">
                <input
                  type="number"
                  className={inputClass()}
                  value={newTeam.pitch_width}
                  onChange={(e) =>
                    setNewTeam({ ...newTeam, pitch_width: Number(e.target.value) })
                  }
                />
              </Field>
              <Field label="Sezon etiketi">
                <input
                  className={inputClass()}
                  value={newTeam.season}
                  onChange={(e) => setNewTeam({ ...newTeam, season: e.target.value })}
                />
              </Field>
            </div>
            <button
              type="button"
              onClick={() => void createTeam()}
              className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
            >
              Takımı kaydet
            </button>
          </div>

          <div className="rounded-2xl pv-card p-6 space-y-4">
            <div className="text-sm font-semibold text-white">Sezonlar</div>
            <div className="flex flex-wrap gap-2">
              <input
                className={`${inputClass()} max-w-xs`}
                placeholder="Yeni sezon adı (ör. 2026-27)"
                value={newSeasonName}
                onChange={(e) => setNewSeasonName(e.target.value)}
              />
              <button
                type="button"
                onClick={addSeasonLocal}
                className="rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-sm text-white hover:bg-white/10"
              >
                Sezon oluştur (demo)
              </button>
            </div>
            <ul className="space-y-2 text-sm">
              {seasons.map((s) => (
                <li
                  key={s.id}
                  className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2"
                >
                  <div>
                    <div className="font-medium text-white">{s.name}</div>
                    <div className="text-xs text-text-muted">
                      {s.start_date} — {s.end_date} · {s.teams_count} takım
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {s.is_active ? (
                      <span className="rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs text-emerald-200">
                        Aktif
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => void activateSeason(s.id)}
                        className="text-xs text-emerald-300 hover:underline"
                      >
                        Aktif yap
                      </button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-2xl pv-card p-6 lg:col-span-2">
            <div className="text-sm font-semibold text-white">Mevcut takımlar</div>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full min-w-[640px] text-left text-sm">
                <thead className="text-text-muted">
                  <tr>
                    <th className="py-2 pr-4">Ad</th>
                    <th className="py-2 pr-4">Yaş</th>
                    <th className="py-2 pr-4">Format</th>
                    <th className="py-2 pr-4">Diziliş</th>
                    <th className="py-2 pr-4">Saha</th>
                    <th className="py-2">Sezon</th>
                  </tr>
                </thead>
                <tbody>
                  {teams.map((t) => (
                    <tr key={t.id} className="border-t border-white/10">
                      <td className="py-2 pr-4 text-white">{t.name}</td>
                      <td className="py-2 pr-4">{t.age_category}</td>
                      <td className="py-2 pr-4">{t.game_format}</td>
                      <td className="py-2 pr-4">{t.default_formation}</td>
                      <td className="py-2 pr-4">
                        {t.pitch_length}×{t.pitch_width} m
                      </td>
                      <td className="py-2">{t.season}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {tab === "roster" && (
        <div className="space-y-4">
          <div className="rounded-2xl pv-card p-6 space-y-4">
            <div className="text-sm font-semibold text-white">Oyuncu içe / dışa aktarım</div>
            <p className="text-sm text-text-muted">
              CSV ile toplu oyuncu içe aktarma yakında. Şimdilik dosya seçimi yalnızca arayüz
              yer tutucusudur.
            </p>
            <UploadDropzone
              title="CSV yükle (placeholder)"
              onFileSelected={() => showToast("Dosya seçildi (demo; işlenmedi).")}
            />
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => showToast("Dışa aktarma kuyruğa alındı (demo).")}
                className="rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-sm text-white hover:bg-white/10"
              >
                Oyuncu export (JSON)
              </button>
            </div>
          </div>

          <div className="rounded-2xl pv-card p-6 space-y-3">
            <div className="text-sm font-semibold text-white">Takım kadrosu ve taşıma</div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[520px] text-left text-sm">
                <thead className="text-text-muted">
                  <tr>
                    <th className="py-2 pr-4">Oyuncu</th>
                    <th className="py-2 pr-4">Pozisyon</th>
                    <th className="py-2 pr-4">Takım ID</th>
                    <th className="py-2">Taşı</th>
                  </tr>
                </thead>
                <tbody>
                  {roster.map((p) => (
                    <tr key={p.id} className="border-t border-white/10">
                      <td className="py-2 pr-4 text-white">
                        {p.firstName} {p.lastName}
                      </td>
                      <td className="py-2 pr-4">{p.position}</td>
                      <td className="py-2 pr-4">{p.teamId ?? "—"}</td>
                      <td className="py-2">
                        <select
                          className={inputClass()}
                          value={p.teamId ?? ""}
                          onChange={(e) => {
                            const v = e.target.value ? Number(e.target.value) : undefined;
                            setRoster((prev) =>
                              prev.map((x) => (x.id === p.id ? { ...x, teamId: v } : x))
                            );
                            showToast("Oyuncu takımı güncellendi (demo).");
                          }}
                        >
                          <option value="">Atanmamış</option>
                          {teams.map((t) => (
                            <option key={t.id} value={t.id}>
                              {t.name}
                            </option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {tab === "privacy" && privacy && (
        <div className="space-y-4">
          <div className="rounded-2xl pv-card p-6 space-y-4">
            <div className="text-sm font-semibold text-white">Veri ve Gizlilik</div>
            <div className="space-y-3">
              {(
                [
                  ["anonymize_player_data", "Oyuncu verilerini anonimleştir"],
                  ["gdpr_enabled", "KVKK / GDPR bilgilendirme ve süreçleri etkin"],
                  ["parental_consent_required", "Veli onayı zorunlu (genç yaş grupları)"],
                  ["u8_u17_data_security_enabled", "U8–U17 gelişmiş veri güvenliği modu"],
                ] as const
              ).map(([key, label]) => (
                <label
                  key={key}
                  className="flex cursor-pointer items-center justify-between gap-4 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3"
                >
                  <span className="text-sm text-white">{label}</span>
                  <input
                    type="checkbox"
                    className="h-4 w-4 accent-emerald-500"
                    checked={privacy[key]}
                    onChange={() => togglePrivacy(key)}
                  />
                </label>
              ))}
            </div>
            <button
              type="button"
              onClick={() => void savePrivacy()}
              className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
            >
              Gizlilik ayarlarını kaydet
            </button>
          </div>

          <div className="rounded-2xl border border-amber-500/25 bg-amber-950/30 p-5 text-sm text-amber-100/90">
            <div className="font-semibold text-amber-100">U8–U17 veri güvenliği</div>
            <p className="mt-2 text-text-muted">
              Çocuk ve genç oyuncu verilerinde asgari işleme ilkesi uygulanmalı; veli bilgilendirmesi
              ve gerektiğinde açık rıza kayıtları saklanmalıdır. Bu ekran bilgilendirme amaçlıdır;
              hukuki metinler kulüp avukatınız tarafından sağlanmalıdır.
            </p>
          </div>

          <div className="rounded-2xl pv-card p-6 space-y-3 text-sm text-text-muted">
            <div className="font-semibold text-white">KVKK bilgilendirme (placeholder)</div>
            <p>
              Aydınlatma metni, veri işleme envanteri ve başvuru kanalları burada PDF veya URL
              olarak yayınlanacaktır. Şimdilik yalnızca yer tutucudur.
            </p>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => void apiPostSettingsDataExport().then(() => showToast("Export talebi alındı."))}
                className="rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-sm text-white"
              >
                Oyuncu verisi export
              </button>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Oyuncu ID — anonimleştir">
                <div className="flex gap-2">
                  <input id="anonymize-id" className={inputClass()} placeholder="ör. 12" />
                  <button
                    type="button"
                    onClick={() => {
                      const el = document.getElementById("anonymize-id") as HTMLInputElement;
                      const id = Number(el?.value);
                      if (!id) return showToast("Geçerli oyuncu ID girin.");
                      void apiPostSettingsDataAnonymize(id).then(() =>
                        showToast("Anonimleştirme talebi gönderildi.")
                      );
                    }}
                    className="shrink-0 rounded-xl bg-white/10 px-3 py-2 text-xs text-white"
                  >
                    Gönder
                  </button>
                </div>
              </Field>
              <Field label="Oyuncu ID — silme talebi">
                <div className="flex gap-2">
                  <input id="delete-id" className={inputClass()} placeholder="ör. 12" />
                  <button
                    type="button"
                    onClick={() => {
                      const el = document.getElementById("delete-id") as HTMLInputElement;
                      const id = Number(el?.value);
                      if (!id) return showToast("Geçerli oyuncu ID girin.");
                      void apiPostSettingsDataDeleteRequest(id).then(() =>
                        showToast("Silme talebi kayda alındı.")
                      );
                    }}
                    className="shrink-0 rounded-xl bg-white/10 px-3 py-2 text-xs text-white"
                  >
                    Talep
                  </button>
                </div>
              </Field>
            </div>
          </div>
        </div>
      )}

      {tab === "video" && video && (
        <div className="rounded-2xl pv-card p-6 space-y-4">
          <div className="text-sm font-semibold text-white">Video işleme</div>
          <div className="grid gap-4 md:grid-cols-2">
            <Field label="Varsayılan saha ölçüsü">
              <input
                className={inputClass()}
                value={video.default_pitch_size}
                onChange={(e) => setVideo({ ...video, default_pitch_size: e.target.value })}
              />
            </Field>
            <Field label="Varsayılan oyun formatı">
              <input
                className={inputClass()}
                value={video.default_game_format}
                onChange={(e) => setVideo({ ...video, default_game_format: e.target.value })}
              />
            </Field>
            <Field label="Detection confidence (0–1)">
              <input
                type="number"
                step="0.01"
                min={0}
                max={1}
                className={inputClass()}
                value={video.detection_confidence_threshold}
                onChange={(e) =>
                  setVideo({
                    ...video,
                    detection_confidence_threshold: Number(e.target.value),
                  })
                }
              />
            </Field>
            <Field label="Uyarı eşiği">
              <input
                type="number"
                step="0.01"
                min={0}
                max={1}
                className={inputClass()}
                value={video.alert_threshold_value}
                onChange={(e) =>
                  setVideo({ ...video, alert_threshold_value: Number(e.target.value) })
                }
              />
            </Field>
            <Field label="Klip varsayılan süresi (sn)">
              <input
                type="number"
                min={5}
                max={120}
                className={inputClass()}
                value={video.default_clip_duration}
                onChange={(e) =>
                  setVideo({ ...video, default_clip_duration: Number(e.target.value) })
                }
              />
            </Field>
          </div>
          <button
            type="button"
            onClick={() => void saveVideo()}
            className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
          >
            Kaydet
          </button>
        </div>
      )}

      {tab === "drone" && drone && (
        <div className="rounded-2xl pv-card p-6 space-y-4">
          <div className="text-sm font-semibold text-white">Drone / çekim checklist’i</div>
          <p className="text-sm text-text-muted">
            Maç günü çekim öncesi güvenlik ve uygunluk kontrolleri. Her maddeyi saha ekibiyle birlikte
            işaretleyin.
          </p>
          <div className="space-y-2">
            {(
              [
                ["flight_permission_checked", "Uçuş izni kontrol edildi"],
                ["pitch_safety_secured", "Saha güvenliği sağlandı"],
                ["parent_player_consents_checked", "Veli/oyuncu izinleri kontrol edildi"],
                ["camera_angle_ok", "Kamera açısı uygun"],
                ["pitch_lines_visible", "Saha çizgileri görünür"],
                ["wind_weather_ok", "Rüzgar/hava durumu uygun"],
              ] as const
            ).map(([key, label]) => (
              <label
                key={key}
                className="flex cursor-pointer items-center justify-between gap-4 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3"
              >
                <span className="text-sm text-white">{label}</span>
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-emerald-500"
                  checked={drone[key]}
                  onChange={() => toggleDrone(key)}
                />
              </label>
            ))}
          </div>
          <button
            type="button"
            onClick={() => void saveDrone()}
            className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
          >
            Checklist’i kaydet
          </button>
        </div>
      )}

      {tab === "notifications" && notifications && (
        <div className="rounded-2xl pv-card p-6 space-y-4">
          <div className="text-sm font-semibold text-white">Bildirimler</div>
          <div className="space-y-2">
            {(
              [
                ["notify_analysis_complete", "Analiz tamamlanınca bildir"],
                ["notify_errors", "Hata oluşunca bildir"],
                ["notify_new_report", "Yeni rapor oluşunca bildir"],
                ["notify_scout_note", "Scout notu eklenince bildir"],
                ["notify_player_development", "Oyuncu gelişim raporu oluşunca bildir"],
              ] as const
            ).map(([key, label]) => (
              <label
                key={key}
                className="flex cursor-pointer items-center justify-between gap-4 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3"
              >
                <span className="text-sm text-white">{label}</span>
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-emerald-500"
                  checked={notifications[key]}
                  onChange={() => toggleNotify(key)}
                />
              </label>
            ))}
          </div>
          <button
            type="button"
            onClick={() => void saveNotifications()}
            className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
          >
            Bildirimleri kaydet
          </button>
        </div>
      )}

      {tab === "billing" && subscription && (
        <div className="space-y-4">
          <BillingPanel
            subscription={subscription}
            onPortalClick={() => showToast("Fatura portalı yakında aktif olacak.")}
          />
          <p className="text-center text-sm text-text-muted">
            <Link
              href="/settings/billing"
              className="text-emerald-300/90 underline-offset-2 hover:underline"
            >
              Abonelik ve kullanımı ayrı sayfada aç
            </Link>
          </p>
        </div>
      )}

      <Modal open={inviteOpen} title="Kullanıcı davet et" onClose={() => setInviteOpen(false)}>
        <div className="space-y-4">
          <Field label="E-posta">
            <input
              className={inputClass()}
              value={invite.email}
              onChange={(e) => setInvite({ ...invite, email: e.target.value })}
            />
          </Field>
          <Field label="Ad Soyad">
            <input
              className={inputClass()}
              value={invite.full_name}
              onChange={(e) => setInvite({ ...invite, full_name: e.target.value })}
            />
          </Field>
          <Field label="Rol">
            <select
              className={inputClass()}
              value={invite.role}
              onChange={(e) => setInvite({ ...invite, role: e.target.value })}
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </Field>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setInviteOpen(false)}
              className="rounded-xl border border-white/10 px-4 py-2 text-sm text-text-muted"
            >
              Vazgeç
            </button>
            <button
              type="button"
              onClick={() => void onInvite()}
              className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white"
            >
              Davet gönder
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
