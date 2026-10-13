"use client";

import React, { useState } from "react";
import Link from "next/link";

import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ConfidenceBadge } from "@/components/ui/ConfidenceBadge";
import { SeverityBadge } from "@/components/ui/SeverityBadge";
import { Modal } from "@/components/ui/Modal";
import { Toast, type ToastItem } from "@/components/ui/Toast";
import { ProcessingStep, type ProcessingStepItem } from "@/components/ui/ProcessingStep";
import { FilterBar } from "@/components/ui/FilterBar";
import { UploadDropzone } from "@/components/ui/UploadDropzone";

// ── Reusable action button ────────────────────────────────────────────────────
function Btn({
  label,
  primary = true,
  href,
  onClick,
}: {
  label: string;
  primary?: boolean;
  href?: string;
  onClick?: () => void;
}) {
  const cls = primary
    ? "px-4 py-2 text-sm font-semibold rounded-xl bg-emerald-600 text-white hover:bg-emerald-500 shadow-lg shadow-emerald-900/20 transition-all"
    : "px-4 py-2 text-sm font-semibold rounded-xl bg-white/5 border border-white/10 text-text-soft hover:text-white hover:border-white/20 transition-all";

  if (href) return <Link href={href} className={cls}>{label}</Link>;
  return <button onClick={onClick} className={cls}>{label}</button>;
}

