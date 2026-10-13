"use client";

import React, { useState } from "react";
import type {
  PrivacySettingsDto,
} from "@/lib/apiSettings";
import {
  apiPostSettingsDataAnonymize,
  apiPostSettingsDataDeleteRequest,
  apiPostSettingsDataExport,
  apiPutPrivacySettings,
} from "@/lib/apiSettings";

// ── Helpers ───────────────────────────────────────────────────────────────────

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <div className="text-sm font-semibold text-white">{children}</div>;
}

function InfoBanner({
  tone,
  icon,
  title,
  children,
}: {
  tone: "amber" | "blue" | "red";
  icon: string;
  title: string;
  children: React.ReactNode;
}) {
  const colors = {
    amber: "border-amber-500/25 bg-amber-950/30 text-amber-100/90",
    blue:  "border-blue-500/25  bg-blue-950/30  text-blue-100/90",
    red:   "border-red-500/25   bg-red-950/30   text-red-100/90",
  };
  return (
    <div className={`rounded-2xl border p-5 text-sm ${colors[tone]}`}>
      <div className="flex items-start gap-3">
        <span className="text-xl flex-shrink-0">{icon}</span>
        <div>
          <div className="font-semibold mb-1">{title}</div>
          <div className="text-text-muted leading-relaxed">{children}</div>
        </div>
      </div>
    </div>
  );
}

function Toggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description?: string;
  checked: boolean;
  onChange: () => void;
}) {
  return (
    <label className="flex cursor-pointer items-start justify-between gap-4 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 hover:bg-white/[0.05] transition-colors">
      <div>
        <div className="text-sm text-white">{label}</div>
        {description && <div className="text-xs text-text-muted mt-0.5">{description}</div>}
      </div>
      <input
        type="checkbox"
        className="mt-0.5 h-4 w-4 flex-shrink-0 accent-emerald-500"
        checked={checked}
        onChange={onChange}
      />
    </label>
  );
}

// ── Consent record form ───────────────────────────────────────────────────────

