"use client";

import React from "react";

export type TimelineItem = {
  id: string;
  title: string;
  timeLabel?: string;
  tone?: "accent" | "success" | "warning" | "danger";
  description?: string;
};

export function Timeline({ items }: { items: TimelineItem[] }) {
  return (
    <div className="rounded-2xl pv-card p-4">
      <div className="flex flex-col gap-4">
        {items.map((it, i) => {
          const tone =
            it.tone === "success"
              ? "bg-success/60"
              : it.tone === "warning"
              ? "bg-warning/60"
              : it.tone === "danger"
              ? "bg-danger/60"
              : "bg-accent/70";
          return (
            <div key={it.id} className="flex gap-3">
              <div className="relative flex w-8 justify-center">
                <div className={`mt-1 h-3 w-3 rounded-full ${tone}`} />
                {i === items.length - 1 ? null : (
                  <div className="absolute top-4 h-full w-px bg-white/10" style={{ left: "50%" }} />
                )}
              </div>
              <div className="flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <div className="text-sm font-semibold text-white">{it.title}</div>
                  {it.timeLabel ? <span className="text-xs text-text-muted">{it.timeLabel}</span> : null}
                </div>
                {it.description ? <div className="mt-1 text-sm text-text-muted">{it.description}</div> : null}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

