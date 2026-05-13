"use client";

import React, { useState } from "react";

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

export default function UiStatesPage() {
  const [open, setOpen] = useState(false);
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const pushToast = (t: Omit<ToastItem, "id">) => {
    setToasts((prev) => [...prev, { ...t, id: String(Date.now()) }]);
  };

  const ActionBtn = ({ label, primary = true, onClick }: { label: string; primary?: boolean; onClick?: () => void }) => (
    <button
      onClick={onClick}
      className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all ${
        primary
          ? "bg-emerald-600 text-white hover:bg-emerald-500 shadow-lg shadow-emerald-900/20"
          : "bg-white/5 border border-white/10 text-text-soft hover:text-white hover:border-white/20"
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="space-y-12 pb-20">
      <div>
        <div className="text-sm font-medium text-emerald-400">UI States & Feedback System</div>
        <h1 className="mt-1 text-3xl font-bold text-white">Bileşen Durumları ve Bildirimler</h1>
        <p className="mt-2 text-sm text-text-muted">PitchVision Lite genelinde kullanılan boş durum (empty), hata (error) ve geri bildirim bileşenleri.</p>
      </div>

      {/* 1. Maçlar & Upload */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-sm">01</span>
          Maçlar & Yükleme
        </h2>
        <div className="grid gap-6 md:grid-cols-2">
          <EmptyState
            title="Henüz maç yok"
            description="Analiz etmek istediğiniz maç videolarını yükleyerek başlayabilirsiniz."
            icon="⚽"
            action={<ActionBtn label="Yeni Maç Yükle" />}
          />
          <EmptyState
            title="Filtreye uygun maç bulunamadı"
            description="Seçili tarih aralığında veya kriterlerde maç kaydı yok. Lütfen filtreleri kontrol edin."
            icon="🔍"
            action={<ActionBtn label="Filtreleri Temizle" primary={false} />}
          />
          <EmptyState
            title="Yükleme bekleniyor"
            description="Analiz sürecini başlatmak için bir video dosyası seçin veya sürükleyip bırakın."
            icon="📤"
            action={<ActionBtn label="Dosya Seç" />}
          />
          <ErrorState
            title="Yükleme başarısız"
            description="İnternet bağlantınızı kontrol edin veya dosyayı tekrar yüklemeyi deneyin."
            icon="📡"
            action={<ActionBtn label="Yeniden Dene" />}
          />
          <ErrorState
            title="Dosya formatı desteklenmiyor"
            description="Lütfen .mp4, .mov veya .avi formatında bir video dosyası yükleyin."
            icon="📁"
            action={<ActionBtn label="Dosyayı Değiştir" />}
          />
          <ErrorState
            title="Dosya çok büyük"
            description="Ücretsiz planda maksimum dosya boyutu 2GB'dır. Lütfen videoyu sıkıştırın veya planınızı yükseltin."
            icon="⚖️"
            action={<ActionBtn label="Planı Yükselt" />}
            secondaryAction={<ActionBtn label="Anladım" primary={false} />}
          />
        </div>
      </section>

      {/* 2. Analiz & Kalibrasyon */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-sm">02</span>
          Analiz & Kalibrasyon
        </h2>
        <div className="grid gap-6 md:grid-cols-2">
          <EmptyState
            title="Analiz devam ediyor"
            description="Video işleme ve metrik hesaplama süreci devam ediyor. Tamamlandığında bildirim alacaksınız."
            icon="⚙️"
            action={<ActionBtn label="Durumu Görüntüle" primary={false} />}
          />
          <ErrorState
            title="Analiz başarısız oldu"
            description="Sunucu kaynaklı bir hata oluştu. Analiz sürecini tekrar başlatmayı deneyebilirsiniz."
            icon="❌"
            action={<ActionBtn label="Süreci Yeniden Başlat" />}
          />
          <EmptyState
            title="Kalibrasyon yapılmadı"
            description="Maç videosundan saha koordinatları çıkarılabilmesi için önce saha noktalarını işaretlemen gerekiyor."
            icon="📐"
            action={<ActionBtn label="Saha Kalibrasyonuna Git" />}
          />
          <ErrorState
            title="Kalibrasyon noktaları yetersiz"
            description="Saha sınırlarını belirlemek için en az 4 geçerli köşe noktası işaretlenmelidir."
            icon="📍"
            action={<ActionBtn label="Noktaları Düzenle" />}
          />
          <ErrorState
            title="Homografi kalitesi düşük"
            description="İşaretlenen noktalar arasında perspektif uyumsuzluğu var. Lütfen noktaların doğruluğunu kontrol edin."
            icon="📉"
            action={<ActionBtn label="Kalibrasyonu Kontrol Et" />}
          />
          <ErrorState
            title="Saha çizgileri görünmüyor"
            description="Görüntü kalitesi veya ışık nedeniyle saha çizgileri tespit edilemiyor. Manuel kalibrasyon gerekebilir."
            icon="🚫"
            action={<ActionBtn label="Manuel Modu Aç" />}
          />
        </div>
      </section>

      {/* 3. Oyuncular & Scouting */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-sm">03</span>
          Oyuncular & Scouting
        </h2>
        <div className="grid gap-6 md:grid-cols-2">
          <EmptyState
            title="Henüz oyuncu yok"
            description="Takımınıza oyuncu ekleyerek gelişim takiplerini ve analizleri başlatabilirsiniz."
            icon="👤"
            action={<ActionBtn label="Oyuncu Ekle" />}
          />
          <EmptyState
            title="Filtreye uygun oyuncu yok"
            description="Seçili kriterlere uygun oyuncu bulunamadı. Filtreleri genişletmeyi deneyin."
            icon="👥"
            action={<ActionBtn label="Filtreleri Sıfırla" primary={false} />}
          />
          <EmptyState
            title="Yeterli maç verisi yok"
            description="Bu oyuncu için gelişim trendi oluşturabilmek için en az 3 maç verisi gereklidir."
            icon="📈"
            action={<ActionBtn label="Maç Verisi Ekle" />}
          />
          <EmptyState
            title="Henüz scout notu yok"
            description="Bu oyuncu için yapılmış bir gözlem bulunmuyor. İlk notunuzu ekleyin."
            icon="📝"
            action={<ActionBtn label="Not Ekle" />}
          />
          <EmptyState
            title="Klip bulunamadı"
            description="Oyuncuya ait etiketlenmiş video klibi mevcut değil."
            icon="🎬"
            action={<ActionBtn label="Klip Oluştur" />}
          />
        </div>
      </section>

      {/* 4. Raporlar & Diğer */}
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-sm">04</span>
          Raporlar & Diğer
        </h2>
        <div className="grid gap-6 md:grid-cols-2">
          <EmptyState
            title="Henüz rapor oluşturulmadı"
            description="Analiz tamamlandıktan sonra maç özeti ve detaylı raporlar burada listelenir."
            icon="📄"
            action={<ActionBtn label="Analizi Başlat" />}
          />
          <ErrorState
            title="PDF export başarısız"
            description="Rapor oluşturulurken teknik bir hata oluştu. Lütfen tarayıcıyı yenileyip tekrar deneyin."
            icon="📑"
            action={<ActionBtn label="Tekrar Dene" />}
          />
          <ErrorState
            title="Tracking güven skoru düşük"
            description="Video kalitesi nedeniyle oyuncu takibi düşük doğrulukla yapılıyor. Metrikler sapma gösterebilir."
            icon="🎯"
            action={<ActionBtn label="Yine de Devam Et" />}
            secondaryAction={<ActionBtn label="İptal" primary={false} />}
          />
        </div>
      </section>

      {/* UI Elements Showcase */}
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
                onClick={() => setOpen(true)}
                className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-text-muted hover:text-white hover:border-emerald-400/40 transition-all"
              >
                Modal Aç
              </button>
              <button
                onClick={() => pushToast({ title: "Başarılı", message: "İşlem başarıyla tamamlandı.", tone: "success" })}
                className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 transition-all"
              >
                Success Toast
              </button>
              <button
                onClick={() => pushToast({ title: "Uyarı", message: "Lütfen verileri kontrol edin.", tone: "warning" })}
                className="rounded-xl bg-amber-600/20 border border-amber-600/40 px-4 py-2 text-sm font-semibold text-amber-500 hover:bg-amber-600/30 transition-all"
              >
                Warning Toast
              </button>
            </div>
          </div>
        </div>
      </section>

      <Modal open={open} title="Sistem Mesajı" onClose={() => setOpen(false)}>
        <div className="space-y-4">
          <p className="text-sm text-text-muted">
            Bu modal PitchVision Lite tasarım sistemindeki standart diyalog yapısını gösterir. 
            İçerik buraya gelir ve aksiyon butonları aşağıda yer alır.
          </p>
          <div className="flex justify-end gap-3 mt-6">
            <button onClick={() => setOpen(false)} className="px-4 py-2 text-sm font-medium text-text-soft hover:text-white">İptal</button>
            <button onClick={() => setOpen(false)} className="px-6 py-2 text-sm font-bold bg-emerald-600 text-white rounded-xl">Onayla</button>
          </div>
        </div>
      </Modal>

      <Toast toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />
    </div>
  );
}