function ConsentForm({ onSaved }: { onSaved: (msg: string) => void }) {
  const [form, setForm] = useState({
    player_id: "",
    guardian_name: "",
    guardian_email: "",
    consent_type: "video_recording",
  });

  const CONSENT_TYPES = [
    { value: "video_recording",      label: "Video kaydı" },
    { value: "data_processing",      label: "Kişisel veri işleme" },
    { value: "performance_analysis", label: "Performans analizi" },
    { value: "photo_sharing",        label: "Fotoğraf paylaşımı" },
  ];

  const save = () => {
    if (!form.player_id.trim() || !form.guardian_name.trim()) {
      onSaved("Oyuncu ID ve veli adı zorunludur.");
      return;
    }
    // TODO: apiPostConsent(form) — backend endpoint hazır olduğunda bağlanacak
    onSaved(`Veli onayı kaydedildi (demo): ${form.guardian_name} → ${form.consent_type}`);
    setForm({ player_id: "", guardian_name: "", guardian_email: "", consent_type: "video_recording" });
  };

  const inp = "w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-emerald-500/50";

  return (
    <div className="rounded-2xl pv-card p-5 space-y-4">
      <SectionTitle>Veli onayı kaydet</SectionTitle>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block space-y-1.5 text-sm">
          <span className="text-text-muted">Oyuncu ID</span>
          <input className={inp} placeholder="ör. 1" value={form.player_id}
            onChange={e => setForm(f => ({ ...f, player_id: e.target.value }))} />
        </label>
        <label className="block space-y-1.5 text-sm">
          <span className="text-text-muted">Veli / Vasi adı soyadı</span>
          <input className={inp} placeholder="Ad Soyad" value={form.guardian_name}
            onChange={e => setForm(f => ({ ...f, guardian_name: e.target.value }))} />
        </label>
        <label className="block space-y-1.5 text-sm">
          <span className="text-text-muted">Veli e-postası (opsiyonel)</span>
          <input className={inp} type="email" placeholder="veli@ornek.com" value={form.guardian_email}
            onChange={e => setForm(f => ({ ...f, guardian_email: e.target.value }))} />
        </label>
        <label className="block space-y-1.5 text-sm">
          <span className="text-text-muted">Onay türü</span>
          <select className={inp} value={form.consent_type}
            onChange={e => setForm(f => ({ ...f, consent_type: e.target.value }))}>
            {CONSENT_TYPES.map(t => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </label>
      </div>
      <div className="flex items-center gap-3">
        <button type="button" onClick={save}
          className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 transition-colors">
          Onayı kaydet
        </button>
        <span className="text-xs text-text-muted">
          Fiziksel onay formu ayrıca saklanmalıdır.
        </span>
      </div>
    </div>
  );
}

// ── Data actions ──────────────────────────────────────────────────────────────

function DataActions({ onToast }: { onToast: (msg: string) => void }) {
  const [playerId, setPlayerId] = useState("");
  const [deleteId, setDeleteId] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(false);

  const inp = "rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-emerald-500/50 w-40";

  return (
    <div className="rounded-2xl pv-card p-5 space-y-5">
      <SectionTitle>Veri işlemleri</SectionTitle>

      {/* Export */}
      <div className="flex flex-wrap items-center gap-3 pb-4 border-b border-white/10">
        <div className="flex-1 min-w-0">
          <div className="text-sm text-white">Tüm oyuncu verilerini dışa aktar</div>
          <div className="text-xs text-text-muted mt-0.5">
            KVKK madde 11 — veri sahibinin erişim hakkı kapsamında JSON formatında hazırlanır.
          </div>
        </div>
        <button type="button"
          onClick={() => apiPostSettingsDataExport().then(() => onToast("Export talebi alındı. Hazır olduğunda bildirim gönderilecek."))}
          className="rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-sm text-white hover:bg-white/10 transition-colors flex-shrink-0">
          📥 Veri export
        </button>
      </div>

      {/* Anonymize */}
      <div className="flex flex-wrap items-center gap-3 pb-4 border-b border-white/10">
        <div className="flex-1 min-w-0">
          <div className="text-sm text-white">Oyuncu verilerini anonimleştir</div>
          <div className="text-xs text-text-muted mt-0.5">
            Ad, soyad ve fotoğraf kaldırılır; analitik veriler korunur.
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <input className={inp} placeholder="Oyuncu ID" value={playerId}
            onChange={e => setPlayerId(e.target.value)} />
          <button type="button"
            onClick={() => {
              const id = Number(playerId);
              if (!id) return onToast("Geçerli bir oyuncu ID girin.");
              apiPostSettingsDataAnonymize(id).then(() => {
                onToast(`Oyuncu #${id} anonimleştirildi.`);
                setPlayerId("");
              });
            }}
            className="rounded-xl border border-amber-500/30 bg-amber-950/30 px-4 py-2 text-sm text-amber-200 hover:bg-amber-950/50 transition-colors">
            Anonimleştir
          </button>
        </div>
      </div>

      {/* Delete request */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex-1 min-w-0">
          <div className="text-sm text-white">Oyuncu verisi silme talebi</div>
          <div className="text-xs text-text-muted mt-0.5">
            KVKK madde 7 — silme ve yok etme hakkı. Talep 30 gün içinde işleme alınır.
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <input className={inp} placeholder="Oyuncu ID" value={deleteId}
            onChange={e => { setDeleteId(e.target.value); setConfirmDelete(false); }} />
          {!confirmDelete ? (
            <button type="button"
              onClick={() => { if (!Number(deleteId)) return onToast("Geçerli bir oyuncu ID girin."); setConfirmDelete(true); }}
              className="rounded-xl border border-red-500/30 bg-red-950/30 px-4 py-2 text-sm text-red-300 hover:bg-red-950/50 transition-colors">
              Silme talebi
            </button>
          ) : (
            <div className="flex gap-2">
              <button type="button"
                onClick={() => {
                  apiPostSettingsDataDeleteRequest(Number(deleteId)).then(() => {
                    onToast(`Oyuncu #${deleteId} için silme talebi oluşturuldu.`);
                    setDeleteId(""); setConfirmDelete(false);
                  });
                }}
                className="rounded-xl bg-red-600 px-3 py-2 text-xs font-semibold text-white hover:bg-red-500 transition-colors">
                Onayla
              </button>
              <button type="button" onClick={() => setConfirmDelete(false)}
                className="rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-xs text-white hover:bg-white/10 transition-colors">
                İptal
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Drone checklist ───────────────────────────────────────────────────────────

export function DroneChecklistPanel({
  drone,
  onChange,
  onSave,
}: {
  drone: Record<string, boolean>;
  onChange: (key: string) => void;
  onSave: () => void;
}) {
  const ITEMS: { key: string; label: string; description: string }[] = [
    {
      key: "flight_permission_checked",
      label: "Uçuş izni kontrol edildi",
      description: "İlgili belediye / havacılık otoritesinden gerekli izinler alındı.",
    },
    {
      key: "pitch_safety_secured",
      label: "Saha güvenliği sağlandı",
      description: "Çekim alanı çevresinde güvenlik önlemleri alındı, seyirci bilgilendirildi.",
    },
    {
      key: "parent_player_consents_checked",
      label: "Veli / oyuncu izinleri kontrol edildi",
      description: "U8-U17 oyuncular için veli onayları alındı ve kayıt altına alındı.",
    },
    {
      key: "camera_angle_ok",
      label: "Kamera açısı uygun",
      description: "Tüm saha görünür, kalibrasyon için saha çizgileri net.",
    },
    {
      key: "pitch_lines_visible",
      label: "Saha çizgileri görünür",
      description: "Homografi hesabı için köşe ve çizgi noktaları net seçilebilir.",
    },
    {
      key: "wind_weather_ok",
      label: "Rüzgar / hava durumu uygun",
      description: "Rüzgar hızı < 10 m/s, yağış yok, görüş mesafesi yeterli.",
    },
  ];

  const completed = ITEMS.filter(i => drone[i.key]).length;

  return (
    <div className="rounded-2xl pv-card p-5 space-y-4">
      <div className="flex items-center justify-between">
        <SectionTitle>Drone / Çekim Checklist'i</SectionTitle>
        <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
          completed === ITEMS.length
            ? "bg-emerald-500/20 text-emerald-200"
            : "bg-white/10 text-text-muted"
        }`}>
          {completed}/{ITEMS.length} tamamlandı
        </span>
      </div>

      <div className="space-y-2">
        {ITEMS.map(item => (
          <Toggle
            key={item.key}
            label={item.label}
            description={item.description}
            checked={!!drone[item.key]}
            onChange={() => onChange(item.key)}
          />
        ))}
      </div>

      {completed === ITEMS.length && (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/30 px-4 py-3 text-sm text-emerald-200">
          ✅ Tüm kontroller tamamlandı. Çekim başlatılabilir.
        </div>
      )}

      <button type="button" onClick={onSave}
        className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 transition-colors">
        Checklist'i kaydet
      </button>
    </div>
  );
}

// ── Main PrivacyPanel ─────────────────────────────────────────────────────────

export function PrivacyPanel({
  privacy,
  onToggle,
  onSave,
  onToast,
}: {
  privacy: PrivacySettingsDto;
  onToggle: (key: keyof PrivacySettingsDto) => void;
  onSave: () => void;
  onToast: (msg: string) => void;
}) {
  const TOGGLES: { key: keyof PrivacySettingsDto; label: string; description: string }[] = [
    {
      key: "anonymize_player_data",
      label: "Oyuncu verilerini anonimleştir",
      description: "Yeni kayıtlarda ad/soyad yerine anonim token kullanılır.",
    },
    {
      key: "gdpr_enabled",
      label: "KVKK / GDPR süreçleri etkin",
      description: "Aydınlatma metni, başvuru kanalı ve veri envanteri aktif.",
    },
    {
      key: "parental_consent_required",
      label: "Veli onayı zorunlu",
      description: "18 yaş altı oyuncular için veli onayı olmadan veri işlenemez.",
    },
    {
      key: "u8_u17_data_security_enabled",
      label: "U8–U17 gelişmiş veri güvenliği modu",
      description: "Çocuk oyuncu verileri için ek kısıtlamalar ve asgari işleme ilkesi.",
    },
  ];

  return (
    <div className="space-y-5">

      {/* U8-U17 uyarı banner */}
      <InfoBanner tone="amber" icon="🔒" title="U8–U17 oyuncu veri güvenliği">
        U8–U17 oyuncu verileri için veli onayı ve veri mahremiyeti süreçleri takip edilmelidir.
        Çocuk ve genç oyuncu verilerinde asgari işleme ilkesi uygulanmalı; veli bilgilendirmesi
        ve gerektiğinde açık rıza kayıtları saklanmalıdır.
      </InfoBanner>

      {/* KVKK bilgilendirme */}
      <InfoBanner tone="blue" icon="📋" title="KVKK bilgilendirme (placeholder)">
        Aydınlatma metni, veri işleme envanteri ve başvuru kanalları burada yayınlanacaktır.
        Hukuki metinler kulüp avukatınız tarafından hazırlanmalı ve bu alana eklenmelidir.
        Bu ekran yalnızca ürün içi uyumluluk alanı ve uyarı amacı taşır; hukuki danışmanlık
        yerine geçmez.
      </InfoBanner>

      {/* Gizlilik toggle'ları */}
      <div className="rounded-2xl pv-card p-5 space-y-3">
        <SectionTitle>Gizlilik ayarları</SectionTitle>
        {TOGGLES.map(t => (
          <Toggle
            key={t.key}
            label={t.label}
            description={t.description}
            checked={privacy[t.key]}
            onChange={() => onToggle(t.key)}
          />
        ))}
        <button type="button" onClick={onSave}
          className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 transition-colors">
          Gizlilik ayarlarını kaydet
        </button>
      </div>

      {/* Veli onayı formu */}
      <ConsentForm onSaved={onToast} />

      {/* Veri işlemleri */}
      <DataActions onToast={onToast} />

      {/* Disclaimer */}
      <InfoBanner tone="red" icon="⚠️" title="Önemli not">
        Bu ekrandaki işlemler demo ortamında simüle edilmektedir. Gerçek veri silme,
        anonimleştirme ve export işlemleri için backend entegrasyonu tamamlanmalı ve
        hukuki süreçler yürütülmelidir. PitchVision Lite hukuki danışmanlık vermez.
      </InfoBanner>

    </div>
  );
}