// ── Section wrapper ───────────────────────────────────────────────────────────
function Section({ num, title, children }: { num: string; title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-4">
      <h2 className="text-lg font-semibold text-white flex items-center gap-2">
        <span className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-sm font-mono">
          {num}
        </span>
        {title}
      </h2>
      <div className="grid gap-6 md:grid-cols-2">{children}</div>
    </section>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────
export default function UiStatesPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const push = (t: Omit<ToastItem, "id">) =>
    setToasts((prev) => [...prev, { ...t, id: String(Date.now()) }]);

  return (
    <div className="space-y-14 pb-20">
      {/* Header */}
      <div>
        <div className="text-sm font-medium text-emerald-400">UI States Showcase</div>
        <h1 className="mt-1 text-3xl font-bold text-white">Boş & Hata Durumları</h1>
        <p className="mt-2 text-sm text-text-muted">
          PitchVision Lite genelinde kullanılan tüm empty state ve error state bileşenleri.
        </p>
      </div>

      {/* ── 01 Maçlar ── */}
      <Section num="01" title="Maçlar">
        <EmptyState
          title="Henüz maç yok"
          description="Analiz etmek istediğin maç videolarını yükleyerek başlayabilirsin."
          icon="⚽"
          action={<Btn label="Yeni Maç Yükle" href="/matches/new" />}
        />
        <EmptyState
          title="Filtreye uygun maç yok"
          description="Seçili tarih aralığında veya kriterlerde maç kaydı bulunamadı. Filtreleri kontrol et."
          icon="�"
          action={<Btn label="Filtreleri Temizle" primary={false} />}
        />
      </Section>

      {/* ── 02 Upload ── */}
      <Section num="02" title="Upload">
        <EmptyState
          title="Upload bekleniyor"
          description="Analiz sürecini başlatmak için bir video dosyası seç veya sürükleyip bırak."
          icon="📤"
          action={<Btn label="Dosya Seç" />}
        />
        <ErrorState
          title="Upload başarısız"
          description="İnternet bağlantını kontrol et veya dosyayı tekrar yüklemeyi dene."
          icon="📡"
          action={<Btn label="Yeniden Dene" />}
        />
        <ErrorState
          title="Dosya formatı desteklenmiyor"
          description="Lütfen .mp4, .mov veya .avi formatında bir video dosyası yükle."
          icon="📁"
          action={<Btn label="Dosyayı Değiştir" />}
        />
        <ErrorState
          title="Dosya çok büyük"
          description="Ücretsiz planda maksimum dosya boyutu 2 GB'dır. Videoyu sıkıştır veya planını yükselt."
          icon="⚖️"
          action={<Btn label="Planı Yükselt" />}
          secondaryAction={<Btn label="Anladım" primary={false} />}
        />
      </Section>

      {/* ── 03 Processing ── */}
      <Section num="03" title="Processing">
        <EmptyState
          title="Analiz devam ediyor"
          description="Video işleme ve metrik hesaplama süreci devam ediyor. Tamamlandığında bildirim alacaksın."
          icon="⚙️"
          action={<Btn label="Durumu Görüntüle" primary={false} />}
        />
        <ErrorState
          title="Analiz başarısız oldu"
          description="Sunucu kaynaklı bir hata oluştu. Analiz sürecini tekrar başlatmayı deneyebilirsin."
          icon="❌"
          action={<Btn label="Süreci Yeniden Başlat" />}
        />
        <EmptyState
          title="Yeniden dene"
          description="Önceki analiz tamamlanamadı. Videoyu ve kalibrasyon ayarlarını kontrol ettikten sonra tekrar başlatabilirsin."
          icon="�"
          action={<Btn label="Analizi Başlat" />}
          secondaryAction={<Btn label="Kalibrasyona Git" primary={false} />}
        />
      </Section>

      {/* ── 04 Kalibrasyon ── */}
      <Section num="04" title="Kalibrasyon">
        <EmptyState
          title="Kalibrasyon yapılmadı"
          description="Maç videosundan saha koordinatları çıkarılabilmesi için önce saha noktalarını işaretlemen gerekiyor."
          icon="📐"
          action={<Btn label="Saha Kalibrasyonuna Git" />}
        />
        <ErrorState
          title="Nokta sayısı yetersiz"
          description="Saha sınırlarını belirlemek için en az 4 geçerli köşe noktası işaretlenmelidir."
          icon="📍"
          action={<Btn label="Noktaları Düzenle" />}
        />
        <ErrorState
          title="Homografi kalitesi düşük"
          description="İşaretlenen noktalar arasında perspektif uyumsuzluğu var. Noktaların doğruluğunu kontrol et."
          icon="�"
          action={<Btn label="Kalibrasyonu Kontrol Et" />}
        />
        <ErrorState
          title="Saha çizgileri görünmüyor"
          description="Görüntü kalitesi veya ışık nedeniyle saha çizgileri tespit edilemiyor. Manuel kalibrasyon gerekebilir."
          icon="🚫"
          action={<Btn label="Manuel Modu Aç" />}
        />
      </Section>

      {/* ── 05 Video Analiz ── */}
      <Section num="05" title="Video Analiz">
        <EmptyState
          title="Video işlenmedi"
          description="Bu maç için henüz video analizi çalıştırılmadı. Önce işleme adımını tamamla."
          icon="�"
          action={<Btn label="İşlemeye Git" />}
        />
        <ErrorState
          title="Tracking güven skoru düşük"
          description="Video kalitesi nedeniyle oyuncu takibi düşük doğrulukla yapılıyor. Metrikler sapma gösterebilir."
          icon="🎯"
          action={<Btn label="Yine de Devam Et" />}
          secondaryAction={<Btn label="İptal" primary={false} />}
        />
        <EmptyState
          title="Taktiksel uyarı bulunamadı"
          description="Bu maçta kural motorunun tetiklediği taktiksel uyarı tespit edilmedi."
          icon="⚡"
          action={<Btn label="Eşik Değerlerini Ayarla" primary={false} />}
        />
        <EmptyState
          title="Klip yok"
          description="Bu maça ait etiketlenmiş video klibi mevcut değil. Analiz sırasında klip oluşturabilirsin."
          icon="✂️"
          action={<Btn label="Klip Oluştur" />}
        />
      </Section>

      {/* ── 06 Oyuncular ── */}
      <Section num="06" title="Oyuncular">
        <EmptyState
          title="Henüz oyuncu yok"
          description="Takımına oyuncu ekleyerek gelişim takiplerini ve analizleri başlatabilirsin."
          icon="👤"
          action={<Btn label="Oyuncu Ekle" />}
        />
        <EmptyState
          title="Filtreye uygun oyuncu yok"
          description="Seçili kriterlere uygun oyuncu bulunamadı. Filtreleri genişletmeyi dene."
          icon="👥"
          action={<Btn label="Filtreleri Sıfırla" primary={false} />}
        />
      </Section>

      {/* ── 07 Oyuncu Pasaportu ── */}
      <Section num="07" title="Oyuncu Pasaportu">
        <EmptyState
          title="Yeterli maç verisi yok"
          description="Bu oyuncu için gelişim trendi oluşturabilmek için en az 3 maç verisi gereklidir."
          icon="📈"
          action={<Btn label="Maç Verisi Ekle" />}
        />
        <EmptyState
          title="Henüz scout notu yok"
          description="Bu oyuncu için yapılmış bir gözlem bulunmuyor. İlk notunu ekle."
          icon="📝"
          action={<Btn label="Not Ekle" />}
        />
        <EmptyState
          title="Klip yok"
          description="Oyuncuya ait etiketlenmiş video klibi mevcut değil."
          icon="🎬"
          action={<Btn label="Klip Oluştur" />}
        />
      </Section>

      {/* ── 08 Scouting ── */}
      <Section num="08" title="Scouting">
        <EmptyState
          title="Filtreye uygun oyuncu yok"
          description="Arama kriterlerine uygun oyuncu kaydı bulunamadı. Filtreleri kontrol et."
          icon="🔍"
          action={<Btn label="Filtreleri Temizle" primary={false} />}
        />
        <EmptyState
          title="Scout notu yok"
          description="Henüz hiçbir oyuncu için gözlem notu eklenmemiş."
          icon="📋"
          action={<Btn label="İlk Notu Ekle" />}
        />
      </Section>

      {/* ── 09 Raporlar ── */}
      <Section num="09" title="Raporlar">
        <EmptyState
          title="Henüz rapor oluşturulmadı"
          description="Analiz tamamlandıktan sonra maç özeti ve detaylı raporlar burada listelenir."
          icon="📄"
          action={<Btn label="Analizi Başlat" />}
        />
        <ErrorState
          title="PDF export başarısız"
          description="Rapor oluşturulurken teknik bir hata oluştu. Tarayıcıyı yenileyip tekrar dene."
          icon="📑"
          action={<Btn label="Tekrar Dene" />}
          secondaryAction={<Btn label="Sayfayı Yenile" primary={false} onClick={() => window.location.reload()} />}
        />
      </Section>

      {/* ── Global Bileşenler ── */}
      <section className="space-y-8 pt-10 border-t border-white/10">
        <div>
          <h2 className="text-xl font-bold text-white">Global Bileşenler</h2>
          <p className="text-sm text-text-muted">Badges, Modals, Toasts ve daha fazlası.</p>
        </div>

        <div className="grid gap-8 md:grid-cols-2">
          <div className="space-y-4 rounded-2xl pv-card p-6">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Badge Seti</h3>
            <div className="flex flex-wrap gap-3">
              <StatusBadge status="completed" />
              <StatusBadge status="processing" />
              <StatusBadge status="scheduled" />
              <ConfidenceBadge value={0.82} />
              <SeverityBadge severity="high" />
              <SeverityBadge severity="medium" />
              <SeverityBadge severity="low" />
            </div>
          </div>

          <div className="space-y-4 rounded-2xl pv-card p-6">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Etkileşim</h3>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => setModalOpen(true)}
                className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-text-muted hover:text-white hover:border-emerald-400/40 transition-all"
              >
                Modal Aç
              </button>
              <button
                onClick={() => push({ title: "Başarılı", message: "İşlem başarıyla tamamlandı.", tone: "success" })}
                className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 transition-all"
              >
                Success Toast
              </button>
              <button
                onClick={() => push({ title: "Uyarı", message: "Lütfen verileri kontrol edin.", tone: "warning" })}
                className="rounded-xl bg-amber-600/20 border border-amber-600/40 px-4 py-2 text-sm font-semibold text-amber-500 hover:bg-amber-600/30 transition-all"
              >
                Warning Toast
              </button>
              <button
                onClick={() => push({ title: "Hata", message: "İşlem gerçekleştirilemedi.", tone: "danger" })}
                className="rounded-xl bg-red-600/20 border border-red-600/40 px-4 py-2 text-sm font-semibold text-red-400 hover:bg-red-600/30 transition-all"
              >
                Error Toast
              </button>
            </div>
          </div>
        </div>
      </section>

      <Modal open={modalOpen} title="Sistem Mesajı" onClose={() => setModalOpen(false)}>
        <div className="space-y-4">
          <p className="text-sm text-text-muted">
            Bu modal PitchVision Lite tasarım sistemindeki standart diyalog yapısını gösterir.
          </p>
          <div className="flex justify-end gap-3 mt-6">
            <button onClick={() => setModalOpen(false)} className="px-4 py-2 text-sm font-medium text-text-soft hover:text-white">
              İptal
            </button>
            <button onClick={() => setModalOpen(false)} className="px-6 py-2 text-sm font-bold bg-emerald-600 text-white rounded-xl">
              Onayla
            </button>
          </div>
        </div>
      </Modal>

      <Toast toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
    </div>
  );
}
