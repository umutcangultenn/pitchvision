'use client';

import React, { useState } from 'react';

const EVENT_TAGS = [
  { id: 'shot',                label: 'Şut',                  color: 'bg-blue-100 text-blue-700' },
  { id: 'goal',                label: 'Gol',                  color: 'bg-green-100 text-green-700' },
  { id: 'possession_loss',     label: 'Top Kaybı',            color: 'bg-red-100 text-red-700' },
  { id: 'possession_regain',   label: 'Top Kazanma',          color: 'bg-green-100 text-green-700' },
  { id: 'pressing_moment',     label: 'Baskı Anı',            color: 'bg-orange-100 text-orange-700' },
  { id: 'transition',          label: 'Geçiş Hücumu',         color: 'bg-purple-100 text-purple-700' },
  { id: 'dangerous_attack',    label: 'Tehlikeli Atak',       color: 'bg-rose-100 text-rose-700' },
  { id: 'buildup_issue',       label: 'Oyun Kurma Sorunu',    color: 'bg-amber-100 text-amber-700' },
  { id: 'compactness_issue',   label: 'Kompaktlık Sorunu',    color: 'bg-stone-100 text-stone-700' },
  { id: 'counter_attack',      label: 'Kontratak',            color: 'bg-indigo-100 text-indigo-700' },
  { id: 'wing_overload',       label: 'Kanat Yığılması',      color: 'bg-teal-100 text-teal-700' },
  { id: 'defensive_breakdown', label: 'Savunma Zafiyeti',     color: 'bg-red-200 text-red-800' },
] as const;

interface EventTaggerProps {
  /** Current video playback position in seconds. */
  currentTimestamp: number;
  /** Called when the analyst submits a new event. */
  onSaveEvent: (data: {
    tag: string;
    timestamp_seconds: number;
    notes: string;
    confidence: string;
  }) => void;
  /** Disables the form while the parent is persisting the event. */
  isSaving?: boolean;
}

export default function EventTagger({ currentTimestamp, onSaveEvent, isSaving = false }: EventTaggerProps) {
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [notes,       setNotes]       = useState('');
  const [confidence,  setConfidence]  = useState('certain');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTag || isSaving) return;

    onSaveEvent({
      tag: selectedTag,
      timestamp_seconds: currentTimestamp,
      notes,
      confidence,
    });

    setSelectedTag(null);
    setNotes('');
  };

  return (
    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Manuel Olay Ekle</h3>

      <div className="mb-4">
        <p className="text-sm text-gray-500 mb-2">
          Seçili Zaman:{' '}
          <span className="font-mono font-bold text-gray-800">
            {Math.floor(currentTimestamp / 60).toString().padStart(2, '0')}:
            {Math.floor(currentTimestamp % 60).toString().padStart(2, '0')}
          </span>
          <span className="ml-2 text-xs text-gray-400">(video pozisyonundan otomatik alınır)</span>
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Olay Türü</label>
          <div className="flex flex-wrap gap-2" role="group" aria-label="Olay türü seçimi">
            {EVENT_TAGS.map((tag) => (
              <button
                key={tag.id}
                type="button"
                onClick={() => setSelectedTag(tag.id)}
                aria-pressed={selectedTag === tag.id}
                className={`
                  px-3 py-1.5 rounded-full text-xs font-medium transition-colors border
                  ${selectedTag === tag.id
                    ? `border-transparent ring-2 ring-offset-1 ring-gray-400 ${tag.color}`
                    : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'}
                `}
              >
                {tag.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label htmlFor="event-notes" className="block text-sm font-medium text-gray-700 mb-1">
            Analist Notu <span className="text-gray-400 font-normal">(opsiyonel)</span>
          </label>
          <textarea
            id="event-notes"
            rows={2}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
            placeholder="Pozisyon hakkında detaylı notunuz..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>

        <div className="flex justify-between items-center pt-2">
          <label htmlFor="event-confidence" className="sr-only">Güven seviyesi</label>
          <select
            id="event-confidence"
            value={confidence}
            onChange={(e) => setConfidence(e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
          >
            <option value="certain">Eminim</option>
            <option value="probable">Muhtemel</option>
            <option value="uncertain">Emin Değilim</option>
          </select>

          <button
            type="submit"
            disabled={!selectedTag || isSaving}
            className="inline-flex items-center gap-2 justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSaving && (
              <span className="animate-spin rounded-full h-3 w-3 border-b-2 border-white" aria-hidden="true" />
            )}
            {isSaving ? 'Kaydediliyor...' : 'Kaydet'}
          </button>
        </div>
      </form>
    </div>
  );
}
