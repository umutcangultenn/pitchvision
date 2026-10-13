"use client";

import React, { useState, useRef, useCallback } from "react";
import type { OverlayType } from "@/types/domain";

type AnalysisVideoPlayerProps = {
  src?: string;
  title?: string;
  currentTime?: number;
  duration?: number;
  onTimeUpdate?: (time: number) => void;
  onCreateClip?: () => void;
  onAddNote?: () => void;
  overlays?: OverlayType[];
  onOverlayToggle?: (overlay: OverlayType) => void;
};

export function AnalysisVideoPlayer({
  src,
  title = "Maç videosu",
  currentTime = 0,
  duration = 5400, // 90 minutes default
  onTimeUpdate,
  onCreateClip,
  onAddNote,
  overlays = [],
  onOverlayToggle
}: AnalysisVideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showOverlayMenu, setShowOverlayMenu] = useState(false);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handlePlayPause = useCallback(() => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  }, [isPlaying]);

  const handleFrameStep = useCallback((direction: 'forward' | 'backward') => {
    if (videoRef.current) {
      const frameTime = 1 / 25; // 25 FPS
      const newTime = Math.max(0, Math.min(duration, currentTime + (direction === 'forward' ? frameTime : -frameTime)));
      videoRef.current.currentTime = newTime;
      onTimeUpdate?.(newTime);
    }
  }, [currentTime, duration, onTimeUpdate]);

  const handleSpeedChange = useCallback((rate: number) => {
    setPlaybackRate(rate);
    if (videoRef.current) {
      videoRef.current.playbackRate = rate;
    }
  }, []);

  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      videoRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  const overlayOptions: { key: OverlayType; label: string; icon: string }[] = [
    { key: "players", label: "Oyuncu Noktaları", icon: "👥" },
    { key: "player_ids", label: "Oyuncu ID'leri", icon: "🔢" },
    { key: "formation", label: "Takım Şekli", icon: "⚽" },
    { key: "defense_line", label: "Savunma Hattı", icon: "🛡️" },
    { key: "block_distance", label: "Blok Mesafesi", icon: "📏" },
    { key: "ball_trajectory", label: "Top Yörüngesi", icon: "🎾" },
    { key: "heatmap", label: "Heatmap", icon: "🔥" },
    { key: "tactical_alerts", label: "Taktiksel Uyarılar", icon: "⚠️" },
    { key: "pitch_zones", label: "Saha Bölgeleri", icon: "🗺️" },
  ];

  return (
    <div className="space-y-4">
      {/* Video container */}
      <div className="relative rounded-xl border border-white/10 bg-black overflow-hidden">
        {src ? (
          <video
            ref={videoRef}
            className="w-full aspect-video"
            src={src}
            onTimeUpdate={(e) => onTimeUpdate?.(e.currentTarget.currentTime)}
            onLoadedMetadata={() => {
              if (videoRef.current) {
                videoRef.current.playbackRate = playbackRate;
              }
            }}
          />
        ) : (
          <div className="w-full aspect-video bg-pitch flex items-center justify-center">
            <div className="text-center">
              <div className="text-4xl mb-2">🎬</div>
              <div className="text-sm text-text-muted">Video yükleniyor...</div>
            </div>
          </div>
        )}

        {/* Video overlay controls */}
        <div className="absolute top-4 right-4 flex gap-2">
          <button
            onClick={() => setShowOverlayMenu(!showOverlayMenu)}
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-black/60 border border-white/20 text-white hover:bg-black/80 transition-all"
          >
            🎛️ Overlay
          </button>
          <button
            onClick={onCreateClip}
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all"
          >
            ✂️ Klip
          </button>
          <button
            onClick={onAddNote}
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-warning/20 border border-warning/40 text-warning hover:bg-warning/30 transition-all"
          >
            📝 Not
          </button>
        </div>

        {/* Overlay menu */}
        {showOverlayMenu && (
          <div className="absolute top-16 right-4 w-64 rounded-xl bg-black/90 border border-white/20 p-4 space-y-2">
            <div className="text-sm font-semibold text-white mb-3">Video Overlay</div>
            {overlayOptions.map(option => (
              <label key={option.key} className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={overlays.includes(option.key)}
                  onChange={() => onOverlayToggle?.(option.key)}
                  className="w-4 h-4 rounded border-white/20 bg-white/10 text-accent focus:ring-accent/50"
                />
                <span className="text-sm">{option.icon}</span>
                <span className="text-sm text-white">{option.label}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Video controls */}
      <div className="rounded-xl pv-card p-4 space-y-3">
        {/* Main controls */}
        <div className="flex items-center gap-4">
          <button
            onClick={handlePlayPause}
            className="w-10 h-10 rounded-full bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all flex items-center justify-center"
          >
            {isPlaying ? "⏸️" : "▶️"}
          </button>
          
          <button
            onClick={() => handleFrameStep('backward')}
            className="w-8 h-8 rounded-lg bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all flex items-center justify-center text-sm"
          >
            ⏮️
          </button>
          
          <button
            onClick={() => handleFrameStep('forward')}
            className="w-8 h-8 rounded-lg bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all flex items-center justify-center text-sm"
          >
            ⏭️
          </button>

          <div className="flex-1 text-center">
            <div className="text-sm text-white font-mono">
              {formatTime(currentTime)} / {formatTime(duration)}
            </div>
          </div>

          {/* Speed controls */}
          <div className="flex gap-1">
            {[0.5, 1, 1.5, 2].map(rate => (
              <button
                key={rate}
                onClick={() => handleSpeedChange(rate)}
                className={`px-2 py-1 rounded text-xs font-medium transition-all ${
                  playbackRate === rate
                    ? "bg-accent/20 border border-accent/40 text-accent"
                    : "bg-white/10 border border-white/20 text-text hover:bg-white/15"
                }`}
              >
                {rate}x
              </button>
            ))}
          </div>

          <button
            onClick={toggleFullscreen}
            className="w-8 h-8 rounded-lg bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all flex items-center justify-center text-sm"
          >
            ⛶
          </button>
        </div>

        {/* Progress bar */}
        <div className="relative">
          <div className="h-2 rounded-full bg-white/10">
            <div 
              className="h-full rounded-full bg-accent transition-all duration-200"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            />
          </div>
          <input
            type="range"
            min={0}
            max={duration}
            value={currentTime}
            onChange={(e) => {
              const time = Number(e.target.value);
              if (videoRef.current) {
                videoRef.current.currentTime = time;
              }
              onTimeUpdate?.(time);
            }}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
        </div>
      </div>
    </div>
  );
}