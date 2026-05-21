"use client";

import React, { useState } from "react";

type CreateClipModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onCreateClip: (data: {
    title: string;
    description: string;
    startTime: number;
    endTime: number;
    tag: string;
  }) => void;
  currentTime: number;
};

export function CreateClipModal({ isOpen, onClose, onCreateClip, currentTime }: CreateClipModalProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [startTime, setStartTime] = useState(Math.max(0, currentTime - 10));
  const [endTime, setEndTime] = useState(currentTime + 10);
  const [tag, setTag] = useState("general");

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    onCreateClip({
      title: title.trim(),
      description: description.trim(),
      startTime,
      endTime,
      tag
    });

    // Reset form
    setTitle("");
    setDescription("");
    setStartTime(Math.max(0, currentTime - 10));
    setEndTime(currentTime + 10);
    setTag("general");
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl bg-surface border border-white/20 p-6 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-white">Klip Oluştur</h2>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all flex items-center justify-center"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Klip Başlığı *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Örn: Hızlı geçiş fırsatı"
              className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-text-muted"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Açıklama
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Klip hakkında detaylı açıklama..."
              rows={3}
              className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-text-muted resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-white mb-2">
                Başlangıç
              </label>
              <input
                type="number"
                value={startTime}
                onChange={(e) => setStartTime(Number(e.target.value))}
                min={0}
                step={0.1}
                className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white"
              />
              <div className="text-xs text-text-muted mt-1">{formatTime(startTime)}</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-white mb-2">
                Bitiş
              </label>
              <input
                type="number"
                value={endTime}
                onChange={(e) => setEndTime(Number(e.target.value))}
                min={startTime}
                step={0.1}
                className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white"
              />
              <div className="text-xs text-text-muted mt-1">{formatTime(endTime)}</div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Etiket
            </label>
            <select
              value={tag}
              onChange={(e) => setTag(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white"
            >
              <option value="general">Genel</option>
              <option value="transition">Geçiş</option>
              <option value="pressing">Baskı</option>
              <option value="duel">İkili Mücadele</option>
              <option value="wing_overload">Kanat Yüklenmesi</option>
              <option value="set_piece">Duran Top</option>
              <option value="goal">Gol</option>
              <option value="defense">Savunma</option>
            </select>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 rounded-xl text-sm font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all"
            >
              İptal
            </button>
            <button
              type="submit"
              disabled={!title.trim()}
              className="flex-1 px-4 py-2.5 rounded-xl text-sm font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ✂️ Oluştur
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}