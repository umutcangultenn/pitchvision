"use client";

import React, { useMemo, useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

import { mockMatches } from "@/data/demo";
import { ProcessingStep, type ProcessingStepItem, type StepStatus } from "@/components/ui/ProcessingStep";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { apiGetMatchById, apiGetProcessingStatus } from "@/lib/api";
import type { Match } from "@/types/domain";

// ─── Demo state types ────────────────────────────────────────────────────────
type DemoMode = "completed" | "processing" | "error";

// ─── 11-step pipeline definition ─────────────────────────────────────────────
const PIPELINE: { key: string; icon: string; label: string; description: string }[] = [
  { key: "upload",      icon: "📤", label: "Video yüklendi",        description: "Ham video dosyası depolama alanına aktarıldı." },
  { key: "metadata",    icon: "🔍", label: "Metadata çıkarıldı",    description: "Çözünürlük, FPS, süre ve codec bilgileri okundu." },
  { key: "frames",      icon: "🎞️", label: "Frame extraction",      description: "Video kareler halinde ayrıştırıldı ve önbelleğe alındı." },
  { key: "calibration", icon: "📐", label: "Saha kalibrasyonu",     description: "Homografi matrisi hesaplandı, perspektif düzeltildi." },
  { key: "detection",   icon: "👁️", label: "Oyuncu tespiti",        description: "Demo: gerçek YOLO yok; MVP’de örnek tespit adımı (YOLOv8 hedef mimari)." },
  { key: "tracking",    icon: "🎯", label: "Tracking",              description: "ByteTrack ile her nesneye benzersiz ID atandı." },
  { key: "metrics",     icon: "📊", label: "Metrik hesaplama",      description: "Kompaktlık, field tilt, PPDA ve hız metrikleri üretildi." },
  { key: "alerts",      icon: "⚡", label: "Taktiksel uyarılar",    description: "Kural motoru ile kritik taktiksel anlar tespit edildi." },
  { key: "clips",       icon: "✂️", label: "Klip oluşturma",        description: "Her uyarı için video klipler kesildi ve etiketlendi." },
  { key: "report",      icon: "📝", label: "Rapor hazırlanıyor",    description: "Maç özeti ve antrenman önerileri derleniyor." },
  { key: "done",        icon: "🏁", label: "Tamamlandı",            description: "Tüm analiz adımları başarıyla tamamlandı." },
];

function buildSteps(mode: DemoMode, currentStep?: number): ProcessingStepItem[] {
  if (mode === "completed") {
    return PIPELINE.map((s) => ({ ...s, status: "completed" as StepStatus }));
  }
  if (mode === "error") {
    // Error at calibration step (idx 3)
    return PIPELINE.map((s, i) => ({
      ...s,
      status: (i < 3 ? "completed" : i === 3 ? "error" : "pending") as StepStatus,
    }));
  }
  // processing: use currentStep for dynamic progress
  const current = currentStep ?? 6;
  return PIPELINE.map((s, i) => ({
    ...s,
    status: (i < current ? "completed" : i === current ? "current" : "pending") as StepStatus,
  }));
}

// ─── Info row helper ──────────────────────────────────────────────────────────
function InfoRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between items-start gap-2 py-2 border-b border-white/5 last:border-0">
      <span className="text-xs text-text-soft">{label}</span>
      <span className="text-xs text-text text-right">{value}</span>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────
export default function MatchProcessingPage() {
  const params = useParams();
  const router = useRouter();
  const idParam = String(params.id);
  const matchId = Number(idParam);
  const isDemo = idParam === "demo-match" || !Number.isFinite(matchId);

  const [match, setMatch] = useState<Match | null>(null);
  const [processingStatus, setProcessingStatus] = useState<string>("processing");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      if (isDemo) {
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        // Fetch match
        const matchRes = await apiGetMatchById(matchId);
        if (matchRes.ok) {
          setMatch(matchRes.data);
        } else {
          const fallback = mockMatches.find((m) => m.id === matchId);
          setMatch(fallback as Match);
        }

        // Fetch processing status
        const statusRes = await apiGetProcessingStatus(matchId);
        if (statusRes.ok) {
          setProcessingStatus(statusRes.data.status);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        const fallback = mockMatches.find((m) => m.id === matchId);
        setMatch(fallback as Match);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [matchId, isDemo]);

  const effectiveMatch = match || mockMatches.find((m) => m.id === matchId) || mockMatches[0];

  // Derive demo mode from processing status
  const defaultMode: DemoMode = useMemo(() => {
    if (isDemo) return "processing";
    if (processingStatus === "completed") return "completed";
    if (processingStatus === "error" || processingStatus === "failed") return "error";
    return "processing";
  }, [processingStatus, isDemo]);

  const [demoMode, setDemoMode] = useState<DemoMode>(defaultMode);
  const [currentStep, setCurrentStep] = useState(6);
  
  // Simulate real-time progress for processing mode
  useEffect(() => {
    if (demoMode !== "processing") return;
    
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= PIPELINE.length - 1) {
          setDemoMode("completed");
          return prev;
        }
        return prev + 1;
      });
    }, 3000); // Progress every 3 seconds
    
    return () => clearInterval(interval);
  }, [demoMode]);
  
  // Reset current step when mode changes
  useEffect(() => {
    if (demoMode === "processing") {
      setCurrentStep(6);
    }
  }, [demoMode]);
  
  const steps = useMemo(() => buildSteps(demoMode, currentStep), [demoMode, currentStep]);

  const hasError = demoMode === "error";
  const isCompleted = demoMode === "completed";

  const matchLabel = isDemo
    ? "Demo Maç"
    : effectiveMatch
    ? `${effectiveMatch.opponentName} (${new Date(effectiveMatch.matchDate).toLocaleDateString("tr-TR")})`
    : `Maç #${idParam}`;

  const videoName = isDemo ? "demo_match.mp4" : "—";
  const fileSize = isDemo ? "2.1 GB" : "—";
  const duration = isDemo ? "90:00" : "—";
  const source = isDemo ? "Dosya yükleme" : effectiveMatch?.videoSource === "file_upload" ? "Dosya yükleme" : effectiveMatch?.videoSource ?? "—";
  const calibQuality = demoMode === "completed" ? "İyi (ort. hata 0.8 m)" : demoMode === "error" ? "Yetersiz (hata > 3 m)" : "Hesaplanıyor…";
  const trackingScore = demoMode === "completed" ? "%94 güven" : demoMode === "error" ? "—" : "İşleniyor…";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
        <div>
          <div className="text-sm text-text-muted">İşleme Durumu</div>
          <h1 className="mt-1 text-2xl font-semibold text-white">{matchLabel}</h1>
          <div className="mt-2">
            <StatusBadge status={isCompleted ? "completed" : hasError ? "error" : "processing"} />
          </div>
        </div>

        {/* Demo state switcher */}
        <div className="flex gap-2 flex-wrap">
          {(["completed", "processing", "error"] as DemoMode[]).map((m) => (
            <button
              key={m}
              onClick={() => setDemoMode(m)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                demoMode === m
                  ? m === "completed"
                    ? "bg-success/20 border-success/40 text-success shadow-lg shadow-success/20"
                    : m === "error"
                    ? "bg-danger/20 border-danger/40 text-danger shadow-lg shadow-danger/20"
                    : "bg-accent/20 border-accent/40 text-accent shadow-lg shadow-accent/20"
                  : "bg-white/5 border-white/10 text-text-muted hover:bg-white/10 hover:border-white/20"
              }`}
            >
              {m === "completed" ? "✓ Tamamlandı" : m === "error" ? "✕ Hata" : "⟳ İşleniyor"}
            </button>
          ))}
        </div>
      </div>

      {/* Success banner */}
      {isCompleted && (
        <div className="rounded-xl border border-success/30 bg-success/10 p-4 flex flex-col sm:flex-row sm:items-center gap-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 rounded-full bg-success/20 border border-success/40 flex items-center justify-center">
              <span className="text-success text-lg animate-bounce">🎉</span>
            </div>
          </div>
          <div className="flex-1">
            <div className="text-sm font-semibold text-success">Analiz başarıyla tamamlandı!</div>
            <p className="text-xs text-text-muted mt-1">
              Video analizi tamamlandı. Artık maç raporunu görüntüleyebilir ve video analizine başlayabilirsiniz.
            </p>
          </div>
          <div className="flex gap-2 flex-shrink-0">
            <Link
              href={`/matches/${idParam}/analysis`}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all"
            >
              🎬 Analizi Görüntüle
            </Link>
          </div>
        </div>
      )}

      {/* Error banner */}
      {hasError && (
        <div className="rounded-xl border border-danger/30 bg-danger/10 p-4 flex flex-col sm:flex-row sm:items-start gap-4">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 rounded-full bg-danger/20 border border-danger/40 flex items-center justify-center">
              <span className="text-danger text-lg">⚠️</span>
            </div>
          </div>
          <div className="flex-1">
            <div className="text-sm font-semibold text-danger mb-1">Kalibrasyon noktaları yetersiz</div>
            <p className="text-xs text-text-muted mb-3">
              Saha köşe noktaları doğru tespit edilemedi. Ortalama hata 3 metrenin üzerinde — analiz devam ettirilemiyor.
            </p>
            <div className="text-xs text-text-soft">
              <strong>Öneriler:</strong> Saha çizgilerinin net görünür olduğundan, kamera açısının uygun olduğundan ve aydınlatmanın yeterli olduğundan emin olun.
            </div>
          </div>
          <div className="flex gap-2 flex-shrink-0">
            <Link
              href={`/matches/${idParam}/calibration`}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-warning/20 border border-warning/40 text-warning hover:bg-warning/30 transition-all"
            >
              📐 Kalibrasyonu Kontrol Et
            </Link>
            <button
              onClick={() => setDemoMode("processing")}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all"
            >
              🔄 Yeniden Dene
            </button>
          </div>
        </div>
      )}

      {/* Main grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left: stepper (2/3) */}
        <div className="lg:col-span-2 rounded-2xl pv-card p-5">
          <div className="text-sm font-semibold text-white mb-4">İşleme Adımları</div>
          <ProcessingStep steps={steps} />
        </div>

        {/* Right: info panel (1/3) */}
        <div className="space-y-4">
          {/* Video info */}
          <div className="rounded-2xl pv-card p-5">
            <div className="text-sm font-semibold text-white mb-3">Video Bilgisi</div>
            <InfoRow label="Dosya adı" value={videoName} />
            <InfoRow label="Maç" value={matchLabel} />
            <InfoRow label="Dosya boyutu" value={fileSize} />
            <InfoRow label="Süre" value={duration} />
            <InfoRow label="Kaynak" value={source} />
          </div>

          {/* Analysis quality */}
          <div className="rounded-2xl pv-card p-5">
            <div className="text-sm font-semibold text-white mb-3">Analiz Kalitesi</div>
            <InfoRow
              label="Kalibrasyon"
              value={
                <span className={hasError ? "text-danger" : isCompleted ? "text-success" : "text-text-muted"}>
                  {calibQuality}
                </span>
              }
            />
            <InfoRow
              label="Tracking güveni"
              value={
                <span className={isCompleted ? "text-success" : "text-text-muted"}>
                  {trackingScore}
                </span>
              }
            />
            {demoMode === "processing" && (
              <InfoRow
                label="Tahmini süre"
                value={
                  <span className="text-accent">
                    {Math.max(0, (PIPELINE.length - 1 - currentStep) * 3)} dk kaldı
                  </span>
                }
              />
            )}
          </div>

          {/* CTA */}
          <div className="rounded-2xl pv-card p-5 space-y-2">
            <div className="text-sm font-semibold text-white mb-3">Sonraki Adım</div>
            <Link
              href={`/matches/${idParam}/calibration`}
              className="flex items-center gap-2 w-full px-4 py-2.5 rounded-xl text-sm font-medium bg-white/5 border border-white/10 text-text hover:bg-white/10 transition-all"
            >
              <span>📐</span> Saha Kalibrasyonuna Git
            </Link>
            <Link
              href={`/matches/${idParam}/analysis`}
              className={`flex items-center gap-2 w-full px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isCompleted
                  ? "bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30"
                  : "bg-white/5 border border-white/10 text-text-soft cursor-not-allowed opacity-50"
              }`}
            >
              <span>🎬</span> Video Analizi Aç
            </Link>
            <Link
              href={`/matches/${idParam}/report`}
              className={`flex items-center gap-2 w-full px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isCompleted
                  ? "bg-success/20 border border-success/40 text-success hover:bg-success/30"
                  : "bg-white/5 border border-white/10 text-text-soft cursor-not-allowed opacity-50"
              }`}
            >
              <span>📄</span> Raporu Aç
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
