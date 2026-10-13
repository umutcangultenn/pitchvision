"use client";

import React, { useState, useRef, useCallback } from "react";
import type { VideoEvent } from "@/types/domain";

type VideoTimelineProps = {
  duration: number;
  currentTime: number;
  events: VideoEvent[];
  onSeek?: (time: number) => void;
  onEventClick?: (event: VideoEvent) => void;
};

export function VideoTimeline({ duration, currentTime, events, onSeek, onEventClick }: VideoTimelineProps) {
  const [hoveredEvent, setHoveredEvent] = useState<VideoEvent | null>(null);
  const [hoverPosition, setHoverPosition] = useState({ x: 0, y: 0 });
  const timelineRef = useRef<HTMLDivElement>(null);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getEventColor = (type: VideoEvent["type"]) => {
    switch (type) {
      case "alert": return "bg-danger border-danger/60";
      case "clip": return "bg-accent border-accent/60";
      case "goal": return "bg-success border-success/60";
      case "card": return "bg-warning border-warning/60";
      case "substitution": return "bg-white/60 border-white/80";
      default: return "bg-white/40 border-white/60";
    }
  };

  const getEventIcon = (type: VideoEvent["type"]) => {
    switch (type) {
      case "alert": return "⚠️";
      case "clip": return "✂️";
      case "goal": return "⚽";
      case "card": return "🟨";
      case "substitution": return "🔄";
      default: return "📍";
    }
  };

  const handleTimelineClick = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!timelineRef.current) return;
    
    const rect = timelineRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const time = percentage * duration;
    
    onSeek?.(Math.max(0, Math.min(duration, time)));
  }, [duration, onSeek]);

  const handleEventHover = useCallback((event: VideoEvent, e: React.MouseEvent) => {
    setHoveredEvent(event);
    setHoverPosition({ x: e.clientX, y: e.clientY });
  }, []);

  // Generate time markers (every 10 minutes)
  const timeMarkers = [];
  for (let i = 0; i <= duration; i += 600) { // 600 seconds = 10 minutes
    timeMarkers.push(i);
  }

  return (
    <div className="space-y-2">
      {/* Time markers */}
      <div className="relative h-6">
        {timeMarkers.map(time => (
          <div
            key={time}
            className="absolute text-xs text-text-muted"
            style={{ left: `${(time / duration) * 100}%`, transform: 'translateX(-50%)' }}
          >
            {formatTime(time)}
          </div>
        ))}
      </div>

      {/* Timeline */}
      <div
        ref={timelineRef}
        className="relative h-12 rounded-lg bg-white/10 border border-white/20 cursor-pointer overflow-hidden"
        onClick={handleTimelineClick}
      >
        {/* Progress bar */}
        <div
          className="absolute top-0 left-0 h-full bg-accent/30 transition-all duration-200"
          style={{ width: `${(currentTime / duration) * 100}%` }}
        />

        {/* Current time indicator */}
        <div
          className="absolute top-0 w-1 h-full bg-accent shadow-lg transition-all duration-200"
          style={{ left: `${(currentTime / duration) * 100}%` }}
        />

        {/* Events */}
        {events.map(event => (
          <div
            key={event.id}
            className={`absolute top-1 w-2 h-10 rounded-sm cursor-pointer transition-all hover:scale-110 ${getEventColor(event.type)}`}
            style={{ left: `${(event.timestamp / duration) * 100}%`, transform: 'translateX(-50%)' }}
            onClick={(e) => {
              e.stopPropagation();
              onEventClick?.(event);
            }}
            onMouseEnter={(e) => handleEventHover(event, e)}
            onMouseLeave={() => setHoveredEvent(null)}
            title={event.title}
          >
            <div className="text-xs text-center leading-10">
              {getEventIcon(event.type)}
            </div>
          </div>
        ))}

        {/* Grid lines (every 5 minutes) */}
        {Array.from({ length: Math.floor(duration / 300) }, (_, i) => (i + 1) * 300).map(time => (
          <div
            key={time}
            className="absolute top-0 w-px h-full bg-white/10"
            style={{ left: `${(time / duration) * 100}%` }}
          />
        ))}
      </div>

      {/* Event legend */}
      <div className="flex items-center gap-4 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-sm bg-danger"></div>
          <span className="text-text-muted">Uyarılar</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-sm bg-accent"></div>
          <span className="text-text-muted">Klipler</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-sm bg-success"></div>
          <span className="text-text-muted">Goller</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-sm bg-warning"></div>
          <span className="text-text-muted">Kartlar</span>
        </div>
      </div>

      {/* Hover preview card */}
      {hoveredEvent && (
        <div
          className="fixed z-50 p-3 rounded-lg bg-black/90 border border-white/20 text-white shadow-xl pointer-events-none"
          style={{
            left: hoverPosition.x + 10,
            top: hoverPosition.y - 60,
            transform: 'translateY(-100%)'
          }}
        >
          <div className="text-sm font-medium mb-1">{hoveredEvent.title}</div>
          <div className="text-xs text-text-muted mb-1">{formatTime(hoveredEvent.timestamp)}</div>
          {hoveredEvent.description && (
            <div className="text-xs text-text-soft max-w-48">{hoveredEvent.description}</div>
          )}
          {hoveredEvent.confidence && (
            <div className="text-xs text-accent mt-1">
              Güven: {Math.round(hoveredEvent.confidence * 100)}%
            </div>
          )}
        </div>
      )}
    </div>
  );
}