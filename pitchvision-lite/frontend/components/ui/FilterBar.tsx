"use client";

import React from "react";

export function FilterBar({
  left,
  right,
}: {
  left?: React.ReactNode;
  right?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-3 rounded-xl pv-card p-4 md:flex-row md:items-center md:justify-between">
      <div className="flex items-center gap-3">{left}</div>
      <div className="flex items-center gap-3">{right}</div>
    </div>
  );
}

