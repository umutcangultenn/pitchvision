"use client";

import Link from "next/link";
import React from "react";

import { OrgTeamSeasonSelector } from "@/components/layout/OrgTeamSeasonSelector";

function BellIcon() {
  return (
    <svg className="h-5 w-5 text-text-muted" viewBox="0 0 24 24" fill="none">
      <path
        d="M18 8a6 6 0 1 0-12 0c0 7-3 7-3 7h18s-3 0-3-7Z"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  );
}

export function Topbar({
  onHamburger,
}: {
  onHamburger: () => void;
}) {
  return (
    <header className="sticky top-0 z-30 border-b border-white/10 bg-bg/70 backdrop-blur">
      <div className="flex items-center justify-between gap-4 px-4 py-3 md:px-6">
        <div className="flex items-center gap-3">
          <button
            onClick={onHamburger}
            className="inline-flex items-center justify-center rounded-xl border border-white/10 bg-white/5 p-2 text-white md:hidden"
            aria-label="Menü"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none">
              <path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
          </button>
          <div className="hidden md:block">
            <OrgTeamSeasonSelector />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/pricing"
            className="hidden rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-text-muted hover:border-emerald-400/30 hover:text-white lg:inline-flex"
          >
            Planlar
          </Link>
          <Link
            href="/demo-request"
            className="hidden rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-text-muted hover:border-emerald-400/30 hover:text-white sm:inline-flex"
          >
            Demo
          </Link>
          <button className="hidden sm:inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-text-muted hover:border-emerald-400/30 hover:text-white">
            <BellIcon />
            Bildirim
          </button>
          <button className="hidden sm:inline-flex rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-text-muted hover:border-emerald-400/30 hover:text-white">
            Yardım
          </button>
          <button className="hidden sm:inline-flex rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-text-muted hover:border-emerald-400/30 hover:text-white">
            Profil
          </button>

          <Link
            href="/matches/new"
            className="inline-flex items-center justify-center rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500"
          >
            Yeni Maç Yükle
          </Link>
        </div>
      </div>

      <div className="px-4 pb-3 md:hidden">
        <OrgTeamSeasonSelector />
      </div>
    </header>
  );
}

