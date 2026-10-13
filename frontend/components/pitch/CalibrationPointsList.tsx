"use client";

import React from "react";
import type { CalibrationPoint } from "@/types/domain";

type CalibrationPointsListProps = {
  points: CalibrationPoint[];
  selectedPoint: string | null;
  onPointSelect: (pointId: string) => void;
  onPointRemove: (pointId: string) => void;
};

export function CalibrationPointsList({ 
  points, 
  selectedPoint, 
  onPointSelect, 
  onPointRemove 
}: CalibrationPointsListProps) {
  const requiredPoints = points.filter(p => p.isRequired);
  const optionalPoints = points.filter(p => !p.isRequired);
  
  const PointItem = ({ point }: { point: CalibrationPoint }) => (
    <div
      className={`flex items-center justify-between p-3 rounded-lg border transition-all cursor-pointer ${
        selectedPoint === point.id
          ? "border-accent/40 bg-accent/10"
          : point.isMarked
          ? "border-success/30 bg-success/5 hover:bg-success/10"
          : "border-white/10 bg-white/5 hover:bg-white/10"
      }`}
      onClick={() => onPointSelect(point.id)}
    >
      <div className="flex items-center gap-3">
        <div className={`w-3 h-3 rounded-full ${
          point.isMarked 
            ? point.isRequired ? "bg-accent" : "bg-success"
            : "bg-white/20"
        }`} />
        <div>
          <div className="text-sm font-medium text-white">{point.label}</div>
          <div className="text-xs text-text-muted">{point.description}</div>
          {point.isMarked && point.x !== undefined && point.y !== undefined && (
            <div className="text-xs text-text-soft mt-1">
              Piksel: ({Math.round(point.x)}, {Math.round(point.y)})
            </div>
          )}
        </div>
      </div>
      <div className="flex items-center gap-2">
        {point.isRequired && (
          <span className="text-xs px-2 py-1 rounded bg-accent/20 text-accent">
            Gerekli
          </span>
        )}
        {point.isMarked && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onPointRemove(point.id);
            }}
            className="text-xs px-2 py-1 rounded bg-danger/20 text-danger hover:bg-danger/30 transition-all"
          >
            Sil
          </button>
        )}
      </div>
    </div>
  );

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-semibold text-white mb-3">Gerekli Noktalar</h3>
        <div className="space-y-2">
          {requiredPoints.map(point => (
            <PointItem key={point.id} point={point} />
          ))}
        </div>
      </div>
      
      <div>
        <h3 className="text-sm font-semibold text-white mb-3">İsteğe Bağlı Noktalar</h3>
        <div className="space-y-2">
          {optionalPoints.map(point => (
            <PointItem key={point.id} point={point} />
          ))}
        </div>
      </div>
    </div>
  );
}