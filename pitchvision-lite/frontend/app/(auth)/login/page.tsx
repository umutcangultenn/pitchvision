"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

import Link from "next/link";

import { useAuthStore } from "@/lib/store";

export default function LoginPage() {
  const router = useRouter();
  const { setAuthenticated } = useAuthStore();
  const [email, setEmail] = useState("coach@anadolu-akademi.demo");
  const [password, setPassword] = useState("demo12345");

  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6">
      <div className="w-full max-w-md rounded-2xl pv-surface p-8 shadow-xl shadow-black/30">
        <div className="text-sm font-semibold text-emerald-200/90">PitchVision Lite</div>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-white">Giriş yap</h1>
        <p className="mt-2 text-sm text-text-muted">
          MVP demo: Kimlik doğrulama mock olarak çalışır. (Sonra backend JWT bağlanacak.)
        </p>

        <form
          className="mt-8 space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            setAuthenticated(true);
            router.push("/onboarding");
          }}
        >
          <div>
            <label htmlFor="email" className="block text-xs font-medium text-text-muted">
              E-posta
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              placeholder="ornek@kulup.com"
              autoComplete="email"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-xs font-medium text-text-muted">
              Parola
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="flex w-full items-center justify-center rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-500"
          >
            Devam et
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-text-muted">
          Backend bağlantısı gelince gerçek login akışı eklenecek.
          <Link href="/dashboard" className="ml-2 text-emerald-300 hover:underline">
            Doğrudan panele git
          </Link>
        </p>
      </div>
    </main>
  );
}

