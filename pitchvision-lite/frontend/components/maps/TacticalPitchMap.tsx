"use client";

import React from "react";

export function TacticalPitchMap({
  points,
}: {
  points?: { x: number; y: number; value?: number }[];
}) {
  const safe = points ?? [];

  const color = (v?: number) => {
    const t = typeof v === "number" ? Math.max(0, Math.min(1, v)) : 0.5;
    // Accent -> success gradient (basit)
    const accent = [14, 165, 162];
    const success = [52, 211, 153];
    const r = Math.round(accent[0] + (success[0] - accent[0]) * t);
    const g = Math.round(accent[1] + (success[1] - accent[1]) * t);
    const b = Math.round(accent[2] + (success[2] - accent[2]) * t);
    return `rgba(${r},${g},${b},0.95)`;
  };

  return (
    <div className="rounded-2xl pv-card p-4">
      <div className="flex items-center justify-between gap-4">
        <div className="text-sm font-semibold text-white">Taktik saha</div>
        <div className="text-xs text-text-muted">
          {safe.length ? `${safe.length} sinyal` : "Demo placeholder"}
        </div>
      </div>
      <div className="mt-4">
        <svg viewBox="0 0 100 60" className="h-64 w-full">
          <rect x="2" y="2" width="96" height="56" rx="3" fill="rgba(0,0,0,0.15)" stroke="rgba(255,255,255,0.18)" />
          <line x1="50" y1="2" x2="50" y2="58" stroke="rgba(255,255,255,0.12)" />
          <line x1="2" y1="30" x2="98" y2="30" stroke="rgba(255,255,255,0.12)" />
          {safe.slice(0, 120).map((p, idx) => (
            <circle
              key={idx}
              cx={2 + p.x * 0.96}
              cy={2 + p.y * 0.93}
              r={1.4 + (p.value ?? 0.5) * 1.8}
              fill={color(p.value)}
              opacity={0.88}
            />
          ))}
        </svg>
      </div>
    </div>
  );
}

