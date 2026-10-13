"use client";

import React from "react";
import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";

export function RadarChartCard({
  title = "Teknik profil",
  data,
}: {
  title?: string;
  data?: { metric: string; value: number }[];
}) {
  const safe =
    data ??
    [
      { metric: "Teknik", value: 0.82 },
      { metric: "Taktik", value: 0.76 },
      { metric: "Fizik", value: 0.67 },
      { metric: "Karar", value: 0.71 },
      { metric: "İlerleme", value: 0.74 },
    ];

  const radarData = safe.map((d) => ({ metric: d.metric, value: d.value * 100 }));

  return (
    <div className="rounded-2xl pv-card p-5">
      <div className="text-sm font-semibold text-white">{title}</div>
      <div className="mt-4" style={{ height: 260 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData} outerRadius={110}>
            <PolarGrid stroke="rgba(255,255,255,0.12)" />
            <PolarAngleAxis dataKey="metric" tick={false} />
            <Radar
              name="profile"
              dataKey="value"
              stroke="rgba(52,211,153,0.95)"
              fill="rgba(14,165,162,0.18)"
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 flex flex-wrap gap-2 text-xs text-text-muted">
        {safe.map((d) => (
          <span key={d.metric} className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
            {d.metric}: {Math.round(d.value * 100)}%
          </span>
        ))}
      </div>
    </div>
  );
}

