"use client";

import React from "react";
import type { CalibrationResult } from "@/types/domain";

type CalibrationResultProps = {
  result: CalibrationResult | null;
  onCalculate: () => void;
  onTest: () => void;
  onSave: () => void;
  onStartAnalysis: () => void;
  isCalculating?: boolean;
  isTesting?: boolean;
  isSaving?: boolean;
};

export function CalibrationResultCard({ 
  result, 
  onCalculate, 
  onTest, 
  onSave, 
  onStartAnalysis,
  isCalculating = false,
  isTesting = false,
  isSaving = false
}: CalibrationResultProps) {
  const getQualityColor = (quality: CalibrationResult["quality"]) => {
    switch (quality) {
      case "excellent": return "text-success";
      case "good": return "text-accent";
      case "fair": return "text-warning";
      case "poor": return "text-danger";
      default: return "text-text-muted";
    }
  };

  const getQualityLabel = (quality: CalibrationResult["quality"]) => {
    switch (quality) {
      case "excellent": return "Mükemmel";
      case "good": return "İyi";
      case "fair": return "Orta";
      case "poor": return "Zayıf";
      default: return "Bilinmiyor";
    }
  };

  return (
    <div className="rounded-2xl pv-card p-5 space-y-4 border border-white/5 bg-white/[0.02]">
      <div className="text-sm font-semibold text-white flex items-center gap-2">
        <span>📐</span> Kalibrasyon Sonucu
      </div>
      
      {result ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white/5 rounded-xl p-3 border border-white/5">
              <div className="text-[10px] uppercase tracking-wider text-text-muted mb-1">Ortalama Hata</div>
              <div className="text-xl font-bold text-white tabular-nums">{result.averageError} m</div>
            </div>
            <div className="bg-white/5 rounded-xl p-3 border border-white/5">
              <div className="text-[10px] uppercase tracking-wider text-text-muted mb-1">Kalite</div>
              <div className={`text-xl font-bold ${getQualityColor(result.quality)}`}>
                {getQualityLabel(result.quality)}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2 text-xs text-text-soft">
            <span className="w-5 h-5 rounded-full bg-white/10 flex items-center justify-center text-[10px]">📍</span>
            <span>Kullanılan Nokta Sayısı: <strong>{result.pointCount} nokta</strong></span>
          </div>
          
          {result.quality === "poor" && (
            <div className="p-3 rounded-xl bg-danger/10 border border-danger/20 flex gap-3 items-start animate-pulse">
              <span className="text-lg">⚠️</span>
              <div>
                <div className="text-xs font-bold text-danger">Homografi kalitesi düşük</div>
                <div className="text-[11px] text-danger/80 mt-0.5 leading-relaxed">
                  İşaretlenen noktalar arasında perspektif uyumsuzluğu var. Lütfen noktaların doğruluğunu kontrol edin.
                </div>
              </div>
            </div>
          )}
          
          <div className="p-3 rounded-xl bg-accent/10 border border-accent/20 flex gap-3 items-start">
            <span className="text-lg text-accent">💡</span>
            <div className="text-[11px] text-accent-2/80 leading-relaxed">
              Kamera hareketliyse maç içinde yeniden kalibrasyon gerekebilir.
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-10 text-center space-y-3 bg-white/5 rounded-2xl border border-dashed border-white/10">
          <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center text-2xl opacity-50">📍</div>
          <div>
            <div className="text-sm font-medium text-white">Kalibrasyon Bekleniyor</div>
            <p className="text-[11px] text-text-muted mt-1 max-w-[200px] mx-auto">
              Saha sınırlarını belirlemek için en az 4 köşe noktası işaretlenmelidir.
            </p>
          </div>
        </div>
      )}
      
      <div className="space-y-2">
        <button
          onClick={onCalculate}
          disabled={isCalculating || !result}
          className="w-full px-4 py-2.5 rounded-xl text-sm font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isCalculating ? "⏳ Hesaplanıyor..." : "🧮 Homografi Hesapla"}
        </button>
        
        <button
          onClick={onTest}
          disabled={isTesting || !result}
          className="w-full px-4 py-2.5 rounded-xl text-sm font-medium bg-warning/20 border border-warning/40 text-warning hover:bg-warning/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isTesting ? "⏳ Test ediliyor..." : "🎯 Kalibrasyonu Test Et"}
        </button>
        
        <button
          onClick={onSave}
          disabled={isSaving || !result || result.quality === "poor"}
          className="w-full px-4 py-2.5 rounded-xl text-sm font-medium bg-success/20 border border-success/40 text-success hover:bg-success/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? "⏳ Kaydediliyor..." : "💾 Kaydet"}
        </button>
        
        <button
          onClick={onStartAnalysis}
          disabled={!result || result.quality === "poor"}
          className="w-full px-4 py-2.5 rounded-xl text-sm font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          🚀 Analize Başla
        </button>
      </div>
    </div>
  );
}