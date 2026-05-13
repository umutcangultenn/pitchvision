"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

import { UploadDropzone } from "@/components/ui/UploadDropzone";
import { ProcessingStep, type ProcessingStepItem } from "@/components/ui/ProcessingStep";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Toast, type ToastItem } from "@/components/ui/Toast";

import { VideoPlayer } from "@/components/media/VideoPlayer";
import { demoVideoSrc, mockTeams } from "@/data/demo";

export default function NewMatchPage() {
  const router = useRouter();
  const [fileName, setFileName] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploading, setUploading] = useState<boolean>(false);
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const [teamId, setTeamId] = useState<number>(mockTeams[0]?.id ?? 1);
  const [opponentName, setOpponentName] = useState<string>("");
  const [matchDate, setMatchDate] = useState<string>("");
  const [ageCategory, setAgeCategory] = useState<string>("U15");
  const [gameFormat, setGameFormat] = useState<string>("11v11");
  const [pitchType, setPitchType] = useState<string>("full");
  const [attackDirection, setAttackDirection] = useState<string>("left_to_right");
  const [videoSource, setVideoSource] = useState<string>("file_upload");
  const [note, setNote] = useState<string>("");

  const pushToast = (t: Omit<ToastItem, "id">) => {
    setToasts((prev) => [...prev, { ...t, id: String(Date.now()) }]);
  };

  const steps: ProcessingStepItem[] = [
    { key: "upload", icon: "📤", label: "Yükleme", status: fileName ? "completed" : "current", description: fileName ? "Dosya alındı (demo)" : "Video dosyasını seçin." },
    { key: "extract", icon: "🎞️", label: "Özellik çıkarımı", status: fileName ? "current" : "pending", description: "Tespitler ve tracklet'ler hesaplanacak." },
    { key: "report", icon: "📝", label: "Rapor", status: "pending", description: "Taktik raporlar ve antrenman önerileri." },
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="text-sm font-medium text-emerald-200/80">Maç Yükle</div>
          <h1 className="mt-1 text-2xl font-semibold text-white">Yeni maç kaydı</h1>
          <p className="mt-2 text-sm text-text-muted max-w-2xl">
            Demo akışı: video yükleyin, işleme adımlarını izleyin. Sonrasında rapor ve klipler üretilecek.
          </p>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3">
          <div className="text-xs text-text-muted">Durum</div>
          <div className="mt-1">
            <StatusBadge status={fileName ? "processing" : "scheduled"} />
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-2xl pv-card p-5">
          <div className="text-sm font-semibold text-white">Maç bilgileri</div>
          <form
            className="mt-4 grid gap-4 md:grid-cols-2"
            onSubmit={(e) => {
              e.preventDefault();
              pushToast({ title: "Maç oluşturuldu", message: "Demo maç kaydı oluşturuldu.", tone: "success" });
              router.push("/matches/demo-match/processing");
            }}
          >
            <div>
              <label className="block text-xs font-medium text-text-muted">Takım seç</label>
              <select
                value={teamId}
                onChange={(e) => setTeamId(Number(e.target.value))}
                className="mt-1 h-10 w-full rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              >
                {mockTeams.map((t) => (
                  <option key={t.id} value={t.id} className="bg-[#0a0f0d]">
                    {t.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-text-muted">Rakip takım adı</label>
              <input
                value={opponentName}
                onChange={(e) => setOpponentName(e.target.value)}
                className="mt-1 h-10 w-full rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
                placeholder="Örn: Beyazgöl Spor"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-text-muted">Maç tarihi</label>
              <input
                value={matchDate}
                onChange={(e) => setMatchDate(e.target.value)}
                className="mt-1 h-10 w-full rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
                type="date"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-text-muted">Yaş kategorisi</label>
              <input
                value={ageCategory}
                onChange={(e) => setAgeCategory(e.target.value)}
                className="mt-1 h-10 w-full rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
                placeholder="U15"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-text-muted">Oyun formatı</label>
              <select
                value={gameFormat}
                onChange={(e) => setGameFormat(e.target.value)}
                className="mt-1 h-10 w-full rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              >
                <option value="11v11" className="bg-[#0a0f0d]">11v11</option>
                <option value="9v9" className="bg-[#0a0f0d]">9v9</option>
                <option value="7v7" className="bg-[#0a0f0d]">7v7</option>
                <option value="5v5" className="bg-[#0a0f0d]">5v5</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-text-muted">Saha tipi</label>
              <select
                value={pitchType}
                onChange={(e) => setPitchType(e.target.value)}
                className="mt-1 h-10 w-full rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              >
                <option value="full" className="bg-[#0a0f0d]">Tam saha</option>
                <option value="half" className="bg-[#0a0f0d]">Yarım saha</option>
                <option value="small_sided" className="bg-[#0a0f0d]">Dar alan</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-text-muted">İlk yarı hücum yönü</label>
              <select
                value={attackDirection}
                onChange={(e) => setAttackDirection(e.target.value)}
                className="mt-1 h-10 w-full rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              >
                <option value="left_to_right" className="bg-[#0a0f0d]">Sol → Sağ</option>
                <option value="right_to_left" className="bg-[#0a0f0d]">Sağ → Sol</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-text-muted">Video kaynağı</label>
              <select
                value={videoSource}
                onChange={(e) => setVideoSource(e.target.value)}
                className="mt-1 h-10 w-full rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              >
                <option value="file_upload" className="bg-[#0a0f0d]">Dosya yükleme</option>
                <option value="url_stream" className="bg-[#0a0f0d]">URL</option>
                <option value="youtube" className="bg-[#0a0f0d]">YouTube</option>
                <option value="other" className="bg-[#0a0f0d]">Diğer</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs font-medium text-text-muted">Maç notu</label>
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                className="mt-1 min-h-24 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
                placeholder="Örn: 2. yarı formasyon değişti, pres tetikleyicisi..."
              />
            </div>

            <div className="md:col-span-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-end">
              <button
                type="button"
                onClick={() => router.push("/matches")}
                className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-text-muted hover:text-white hover:border-emerald-400/40"
              >
                İptal
              </button>
              <button
                type="submit"
                className="rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-500"
              >
                Kaydet ve İşlemeye Gönder
              </button>
            </div>
          </form>
        </div>

        <aside className="space-y-4">
          <div className="rounded-2xl pv-card p-5">
            <div className="text-sm font-semibold text-white">Daha iyi analiz için çekim önerileri</div>
            <div className="mt-3 space-y-2 text-sm text-text-muted">
              <div className="flex gap-2">
                <span className="mt-2 h-1.5 w-1.5 rounded-full bg-accent/80" />
                <span>Kamera orta çizgi hizasında ve sabit olsun.</span>
              </div>
              <div className="flex gap-2">
                <span className="mt-2 h-1.5 w-1.5 rounded-full bg-accent/80" />
                <span>Top her zaman kadrajda kalsın; zoom minimum.</span>
              </div>
              <div className="flex gap-2">
                <span className="mt-2 h-1.5 w-1.5 rounded-full bg-accent/80" />
                <span>1080p/25fps veya üzeri önerilir.</span>
              </div>
            </div>
          </div>

          <div className="rounded-2xl pv-card p-5">
            <div className="text-sm font-semibold text-white">Önizleme (demo)</div>
            <div className="mt-3">
              <VideoPlayer src={demoVideoSrc} title="Maç videosu (demo)" />
            </div>
          </div>
        </aside>
      </div>

      <UploadDropzone
        title="Maç videosunu sürükle-bırak"
        onFileSelected={(file) => {
          setFileName(file.name);
          pushToast({ title: "Yüklendi", message: file.name, tone: "success" });
          setUploading(true);
          setUploadProgress(0);
          const start = Date.now();
          const timer = window.setInterval(() => {
            const t = Math.min(1, (Date.now() - start) / 1800);
            const p = Math.round(t * 100);
            setUploadProgress(p);
            if (p >= 100) {
              window.clearInterval(timer);
              setUploading(false);
              pushToast({ title: "Upload tamamlandı", message: "Kalibrasyona geçebilir veya daha sonra işleyebilirsiniz.", tone: "success" });
            }
          }, 120);
        }}
      />

      <div className="rounded-2xl pv-card p-5">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="text-sm font-semibold text-white">Upload progress</div>
            <div className="mt-1 text-sm text-text-muted">MP4/MOV • Drag & drop • Mock progress</div>
          </div>
          <div className="text-sm font-semibold text-white">{uploadProgress}%</div>
        </div>
        <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
          <div className="h-full bg-emerald-500 transition-all" style={{ width: `${uploadProgress}%` }} />
        </div>

        <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-end">
          <button
            disabled={uploading || !fileName}
            onClick={() => router.push("/matches/demo-match/calibration")}
            className="rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50"
          >
            Kalibrasyona geç
          </button>
          <button
            disabled={uploading || !fileName}
            onClick={() => router.push("/matches/demo-match/processing")}
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-text-muted hover:text-white hover:border-emerald-400/40 disabled:opacity-50"
          >
            Daha sonra işle
          </button>
        </div>
      </div>

      <ProcessingStep steps={steps} />

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl pv-card p-5">
          <div className="text-sm font-semibold text-white">İşleme sonrası</div>
          <p className="mt-2 text-sm text-text-muted">
            Gerçek backend eklenince burada upload & job başlatma yapılacak. Şimdilik, örnek maç sayfalarına yönlendiriyoruz.
          </p>
          <div className="mt-5 flex flex-col gap-3">
            <button
              disabled={!fileName}
              onClick={() => router.push("/matches/demo-match/processing")}
              className="rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50"
            >
              İşleme ekranına git
            </button>
            <button
              onClick={() => router.push("/dashboard")}
              className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-text-muted hover:text-white"
            >
              Dashboard&apos;a dön
            </button>
          </div>
        </div>
      </div>

      <Toast
        toasts={toasts}
        onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))}
      />
    </div>
  );
}
