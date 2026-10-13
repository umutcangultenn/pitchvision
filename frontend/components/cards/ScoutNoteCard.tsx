"use client";

import React from "react";

import type { ScoutNote } from "@/types/domain";

export function ScoutNoteCard({ note }: { note: ScoutNote }) {
  return (
    <div className="rounded-2xl pv-card p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-white">Scouting notu</div>
          <div className="mt-2 line-clamp-4 text-sm text-text-muted">{note.note}</div>
          {note.tagsJson?.length ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {note.tagsJson.slice(0, 6).map((t, idx) => (
                <span
                  key={idx}
                  className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-text-muted"
                >
                  {t}
                </span>
              ))}
            </div>
          ) : null}
        </div>
        {typeof note.rating === "number" ? (
          <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-right">
            <div className="text-xs text-text-muted">Puan</div>
            <div className="mt-1 text-lg font-semibold text-white">{note.rating.toFixed(1)}</div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

