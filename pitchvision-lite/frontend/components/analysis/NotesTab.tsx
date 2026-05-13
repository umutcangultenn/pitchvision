"use client";

import React, { useState } from "react";

type Note = {
  id: string;
  timestamp: number;
  content: string;
  author: string;
  createdAt: string;
  tags?: string[];
};

type NotesTabProps = {
  notes: Note[];
  onAddNote?: (content: string, timestamp: number, tags: string[]) => void;
  onDeleteNote?: (noteId: string) => void;
  currentTime?: number;
};

export function NotesTab({ notes, onAddNote, onDeleteNote, currentTime = 0 }: NotesTabProps) {
  const [newNote, setNewNote] = useState("");
  const [newTags, setNewTags] = useState("");
  const [isAdding, setIsAdding] = useState(false);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAddNote = () => {
    if (!newNote.trim()) return;
    
    const tags = newTags.split(',').map(tag => tag.trim()).filter(Boolean);
    onAddNote?.(newNote.trim(), currentTime, tags);
    setNewNote("");
    setNewTags("");
    setIsAdding(false);
  };

  const getTagColor = (tag: string) => {
    const colors = [
      "bg-accent/20 text-accent border-accent/30",
      "bg-success/20 text-success border-success/30",
      "bg-warning/20 text-warning border-warning/30",
      "bg-danger/20 text-danger border-danger/30",
    ];
    const index = tag.length % colors.length;
    return colors[index];
  };

  const sortedNotes = [...notes].sort((a, b) => b.timestamp - a.timestamp);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold text-white">Analiz Notları</div>
        <button
          onClick={() => setIsAdding(!isAdding)}
          className="px-3 py-1.5 rounded-lg text-xs font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all"
        >
          {isAdding ? "❌ İptal" : "📝 Not Ekle"}
        </button>
      </div>

      {/* Add note form */}
      {isAdding && (
        <div className="p-4 rounded-lg border border-accent/30 bg-accent/10 space-y-3">
          <div className="text-sm font-medium text-accent">
            Yeni Not ({formatTime(currentTime)})
          </div>
          
          <textarea
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            placeholder="Notunuzu buraya yazın..."
            className="w-full h-20 px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-text-muted resize-none"
          />
          
          <input
            type="text"
            value={newTags}
            onChange={(e) => setNewTags(e.target.value)}
            placeholder="Etiketler (virgülle ayırın)"
            className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-text-muted"
          />
          
          <div className="flex gap-2">
            <button
              onClick={handleAddNote}
              disabled={!newNote.trim()}
              className="px-4 py-2 rounded-lg text-sm font-medium bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              💾 Kaydet
            </button>
            <button
              onClick={() => {
                setNewNote("");
                setNewTags("");
                setIsAdding(false);
              }}
              className="px-4 py-2 rounded-lg text-sm font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all"
            >
              İptal
            </button>
          </div>
        </div>
      )}

      {/* Notes list */}
      <div className="space-y-3 max-h-80 overflow-y-auto">
        {sortedNotes.map(note => (
          <div
            key={note.id}
            className="p-4 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 transition-all"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="text-xs px-2 py-1 rounded bg-accent/20 text-accent">
                  {formatTime(note.timestamp)}
                </div>
                <div className="text-xs text-text-muted">
                  {note.author} • {new Date(note.createdAt).toLocaleDateString("tr-TR")}
                </div>
              </div>
              <button
                onClick={() => onDeleteNote?.(note.id)}
                className="text-xs text-danger hover:text-danger/80 transition-all"
              >
                🗑️
              </button>
            </div>

            <div className="text-sm text-white mb-3 leading-relaxed">
              {note.content}
            </div>

            {note.tags && note.tags.length > 0 && (
              <div className="flex gap-2 flex-wrap">
                {note.tags.map((tag, index) => (
                  <span
                    key={index}
                    className={`text-xs px-2 py-1 rounded border ${getTagColor(tag)}`}
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {sortedNotes.length === 0 && !isAdding && (
        <div className="text-center py-8">
          <div className="text-4xl mb-2">📝</div>
          <div className="text-text-muted text-sm mb-2">Henüz not eklenmemiş</div>
          <div className="text-xs text-text-soft">Video analizi sırasında önemli gözlemlerinizi not alın</div>
        </div>
      )}
    </div>
  );
}