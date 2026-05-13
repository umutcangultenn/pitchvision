"use client";

import React from "react";

export function MiniPitchMap({
  points,
}: {
  points?: { x: number; y: number; tone?: "accent" | "success" | "warning" | "danger" }[];
}) {
  const safe = points ?? [];

  return (
    <div className="rounded-2xl pv-card p-4">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold text-white">Mini saha</div>
        <div className="text-xs text-text-muted">{safe.length} odak</div>
      </div>
      <div className="mt-4">
        <svg viewBox="0 0 100 60" className="h-40 w-full">
          <rect x="2" y="2" width="96" height="56" rx="3" fill="rgba(0,0,0,0.15)" stroke="rgba(255,255,255,0.18)" />
          <line x1="50" y1="2" x2="50" y2="58" stroke="rgba(255,255,255,0.12)" />
          <line x1="2" y1="30" x2="98" y2="30" stroke="rgba(255,255,255,0.12)" />
          {safe.slice(0, 24).map((p, idx) => {
            const tone =
              p.tone === "success"
                ? "rgba(52,211,153,0.9)"
                : p.tone === "warning"
                ? "rgba(251,191,36,0.95)"
                : p.tone === "danger"
                ? "rgba(251,113,133,0.95)"
                : "rgba(14,165,162,0.95)";
            return <circle key={idx} cx={2 + p.x * 0.96} cy={2 + p.y * 0.93} r="1.7" fill={tone} />;
          })}
        </svg>
      </div>
    </div>
  );
}

