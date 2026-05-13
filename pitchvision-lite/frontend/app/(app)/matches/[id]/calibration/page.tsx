"use client";

import React, { useMemo, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

import { mockMatches, mockVideos } from "@/data/demo";
import { CalibrationCanvas } from "@/components/pitch/CalibrationCanvas";
import { CalibrationPointsList } from "@/components/pitch/CalibrationPointsList";
import { CalibrationResultCard } from "@/components/pitch/CalibrationResult";
import { PitchReference } from "@/components/pitch/PitchReference";
import { VideoPlayer } from "@/components/media/VideoPlayer";
import { demoVideoSrc } from "@/data/demo";
import type { CalibrationPoint, CalibrationResult } from "@/types/domain";

export default function MatchCalibrationPage() {
  const params = useParams();
  const router = useRouter();
  const idParam = String(params.id);
  const matchId = Number(idParam);
  const isDemo = idParam === "demo-match" || !Number.isFinite(matchId);

  const match = useMemo(() => {
    if (isDemo) return null;
    return mockMatches.find((m) => m.id === matchId) ?? null;
  }, [matchId, isDemo]);

  const video = useMemo(() => {
    if (isDemo) return null;
    return mockVideos.find((v) => v.matchId === matchId) ?? null;
  }, [matchId, isDemo]);

  const [points, setPoints] = useState<CalibrationPoint[]>([]);
  const [selectedPoint, setSelectedPoint] = useState<string | null>(null);
  const [result, setResult] = useState<CalibrationResult | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const matchLabel = isDemo
    ? "Demo Maç"
    : match
    ? `${match.opponentName} (${new Date(match.matchDate).toLocaleDateString("tr-TR")})`
    : `Maç #${idParam}`;

  const handlePointsChange = useCallback((newPoints: CalibrationPoint[]) => {
    setPoints(newPoints);
  }, []);

  const handleResultChange = useCallback((newResult: CalibrationResult | null) => {
    setResult(newResult);
  }, []);

  const handlePointSelect = useCallback((pointId: string) => {
    setSelectedPoint(pointId);
  }, []);

  const handlePointRemove = useCallback((pointId: string) => {
    setPoints(prev => prev.map(p => 
      p.id === pointId 
        ? { ...p, x: undefined, y: undefined, isMarked: false }
        : p
    ));
    if (selectedPoint === pointId) {
      setSelectedPoint(null);
    }
  }, [selectedPoint]);

  const handleCalculate = useCallback(async () => {
    setIsCalculating(true);
    // Mock hesaplama süresi
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsCalculating(false);
  }, []);

  const handleTest = useCallback(async () => {
    setIsTesting(true);
    // Mock test süresi
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsTesting(false);
  }, []);

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    // Mock kaydetme süresi
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsSaving(false);
  }, []);

  const handleStartAnalysis = useCallback(() => {
    router.push(`/matches/${idParam}/processing`);
  }, [router, idParam]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
        <div>
          <div className="text-sm text-text-muted">Saha Kalibrasyonu</div>
          <h1 className="mt-1 text-2xl font-semibold text-white">{matchLabel}</h1>
          <p className="mt-2 text-sm text-text-muted max-w-2xl">
            Video frame üzerinde saha noktalarını işaretleyerek piksel koordinatlarını gerçek saha metrelerine dönüştürün.
          </p>
        </div>
        <Link
          href={`/matches/${idParam}/processing`}
          className="px-4 py-2 rounded-lg text-sm font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all"
        >
          ← İşleme Durumuna Dön
        </Link>
      </div>

      {/* Main layout */}
      <div className="grid gap-6 lg:grid-cols-4">
        {/* Sol: Canvas (2/4) */}
        <div className="lg:col-span-2 space-y-4">
          <CalibrationCanvas
            onPointsChange={handlePointsChange}
            onResultChange={handleResultChange}
          />
          
          {/* Video player */}
          <div className="rounded-2xl pv-card p-5">
            <div className="text-sm font-semibold text-white mb-3">Video Önizleme</div>
            <VideoPlayer 
              src={demoVideoSrc} 
              title={`${matchLabel} - Kalibrasyon`} 
            />
            <div className="mt-3 text-xs text-text-muted">
              Video üzerinde kalibrasyon noktalarını işaretleyin. Saha çizgilerinin net görünür olduğu bir frame seçin.
            </div>
          </div>
        </div>

        {/* Sağ: Kontroller (2/4) */}
        <div className="lg:col-span-2 space-y-4">
          {/* Nokta listesi */}
          <div className="rounded-2xl pv-card p-5">
            <div className="text-sm font-semibold text-white mb-3">Kalibrasyon Noktaları</div>
            <CalibrationPointsList
              points={points}
              selectedPoint={selectedPoint}
              onPointSelect={handlePointSelect}
              onPointRemove={handlePointRemove}
            />
          </div>

          {/* Sonuç kartı */}
          <CalibrationResultCard
            result={result}
            onCalculate={handleCalculate}
            onTest={handleTest}
            onSave={handleSave}
            onStartAnalysis={handleStartAnalysis}
            isCalculating={isCalculating}
            isTesting={isTesting}
            isSaving={isSaving}
          />
        </div>
      </div>

      {/* Alt: Saha referansı */}
      <PitchReference
        points={points}
        selectedPoint={selectedPoint}
        onPointSelect={handlePointSelect}
      />
    </div>
  );
}