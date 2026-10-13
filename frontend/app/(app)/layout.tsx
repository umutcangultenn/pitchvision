"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { useAuthStore } from "@/lib/store";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();

  // Redirect to login if not authenticated
  // We allow access in mock/dev mode (no backend) — isAuthenticated starts false
  // but zustand-persist will rehydrate it on mount.
  useEffect(() => {
    // Give zustand-persist time to rehydrate from localStorage
    const timer = setTimeout(() => {
      if (!isAuthenticated) {
        router.replace("/login");
      }
    }, 100);
    return () => clearTimeout(timer);
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-sm text-text-muted">Yükleniyor…</div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar onHamburger={() => setSidebarOpen(true)} />
        <div className="flex-1 px-4 py-6 md:px-6 md:py-8">{children}</div>
      </div>
    </div>
  );
}
