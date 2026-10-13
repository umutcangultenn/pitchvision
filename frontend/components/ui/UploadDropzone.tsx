"use client";

import React, { useRef, useState } from "react";

export function UploadDropzone({
  onFileSelected,
  title = "Video yükle",
}: {
  title?: string;
  onFileSelected?: (file: File) => void;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [dragOver, setDragOver] = useState(false);

  return (
    <div
      className={`rounded-2xl border-2 px-6 py-10 text-center transition ${
        dragOver ? "border-accent/60 bg-accent/10" : "border-white/10 bg-white/5"
      }`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files?.[0];
        if (file) onFileSelected?.(file);
      }}
    >
      <div className="text-sm font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm text-text-muted">
        Sürükle-bırak veya seçerek yükleyin. (Mock demo)
      </div>
      <div className="mt-5">
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept="video/*"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onFileSelected?.(file);
          }}
        />
        <button
          onClick={() => inputRef.current?.click()}
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
        >
          Dosya Seç
        </button>
      </div>
    </div>
  );
}

