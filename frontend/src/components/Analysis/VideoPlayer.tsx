'use client';

import React, { useRef, useEffect, useCallback, forwardRef, useImperativeHandle } from 'react';

export interface VideoPlayerHandle {
  /** Seek the video to a specific second. */
  seekTo: (seconds: number) => void;
}

interface VideoPlayerProps {
  /** URL of the video to play. Pass null/undefined to show the placeholder. */
  videoUrl?: string | null;
  /** Called whenever the current playback time changes (throttled to ~1 s). */
  onTimeUpdate?: (currentSeconds: number) => void;
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = Math.floor(seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

const VideoPlayer = forwardRef<VideoPlayerHandle, VideoPlayerProps>(
  ({ videoUrl, onTimeUpdate }, ref) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const lastReportedRef = useRef<number>(-1);

    // Expose seekTo to parent via ref
    useImperativeHandle(ref, () => ({
      seekTo(seconds: number) {
        const video = videoRef.current;
        if (!video) return;
        video.currentTime = Math.max(0, seconds);
        // Auto-play after seek so the analyst sees the moment immediately
        video.play().catch(() => {
          // Autoplay may be blocked — silently ignore
        });
      },
    }));

    const handleTimeUpdate = useCallback(() => {
      const video = videoRef.current;
      if (!video || !onTimeUpdate) return;
      const current = Math.floor(video.currentTime);
      if (current !== lastReportedRef.current) {
        lastReportedRef.current = current;
        onTimeUpdate(current);
      }
    }, [onTimeUpdate]);

    useEffect(() => {
      const video = videoRef.current;
      if (!video) return;
      video.addEventListener('timeupdate', handleTimeUpdate);
      return () => video.removeEventListener('timeupdate', handleTimeUpdate);
    }, [handleTimeUpdate]);

    if (!videoUrl) {
      return (
        <div className="w-full aspect-video bg-gray-900 rounded-xl flex flex-col items-center justify-center border border-gray-700">
          <svg
            className="w-16 h-16 text-gray-600 mb-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M15 10l4.553-2.276A1 1 0 0121 8.723v6.554a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z"
            />
          </svg>
          <p className="text-gray-500 text-sm">Video henüz yüklenmedi</p>
          <p className="text-gray-600 text-xs mt-1">Maç videosu yüklendiğinde burada görünecek</p>
        </div>
      );
    }

    return (
      <div className="w-full rounded-xl overflow-hidden border border-gray-200 shadow-sm bg-black">
        <video
          ref={videoRef}
          src={videoUrl}
          controls
          preload="metadata"
          className="w-full aspect-video"
          aria-label="Maç videosu"
        >
          <track kind="captions" />
          Tarayıcınız video oynatmayı desteklemiyor.
        </video>
      </div>
    );
  }
);

VideoPlayer.displayName = 'VideoPlayer';

export default VideoPlayer;
