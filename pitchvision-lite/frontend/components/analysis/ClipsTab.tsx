"use client";

import React from "react";
import type { Clip } from "@/types/domain";
import { EmptyState } from "@/components/ui/EmptyState";

type ClipsTabProps = {
  clips: Clip[];
  onDownload?: (clipId: number) => void;
  onShare?: (clipId: number) => void;
  onAddToReport?: (clipId: number) => void;
  onPlayClip?: (clipId: number, startTime: number) => void;
};

export function ClipsTab({ clips, onDownload, onShare, onAddToReport, onPlayClip }: ClipsTabProps) {
  const formatDuration = (startTime: number, endTime: number) => {
    const duration = endTime - startTime;
    return `${duration.toFixed(1)}s`;
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getTagColor = (tag?: string) => {
    switch (tag) {
      case "transition": return "bg-accent/20 text-accent border-accent/30";
      case "pressing": return "bg-warning/20 text-warning border-warning/30";
      case "duel": return "bg-danger/20 text-danger border-danger/30";
      case "wing_overload": return "bg-success/20 text-success border-success/30";
      default: return "bg-white/10 text-text-muted border-white/20";
    }
  };

  const getTagLabel = (tag?: string) => {
    switch (tag) {
      case "transition": return "Geçiş";
      case "pressing": return "Baskı";
      case "duel": return "İkili Mücadele";
      case "wing_overload": return "Kanat Yüklenmesi";
      default: return tag || "Genel";
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold text-white">Video Klipleri</div>
        <div className="text-xs text-text-muted">{clips.length} klip</div>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {clips.map(clip => (
          <div
            key={clip.id}
            className="p-4 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 transition-all"
          >
            <div className="flex gap-3">
              {/* Thumbnail placeholder */}
              <div className="w-20 h-12 rounded-lg bg-pitch flex items-center justify-center flex-shrink-0">
                <span className="text-xs text-white/60">🎬</span>
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="text-sm font-medium text-white mb-1">{clip.title}</div>
                    <div className="text-xs text-text-muted mb-2 line-clamp-2">{clip.description}</div>
                  </div>
                </div>

                <div className="flex items-center gap-2 mb-3">
                  <div className="text-xs text-text-soft">
                    {formatTime(clip.startTime)} • {formatDuration(clip.startTime, clip.endTime)}
                  </div>
                  {clip.tag && (
                    <span className={`text-xs px-2 py-1 rounded border ${getTagColor(clip.tag)}`}>
                      {getTagLabel(clip.tag)}
                    </span>
                  )}
                </div>

                <div className="flex gap-2 flex-wrap">
                  <button
                    onClick={() => onPlayClip?.(clip.id, clip.startTime)}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all"
                  >
                    ▶️ Oynat
                  </button>
                  
                  <button
                    onClick={() => onDownload?.(clip.id)}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all"
                  >
                    📥 İndir
                  </button>
                  
                  <button
                    onClick={() => onShare?.(clip.id)}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all"
                  >
                    📤 Paylaş
                  </button>
                  
                  <button
                    onClick={() => onAddToReport?.(clip.id)}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-success/20 border border-success/40 text-success hover:bg-success/30 transition-all"
                  >
                    📄 Rapora Ekle
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {clips.length === 0 && (
        <div className="py-8">
          <EmptyState
            title="Klip bulunamadı"
            description="Video üzerinde önemli anları klip olarak kaydederek burada listeleyebilirsiniz."
            icon="🎬"
          />
        </div>
      )}
    </div>
  );
}