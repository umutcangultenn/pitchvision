'use client';

import React from 'react';
import type { MatchSegment } from '@/lib/api';

interface SegmentTimelineProps {
  segments: MatchSegment[];
  activeSegmentId: number | null;
  onSelectSegment: (id: number) => void;
}

function densityColor(density: number): string {
  if (density > 2.0) return 'bg-red-500 hover:bg-red-600';
  if (density > 1.0) return 'bg-orange-400 hover:bg-orange-500';
  if (density > 0.5) return 'bg-yellow-300 hover:bg-yellow-400';
  if (density > 0.1) return 'bg-green-300 hover:bg-green-400';
  return 'bg-gray-200 hover:bg-gray-300';
}

function densityTextColor(density: number): string {
  return density > 1.0 ? 'text-white' : 'text-gray-800';
}

function densitySubTextColor(density: number): string {
  return density > 1.0 ? 'text-red-100' : 'text-gray-600';
}

export default function SegmentTimeline({
  segments,
  onSelectSegment,
  activeSegmentId,
}: SegmentTimelineProps) {
  if (!segments || segments.length === 0) {
    return (
      <div className="text-gray-500 italic p-4 text-sm">
        Bölüm verisi bulunmuyor.
      </div>
    );
  }

  return (
    <div className="w-full overflow-x-auto bg-gray-50 p-4 rounded-xl border border-gray-100">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">
        Maç Zaman Çizelgesi (Bölümler)
      </h3>

      <div className="flex gap-2" role="group" aria-label="Maç segmentleri">
        {segments.map((seg) => {
          const density = seg.event_density ?? 0;
          const isActive = activeSegmentId === seg.id;

          return (
            <button
              key={seg.id}
              onClick={() => onSelectSegment(seg.id)}
              aria-pressed={isActive}
              title={`Yoğunluk: ${density.toFixed(1)} olay/dk | Tehlikeli Atak: ${seg.dangerous_attacks}`}
              className={`
                flex-shrink-0 flex flex-col items-center justify-center
                w-20 h-16 rounded cursor-pointer transition-all border-2
                ${isActive ? 'border-blue-600 shadow-md scale-105' : 'border-transparent'}
                ${densityColor(density)}
              `}
            >
              <span className={`text-xs font-bold ${densityTextColor(density)}`}>
                {seg.segment_label}
              </span>
              <span className={`text-[10px] ${densitySubTextColor(density)}`}>
                {seg.dangerous_attacks} atak
              </span>
            </button>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-3 flex items-center justify-end text-xs text-gray-500 gap-3">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded bg-gray-200" aria-hidden="true" /> Düşük
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded bg-yellow-300" aria-hidden="true" /> Orta
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded bg-orange-400" aria-hidden="true" /> Yüksek
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded bg-red-500" aria-hidden="true" /> Kritik
        </span>
      </div>
    </div>
  );
}
