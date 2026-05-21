"use client";

import React from "react";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function TrendChartCard({
  title = "Trendi izleme",
  data,
}: {
  title?: string;
  data?: { x: string; y: number }[];
}) {
  const safe =
    data ??
    [
      { x: "1. Yarı", y: 0.52 },
      { x: "10'", y: 0.61 },
      { x: "20'", y: 0.58 },
      { x: "30'", y: 0.66 },
      { x: "40'", y: 0.72 },
    ];

  return (
    <div className="rounded-2xl pv-card p-5">
      <div className="text-sm font-semibold text-white">{title}</div>
      <div className="mt-4" style={{ height: 260 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={safe}>
            <XAxis dataKey="x" stroke="rgba(255,255,255,0.35)" />
            <YAxis stroke="rgba(255,255,255,0.35)" tickFormatter={(v) => `${Math.round(v * 100)}%`} />
            <Tooltip
              contentStyle={{
                background: "rgba(15,23,20,0.9)",
                border: "1px solid rgba(255,255,255,0.12)",
                borderRadius: 12,
              }}
              formatter={(value: any) => `${Math.round(Number(value) * 100)}%`}
              labelFormatter={(label: any) => String(label)}
            />
            <Line
              type="monotone"
              dataKey="y"
              stroke="rgba(52,211,153,0.95)"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

