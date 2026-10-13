'use client';

import React from 'react';

interface AISummaryCardProps {
  title?: string;
  content: string;
}

export default function AISummaryCard({ title, content }: AISummaryCardProps) {
  if (!content) return null;

  return (
    <div className="bg-gradient-to-br from-[#f8f9fc] to-white p-6 rounded-2xl border border-[#e2e8f0] shadow-sm relative overflow-hidden">
      {/* Decorative background blur */}
      <div
        className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-blue-50 rounded-full blur-2xl opacity-70 pointer-events-none"
        aria-hidden="true"
      />

      <div className="flex items-center justify-between mb-4 relative z-10">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <svg
            className="w-5 h-5 text-blue-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          {title ?? 'Taktiksel Özet'}
        </h3>
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          AI Tarafından Üretildi
        </span>
      </div>

      <div className="prose prose-sm max-w-none text-gray-600 relative z-10">
        {content.split('\n').map((paragraph, idx) =>
          paragraph.trim() ? (
            <p key={idx} className="mb-2">
              {paragraph}
            </p>
          ) : null
        )}
      </div>

      <p className="mt-4 text-xs text-gray-400 italic relative z-10">
        Bu özet otomatik olarak üretilmiştir. Nihai değerlendirme analist gözlemiyle birlikte yapılmalıdır.
      </p>
    </div>
  );
}
