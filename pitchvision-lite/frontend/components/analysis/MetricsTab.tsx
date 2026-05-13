"use client";

import React from "react";
import type { TeamMetrics } from "@/types/domain";

type MetricsTabProps = {
  metrics: TeamMetrics;
};

export function MetricsTab({ metrics }: MetricsTabProps) {
  const MetricItem = ({ 
    label, 
    value, 
    unit, 
    trend, 
    description 
  }: { 
    label: string; 
    value: number; 
    unit: string; 
    trend?: "up" | "down" | "stable";
    description?: string;
  }) => (
    <div className="p-4 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 transition-all">
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm font-medium text-white">{label}</div>
        {trend && (
          <div className={`text-xs px-2 py-1 rounded ${
            trend === "up" ? "bg-success/20 text-success" :
            trend === "down" ? "bg-danger/20 text-danger" :
            "bg-white/10 text-text-muted"
          }`}>
            {trend === "up" ? "↗️" : trend === "down" ? "↘️" : "→"}
          </div>
        )}
      </div>
      <div className="text-2xl font-bold text-accent mb-1">
        {value.toFixed(1)} <span className="text-sm font-normal text-text-muted">{unit}</span>
      </div>
      {description && (
        <div className="text-xs text-text-soft">{description}</div>
      )}
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="text-sm font-semibold text-white">Takım Metrikleri</div>
      
      <div className="grid gap-3">
        <MetricItem
          label="Takım Boyu"
          value={metrics.teamLength}
          unit="m"
          trend="stable"
          description="En gerideki ile en öndeki oyuncu arası mesafe"
        />
        
        <MetricItem
          label="Takım Genişliği"
          value={metrics.teamWidth}
          unit="m"
          trend="up"
          description="En soldaki ile en sağdaki oyuncu arası mesafe"
        />
        
        <MetricItem
          label="Kompaktlık"
          value={metrics.compactness}
          unit="m"
          trend="down"
          description="Oyuncular arası ortalama mesafe"
        />
        
        <MetricItem
          label="Savunma-Orta Saha"
          value={metrics.defenseToMidfieldDistance}
          unit="m"
          trend="stable"
          description="Savunma ve orta saha blokları arası mesafe"
        />
        
        <MetricItem
          label="Orta Saha-Forvet"
          value={metrics.midfieldToAttackDistance}
          unit="m"
          trend="up"
          description="Orta saha ve forvet blokları arası mesafe"
        />
        
        <MetricItem
          label="Geçiş Hızı"
          value={metrics.transitionSpeed}
          unit="m/s"
          trend="up"
          description="Top kazanımından sonraki ortalama ilerleme hızı"
        />
      </div>

      <div className="p-4 rounded-lg bg-accent/10 border border-accent/30">
        <div className="text-xs font-medium text-accent mb-2">💡 Analiz Notu</div>
        <div className="text-xs text-text-muted">
          Bu metrikler otomatik hesaplanmıştır. Taktiksel değerlendirme için antrenör gözlemi ile birlikte yorumlanmalıdır.
        </div>
      </div>
    </div>
  );
}