"use client";

import React from "react";

import type { DrillRecommendation } from "@/types/domain";

export function DrillRecommendationCard({
  drill,
  isApplied,
  onMarkApplied,
}: {
  drill: DrillRecommendation;
  isApplied?: boolean;
  onMarkApplied?: () => void;
}) {
  return (
    <div className={`rounded-2xl pv-card p-5 transition-all ${isApplied ? "border border-success/30 bg-success/5" : ""}`}>
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-xs font-semibold text-accent">
              {drill.alertType.replaceAll("_", " ")}
            </span>
            <span className="text-xs text-text-muted">
              {drill.ageCategory} • {drill.pitchSize.replaceAll("_", " ")}
            </span>
            {isApplied && <span className="rounded-full bg-success/20 border border-success/30 text-success px-2 py-0.5 text-xs font-medium">✓ Uygulandı</span>}
          </div>
          <div className="mt-2 text-sm font-semibold text-white">{drill.title}</div>
          {drill.description ? (
            <div className="mt-2 line-clamp-3 text-sm text-text-muted">
              {drill.description}
            </div>
          ) : null}
        </div>

        <div className="flex flex-col items-end gap-2">
          <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-right">
            <div className="text-xs text-text-muted">Süre</div>
            <div className="mt-1 text-lg font-semibold text-white">{drill.durationMinutes} dk</div>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-right">
            <div className="text-xs text-text-muted">Oyuncu</div>
            <div className="mt-1 text-lg font-semibold text-white">{drill.playerCount}</div>
          </div>
        </div>
      </div>

      {drill.coachingPointsJson?.length ? (
        <div className="mt-4 rounded-xl border border-white/10 bg-black/20 p-4">
          <div className="text-xs font-semibold text-text-muted">Koçluk Noktaları</div>
          <div className="mt-2 space-y-2">
            {drill.coachingPointsJson.slice(0, 4).map((p, idx) => (
              <div key={idx} className="flex items-start gap-2 text-sm text-text-muted">
                <span className="mt-0.5 inline-block h-1.5 w-1.5 rounded-full bg-accent/80" />
                <span>{String(p.tr ?? p)}</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {/* Actions */}
      <div className="mt-4 flex flex-wrap gap-2">
        <button className="flex-1 min-w-fit px-3 py-2 rounded-lg text-xs font-medium bg-white/5 border border-white/10 text-text-muted hover:bg-white/10 transition-all">
          📋 Antrenman Planına Ekle
        </button>
        {onMarkApplied && (
          <button
            onClick={onMarkApplied}
            className={`flex-1 min-w-fit px-3 py-2 rounded-lg text-xs font-medium transition-all border ${
              isApplied
                ? "bg-success/20 border-success/40 text-success hover:bg-success/30"
                : "bg-accent/20 border-accent/40 text-accent hover:bg-accent/30"
            }`}
          >
            {isApplied ? "✓ Uygulandı" : "✓ Uygulandı Olarak İşaretle"}
          </button>
        )}
      </div>

      {/* Difficulty badge */}
      <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs text-text-muted">Zorluk:</span>
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
            drill.difficulty === "easy"
              ? "bg-green-500/20 text-green-300"
              : drill.difficulty === "medium"
              ? "bg-yellow-500/20 text-yellow-300"
              : "bg-red-500/20 text-red-300"
          }`}>
            {drill.difficulty === "easy" ? "Kolay" : drill.difficulty === "medium" ? "Orta" : "Zor"}
          </span>
        </div>
        <span className="text-xs text-text-muted">{drill.problemType}</span>
      </div>
    </div>
  );
}


