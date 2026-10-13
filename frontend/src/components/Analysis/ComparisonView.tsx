'use client';

import React from 'react';
import AISummaryCard from './AISummaryCard';
import type { ComparisonResult } from '@/lib/api';

interface ComparisonViewProps {
  comparisonData: ComparisonResult | null;
  /** Optional: seek the video player to a specific second. */
  onSeekTo?: (seconds: number) => void;
}

export default function ComparisonView({ comparisonData, onSeekTo }: ComparisonViewProps) {
  if (!comparisonData) {
    return (
      <div className="text-center p-12 bg-gray-50 rounded-xl border border-gray-200 border-dashed">
        <svg
          className="w-10 h-10 text-gray-300 mx-auto mb-3"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <h3 className="text-sm font-medium text-gray-900">Karşılaştırma Bulunamadı</h3>
        <p className="mt-1 text-sm text-gray-500">
          Bu maç için henüz AI vs Analist karşılaştırması yapılmamış.
          Aşağıdaki butona tıklayarak oluşturabilirsiniz.
        </p>
      </div>
    );
  }

  const {
    total_engine_events,
    total_analyst_events,
    overlapping_events,
    engine_only_events,
    analyst_only_events,
    agreement_ratio,
    comparison_summary,
  } = comparisonData;

  const ratioPercentage = Math.round(agreement_ratio * 100);
  const totalForBar = total_engine_events + total_analyst_events || 1;

  return (
    <div className="space-y-6">
      {comparison_summary && (
        <AISummaryCard
          title="Yapay Zeka Değerlendirmesi"
          content={comparison_summary}
        />
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Agreement ratio */}
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col items-center justify-center">
          <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Anlaşma Oranı</span>
          <div
            className={`mt-2 text-4xl font-extrabold ${
              ratioPercentage >= 70 ? 'text-green-600' :
              ratioPercentage >= 40 ? 'text-yellow-500' : 'text-red-500'
            }`}
          >
            %{ratioPercentage}
          </div>
          <span className="mt-1 text-xs text-gray-400">Örtüşen / Toplam Olay</span>
        </div>

        {/* Event distribution */}
        <div className="col-span-2 bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <h4 className="text-sm font-medium text-gray-900 mb-4">Olay Dağılımı</h4>
          <div className="space-y-3">

            <div className="flex items-center">
              <span className="w-1/3 text-sm text-gray-600">Ortak Tespitler:</span>
              <div className="w-2/3 flex items-center gap-2">
                <div
                  className="bg-green-500 h-4 rounded-sm min-w-[4px]"
                  style={{ width: `${Math.max((overlapping_events / totalForBar) * 100, 2)}%` }}
                />
                <span className="text-sm font-bold text-gray-800">{overlapping_events}</span>
              </div>
            </div>

            <div className="flex items-center">
              <span className="w-1/3 text-sm text-gray-600">Sadece Yapay Zeka:</span>
              <div className="w-2/3 flex items-center gap-2">
                <div
                  className="bg-blue-400 h-4 rounded-sm min-w-[4px]"
                  style={{ width: `${Math.max((engine_only_events / totalForBar) * 100, 2)}%` }}
                />
                <span className="text-sm font-bold text-gray-800">{engine_only_events}</span>
              </div>
            </div>

            <div className="flex items-center">
              <span className="w-1/3 text-sm text-gray-600">Sadece Analist:</span>
              <div className="w-2/3 flex items-center gap-2">
                <div
                  className="bg-purple-400 h-4 rounded-sm min-w-[4px]"
                  style={{ width: `${Math.max((analyst_only_events / totalForBar) * 100, 2)}%` }}
                />
                <span className="text-sm font-bold text-gray-800">{analyst_only_events}</span>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Toplam AI',     value: total_engine_events,  color: 'text-blue-600' },
          { label: 'Toplam Analist', value: total_analyst_events, color: 'text-purple-600' },
          { label: 'Örtüşen',       value: overlapping_events,   color: 'text-green-600' },
          { label: 'Anlaşma',       value: `%${ratioPercentage}`, color: ratioPercentage >= 70 ? 'text-green-600' : 'text-yellow-600' },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm text-center">
            <p className="text-xs text-gray-500 uppercase tracking-wide">{stat.label}</p>
            <p className={`mt-1 text-2xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
