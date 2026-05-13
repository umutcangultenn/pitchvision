"use client";

import React, { useMemo, useState } from "react";

import type { Clip } from "@/types/domain";
import { Modal } from "@/components/ui/Modal";
import { VideoPlayer } from "@/components/media/VideoPlayer";
import { demoVideoSrc } from "@/data/demo";

export function VideoClipCard({ clip }: { clip: Clip }) {
  const [open, setOpen] = useState(false);
  const start = useMemo(() => Math.round(clip.startTime), [clip.startTime]);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="w-full text-left rounded-2xl pv-card p-5 hover:border-emerald-400/40 transition"
      >
        <div className="flex gap-4">
          <div className="h-14 w-24 rounded-xl border border-white/10 bg-white/5" />
          <div className="min-w-0 flex-1">
            <div className="text-sm font-semibold text-white line-clamp-1">{clip.title}</div>
            <div className="mt-2 text-xs text-text-muted">
              {start}s - {Math.round(clip.endTime)}s
              {clip.tag ? ` • ${clip.tag}` : ""}
            </div>
          </div>
        </div>
      </button>
      <Modal open={open} title="Klip oynat" onClose={() => setOpen(false)}>
        <VideoPlayer src={demoVideoSrc} title={clip.title} />
      </Modal>
    </>
  );
}

