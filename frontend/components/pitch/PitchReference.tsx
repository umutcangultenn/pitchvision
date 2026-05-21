"use client";

import React from "react";
import type { CalibrationPoint } from "@/types/domain";

type PitchReferenceProps = {
  points: CalibrationPoint[];
  selectedPoint: string | null;
  onPointSelect: (pointId: string) => void;
};

export function PitchReference({ points, selectedPoint, onPointSelect }: PitchReferenceProps) {
  // Saha boyutları (ölçekli)
  const pitchWidth = 280;
  const pitchHeight = 180;
  const margin = 20;
  
  // Nokta pozisyonları (saha koordinatlarından SVG koordinatlarına)
  const getPointPosition = (point: CalibrationPoint) => {
    if (!point.fieldX || !point.fieldY) return { x: 0, y: 0 };
    
    const x = margin + (point.fieldX / 105) * (pitchWidth - 2 * margin);
    const y = margin + (point.fieldY / 68) * (pitchHeight - 2 * margin);
    
    return { x, y };
  };

  return (
    <div className="rounded-2xl pv-card p-5">
      <div className="text-sm font-semibold text-white mb-3">Saha Referansı</div>
      
      <div className="bg-pitch/20 rounded-lg p-4">
        <svg
          width={pitchWidth}
          height={pitchHeight}
          viewBox={`0 0 ${pitchWidth} ${pitchHeight}`}
          className="w-full h-auto"
        >
          {/* Saha arka planı */}
          <rect
            x={margin}
            y={margin}
            width={pitchWidth - 2 * margin}
            height={pitchHeight - 2 * margin}
            fill="#0d4d3d"
            stroke="#ffffff"
            strokeWidth="1"
          />
          
          {/* Orta çizgi */}
          <line
            x1={pitchWidth / 2}
            y1={margin}
            x2={pitchWidth / 2}
            y2={pitchHeight - margin}
            stroke="#ffffff"
            strokeWidth="1"
          />
          
          {/* Orta daire */}
          <circle
            cx={pitchWidth / 2}
            cy={pitchHeight / 2}
            r="20"
            fill="none"
            stroke="#ffffff"
            strokeWidth="1"
          />
          
          {/* Ceza sahaları */}
          <rect
            x={margin}
            y={margin + 40}
            width="40"
            height="80"
            fill="none"
            stroke="#ffffff"
            strokeWidth="1"
          />
          <rect
            x={pitchWidth - margin - 40}
            y={margin + 40}
            width="40"
            height="80"
            fill="none"
            stroke="#ffffff"
            strokeWidth="1"
          />
          
          {/* Penaltı noktaları */}
          <circle cx={margin + 30} cy={pitchHeight / 2} r="2" fill="#ffffff" />
          <circle cx={pitchWidth - margin - 30} cy={pitchHeight / 2} r="2" fill="#ffffff" />
          
          {/* Kalibrasyon noktaları */}
          {points.map(point => {
            const pos = getPointPosition(point);
            const isSelected = selectedPoint === point.id;
            const radius = isSelected ? 6 : 4;
            
            return (
              <g key={point.id}>
                {/* Nokta gölgesi */}
                <circle
                  cx={pos.x + 1}
                  cy={pos.y + 1}
                  r={radius}
                  fill="rgba(0, 0, 0, 0.3)"
                />
                
                {/* Nokta */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={radius}
                  fill={point.isMarked 
                    ? (point.isRequired ? "#0ea5a2" : "#34d399")
                    : "rgba(255, 255, 255, 0.3)"
                  }
                  stroke={isSelected ? "#ffffff" : "none"}
                  strokeWidth={isSelected ? "2" : "0"}
                  className="cursor-pointer transition-all"
                  onClick={() => onPointSelect(point.id)}
                />
                
                {/* Label */}
                <text
                  x={pos.x}
                  y={pos.y - 10}
                  textAnchor="middle"
                  fontSize="8"
                  fill="#ffffff"
                  className="pointer-events-none select-none"
                >
                  {point.id.split('-')[1] || point.id}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      
      <div className="mt-3 text-xs text-text-muted">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-accent"></div>
            <span>Gerekli</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-success"></div>
            <span>İsteğe bağlı</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-white/30"></div>
            <span>İşaretlenmemiş</span>
          </div>
        </div>
      </div>
    </div>
  );
}