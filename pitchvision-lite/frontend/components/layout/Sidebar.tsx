"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import React, { useMemo } from "react";

import { useAppStore } from "@/lib/appStore";
import { mockMatches, mockPlayers, mockOrganizations } from "@/data/demo";

type NavItem = {
  label: string;
  href: string;
  activeWhen: (pathname: string) => boolean;
};

function Icon({ name }: { name: string }) {
  // Basit inline ikon seti (Stitch benzeri görünüm).
  const common = "h-5 w-5 text-emerald-200/80";
  switch (name) {
    case "overview":
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none">
          <path d="M4 13h6V4H4v9Z" stroke="currentColor" strokeWidth="1.8" />
          <path d="M14 20h6V11h-6v9Z" stroke="currentColor" strokeWidth="1.8" />
          <path d="M14 4h6v5h-6V4Z" stroke="currentColor" strokeWidth="1.8" />
        </svg>
      );
    case "matches":
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none">
          <path d="M7 4h10l2 4-2 4H7L5 8l2-4Z" stroke="currentColor" strokeWidth="1.8" />
          <path d="M7 12h10l2 4-2 4H7l-2-4 2-4Z" stroke="currentColor" strokeWidth="1.8" />
        </svg>
      );
    case "video":
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none">
          <path d="M4 7a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7Z" stroke="currentColor" strokeWidth="1.8" />
          <path d="M17 10l4-2v8l-4-2v-2Z" fill="currentColor" opacity="0.85" />
        </svg>
      );
    case "players":
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none">
          <path d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Z" stroke="currentColor" strokeWidth="1.8" />
          <path d="M4 20a8 8 0 0 1 16 0" stroke="currentColor" strokeWidth="1.8" />
        </svg>
      );
    case "reports":
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none">
          <path d="M7 3h10l4 4v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" stroke="currentColor" strokeWidth="1.8" />
          <path d="M17 3v5h5" stroke="currentColor" strokeWidth="1.8" />
        </svg>
      );
    case "team":
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none">
          <path d="M8 11a4 4 0 1 0-4-4 4 4 0 0 0 4 4Z" stroke="currentColor" strokeWidth="1.8" />
          <path d="M16 11a4 4 0 1 0-4-4 4 4 0 0 0 4 4Z" stroke="currentColor" strokeWidth="1.8" />
          <path d="M2 21a8 8 0 0 1 12-6" stroke="currentColor" strokeWidth="1.8" />
          <path d="M14 21a8 8 0 0 0 8-6" stroke="currentColor" strokeWidth="1.8" />
        </svg>
      );
    case "drills":
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none">
          <path d="M12 2l3 7h7l-6 4 2 9-6-5-6 5 2-9-6-4h7l3-7Z" stroke="currentColor" strokeWidth="1.6" />
        </svg>
      );
    case "settings":
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none">
          <path d="M12 15a3 3 0 1 0-3-3 3 3 0 0 0 3 3Z" stroke="currentColor" strokeWidth="1.8" />
          <path
            d="M19.4 15a7.9 7.9 0 0 0 .1-1l2-1.3-2-3.4-2.3.4a7 7 0 0 0-1.7-1L13 3h-2l-.5 3.7a7 7 0 0 0-1.7 1l-2.3-.4-2 3.4L5.6 14a7.9 7.9 0 0 0 .1 1l-2 1.3 2 3.4 2.3-.4a7 7 0 0 0 1.7 1L11 21h2l.5-3.7a7 7 0 0 0 1.7-1l2.3.4 2-3.4-2.1-1.3Z"
            stroke="currentColor"
            strokeWidth="1.2"
          />
        </svg>
      );
    case "pricing":
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none">
          <path
            d="M7 7h10v10H7V7Z"
            stroke="currentColor"
            strokeWidth="1.7"
            strokeLinejoin="round"
          />
          <path d="M9 3v4M15 3v4M9 17v4M15 17v4M3 9h4M17 9h4M3 15h4M17 15h4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
        </svg>
      );
    default:
      return <span className={common} />;
  }
}

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const pathname = usePathname();
  const { teamId } = useAppStore();
  const firstPlayer = mockPlayers[0]?.id;
  const org = mockOrganizations[0];
  const firstMatch = mockMatches.find((m) => m.teamId === teamId) ?? mockMatches[0];

  const items = useMemo(() => {
    const analysisHref = firstMatch?.id ? `/matches/${firstMatch.id}/analysis` : `/matches/1001/analysis`;
    const passportHref = firstPlayer ? `/players/${firstPlayer}` : `/players`;
    const teamHref = teamId ? `/teams/${teamId}` : `/teams/1`;

    return [
      { label: "Genel Bakış", href: "/dashboard", activeWhen: (p: string) => p === "/dashboard", icon: "overview" },
      {
        label: "Maçlar",
        href: "/matches",
        activeWhen: (p: string) => p.startsWith("/matches"),
        icon: "matches",
      },
      {
        label: "Video Analiz",
        href: analysisHref,
        activeWhen: (p: string) => p.includes("/analysis") || p.includes("/processing"),
        icon: "video",
      },
      { label: "Oyuncular", href: "/players", activeWhen: (p: string) => p === "/players", icon: "players" },
      { label: "Oyuncu Pasaportları", href: passportHref, activeWhen: (p: string) => /^\/players\/[^/]+$/.test(p), icon: "players" },
      { label: "Scouting", href: "/scouting", activeWhen: (p: string) => p.startsWith("/scouting"), icon: "matches" },
      { label: "Raporlar", href: "/reports", activeWhen: (p: string) => p.startsWith("/reports"), icon: "reports" },
      { label: "Takımlar", href: teamHref, activeWhen: (p: string) => p.startsWith("/teams/"), icon: "team" },
      { label: "Antrenman Önerileri", href: "/drills", activeWhen: (p: string) => p.startsWith("/drills"), icon: "drills" },
      { label: "Planlar", href: "/pricing", activeWhen: (p: string) => p.startsWith("/pricing"), icon: "pricing" },
      {
        label: "Demo talep",
        href: "/demo-request",
        activeWhen: (p: string) => p.startsWith("/demo-request"),
        icon: "video",
      },
      { label: "Ayarlar", href: "/settings", activeWhen: (p: string) => p.startsWith("/settings"), icon: "settings" },
    ];
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [firstMatch?.id, firstPlayer, teamId]);

  const drawer = (
    <div className="flex h-full flex-col gap-6 px-4 py-5">
      <div className="pv-card rounded-2xl p-4">
        <div className="text-sm font-semibold text-white">{org?.name}</div>
        <div className="mt-1 text-xs text-text-muted">PitchVision Lite</div>
      </div>

      <nav className="space-y-2">
        {items.map((it) => {
          const active = it.activeWhen(pathname ?? "");
          return (
            <Link
              key={it.href + it.label}
              href={it.href}
              onClick={onClose}
              className={`flex items-center gap-3 rounded-xl border px-3 py-2 text-sm transition ${
                active ? "border-emerald-400/40 bg-emerald-500/10" : "border-white/10 bg-white/5 hover:border-emerald-400/30"
              }`}
            >
              <Icon name={it.icon} />
              <span className={`${active ? "text-white" : "text-text-muted"} font-semibold`}>{it.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto rounded-2xl border border-white/10 bg-white/5 p-4">
        <div className="text-xs text-text-muted">Kısayol</div>
        <div className="mt-2 text-sm font-semibold text-white">Yeni Maç Yükle</div>
        <div className="mt-2 text-xs text-text-muted">Ctrl + U (demo)</div>
      </div>
    </div>
  );

  return (
    <>
      <div className={`fixed inset-0 z-40 bg-black/50 ${open ? "block" : "hidden"} md:hidden`} onClick={onClose} />
      <aside
        className={`fixed left-0 top-0 z-50 h-full w-72 bg-bg border-r border-white/10 transition-transform md:relative md:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {drawer}
      </aside>
    </>
  );
}

