"use client";

import React, { useState } from "react";

type AddNoteModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onAddNote: (data: {
    content: string;
    timestamp: number;
    tags: string[];
  }) => void;
  currentTime: number;
};

export function AddNoteModal({ isOpen, onClose, onAddNote, currentTime }: AddNoteModalProps) {
  const [content, setContent] = useState("");
  const [tags, setTags] = useState("");

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    const tagArray = tags.split(',').map(tag => tag.trim()).filter(Boolean);

    onAddNote({
      content: content.trim(),
      timestamp: currentTime,
      tags: tagArray
    });

    // Reset form
    setContent("");
    setTags("");
    onClose();
  };

  const suggestedTags = [
    "taktik", "teknik", "fiziksel", "mental", "geçiş", "savunma", 
    "hücum", "pressing", "pozisyon", "karar", "tempo", "iletişim"
  ];

  const addSuggestedTag = (tag: string) => {
    const currentTags = tags.split(',').map(t => t.trim()).filter(Boolean);
    if (!currentTags.includes(tag)) {
      const newTags = [...currentTags, tag].join(', ');
      setTags(newTags);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl bg-surface border border-white/20 p-6 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-white">Not Ekle</h2>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all flex items-center justify-center"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="p-3 rounded-lg bg-accent/10 border border-accent/30">
            <div className="text-sm font-medium text-accent mb-1">
              📍 Zaman: {formatTime(currentTime)}
            </div>
            <div className="text-xs text-text-muted">
              Bu not video üzerinde bu zaman damgasıyla kaydedilecek
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Not İçeriği *
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Gözleminizi, analiz notunuzu veya önerinizi buraya yazın..."
              rows={4}
              className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-text-muted resize-none"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Etiketler
            </label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="taktik, teknik, pozisyon (virgülle ayırın)"
              className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-text-muted"
            />
            
            <div className="mt-2">
              <div className="text-xs text-text-muted mb-2">Önerilen etiketler:</div>
              <div className="flex gap-1 flex-wrap">
                {suggestedTags.map(tag => (
                  <button
                    key={tag}
                    type="button"
                    onClick={() => addSuggestedTag(tag)}
                    className="px-2 py-1 rounded text-xs bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all"
                  >
                    #{tag}
                  </button>
                ))}
              </div>
            </div>
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
              disabled={!content.trim()}
              className="flex-1 px-4 py-2.5 rounded-xl text-sm font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              📝 Kaydet
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}