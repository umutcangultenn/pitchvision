"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";

import {
  DEMO_INTEREST_MODULES,
  DEMO_REQUEST_ROLES,
  PRICING_PLANS,
  type PlanId,
} from "@/lib/pricing";
import { apiPostDemoRequest } from "@/lib/api";

const AGE_GROUPS = ["U8", "U9", "U10", "U11", "U12", "U13", "U14", "U15", "U16", "U17", "U19", "A takımı"];

function inputClass() {
  return "w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none focus:border-emerald-500/50";
}

export default function DemoRequestPage() {
  const [planFromUrl, setPlanFromUrl] = useState<string | null>(null);
  const [intentFromUrl, setIntentFromUrl] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [doneRef, setDoneRef] = useState<string | null>(null);

  const [fullName, setFullName] = useState("");
  const [clubName, setClubName] = useState("");
  const [role, setRole] = useState("coach");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [interestModule, setInterestModule] = useState("full_platform");
  const [notes, setNotes] = useState("");
  const [ageSelected, setAgeSelected] = useState<string[]>([]);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    setPlanFromUrl(q.get("plan"));
    setIntentFromUrl(q.get("intent"));
  }, []);

  const planMeta = planFromUrl
    ? PRICING_PLANS.find((p) => p.id === (planFromUrl as PlanId))
    : undefined;

  const toggleAge = (a: string) => {
    setAgeSelected((prev) =>
      prev.includes(a) ? prev.filter((x) => x !== a) : [...prev, a]
    );
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !clubName.trim() || !email.trim()) return;
    setSubmitting(true);
    setDoneRef(null);
    const body = {
      full_name: fullName.trim(),
      club_name: clubName.trim(),
      role,
      email: email.trim(),
      phone: phone.trim(),
      age_categories: ageSelected.length ? ageSelected.join(", ") : "Belirtilmedi",
      interest_module: interestModule,
      notes: notes.trim(),
      plan_interest: planFromUrl,
      intent: intentFromUrl,
    };
    const res = await apiPostDemoRequest(body);
    setSubmitting(false);
    setDoneRef(res?.reference ?? "DEMO-LOCAL");
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <Link href="/pricing" className="text-sm font-medium text-emerald-200/80 hover:text-emerald-100">
          ← Planlara dön
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-white">Demo talep formu</h1>
        <p className="mt-2 text-sm text-text-muted">
          Ekibimiz size özel kısa bir oturum planlar. Zorunlu alanlar minimum tutuldu; geri kalanını
          birlikte netleştiririz.
        </p>
      </div>

      {planMeta ? (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-100">
          Seçtiğiniz plan: <strong className="text-white">{planMeta.name}</strong>
          {intentFromUrl === "select" ? (
            <span className="text-emerald-200/80"> — plan seçimi notu iletilecek.</span>
          ) : null}
        </div>
      ) : null}

      {doneRef ? (
        <div className="rounded-2xl border border-emerald-500/40 bg-emerald-950/40 p-5 text-sm text-emerald-100">
          <p className="font-semibold text-white">Teşekkürler!</p>
          <p className="mt-2 text-text-muted">
            Talebiniz alındı. Referans kodunuz: <span className="font-mono text-white">{doneRef}</span>
          </p>
          <p className="mt-2 text-text-muted">
            En geç 1–2 iş günü içinde e-posta veya telefon ile dönüş yapılır.
          </p>
          <Link
            href="/dashboard"
            className="mt-4 inline-block text-sm font-semibold text-emerald-300 hover:text-emerald-200"
          >
            Panele dön →
          </Link>
        </div>
      ) : (
        <form onSubmit={submit} className="space-y-5 rounded-2xl pv-card p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block space-y-1.5 text-sm sm:col-span-2">
              <span className="text-text-muted">Ad soyad *</span>
              <input
                required
                className={inputClass()}
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="ör. Ayşe Yılmaz"
              />
            </label>
            <label className="block space-y-1.5 text-sm sm:col-span-2">
              <span className="text-text-muted">Kulüp / kurum *</span>
              <input
                required
                className={inputClass()}
                value={clubName}
                onChange={(e) => setClubName(e.target.value)}
                placeholder="ör. Yeşilova SK Akademi"
              />
            </label>
            <label className="block space-y-1.5 text-sm">
              <span className="text-text-muted">Rolünüz</span>
              <select className={inputClass()} value={role} onChange={(e) => setRole(e.target.value)}>
                {DEMO_REQUEST_ROLES.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="block space-y-1.5 text-sm">
              <span className="text-text-muted">E-posta *</span>
              <input
                required
                type="email"
                className={inputClass()}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="siz@kulup.com"
              />
            </label>
            <label className="block space-y-1.5 text-sm sm:col-span-2">
              <span className="text-text-muted">Telefon</span>
              <input
                className={inputClass()}
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+90 …"
              />
            </label>
          </div>

          <div>
            <div className="text-sm text-text-muted">Yaş kategorileri (birden fazla seçebilirsiniz)</div>
            <div className="mt-2 flex flex-wrap gap-2">
              {AGE_GROUPS.map((a) => (
                <button
                  key={a}
                  type="button"
                  onClick={() => toggleAge(a)}
                  className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                    ageSelected.includes(a)
                      ? "border-emerald-400/50 bg-emerald-500/20 text-emerald-100"
                      : "border-white/10 bg-white/5 text-text-muted hover:border-white/20"
                  }`}
                >
                  {a}
                </button>
              ))}
            </div>
          </div>

          <label className="block space-y-1.5 text-sm">
            <span className="text-text-muted">İlgilendiğiniz modül</span>
            <select
              className={inputClass()}
              value={interestModule}
              onChange={(e) => setInterestModule(e.target.value)}
            >
              {DEMO_INTEREST_MODULES.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </label>

          <label className="block space-y-1.5 text-sm">
            <span className="text-text-muted">Not</span>
            <textarea
              rows={4}
              className={inputClass()}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Örn. haftada kaç maç işliyorsunuz, mevcut video altyapınız, entegrasyon beklentiniz…"
            />
          </label>

          <div className="flex flex-wrap gap-3 pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-500 disabled:opacity-50"
            >
              {submitting ? "Gönderiliyor…" : "Talebi gönder"}
            </button>
            <Link
              href="/pricing"
              className="inline-flex items-center rounded-xl border border-white/15 px-5 py-2.5 text-sm text-text-muted hover:text-white"
            >
              Vazgeç
            </Link>
          </div>
        </form>
      )}
    </div>
  );
}
