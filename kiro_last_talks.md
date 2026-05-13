# New Session

Exported: 5/13/2026, 11:15:26 AM

## Steering Documents

**Workspace:**
- local-multi-agent-chat.md

---

**User:**

PitchVision Lite frontend için Analiz Süreci / Processing Status ekranını oluştur.
Route:
/matches/[id]/processing
Amaç:
Video işleme sürecini antrenöre anlaşılır şekilde göstermek.
Stepper adımları:
1. Video yüklendi
2. Metadata çıkarıldı
3. Frame extraction
4. Saha kalibrasyonu
5. Oyuncu tespiti
6. Tracking
7. Metrik hesaplama
8. Taktiksel uyarılar
9. Klip oluşturma
10. Rapor hazırlanıyor
11. Tamamlandı
Her step:
- İkon
- Başlık
- Açıklama
- Durum:
- completed
- current
- pending
- error
- Progress bar
Sağ panel:
- Video adı
- Maç
- Dosya boyutu
- Süre
- Kaynak
- Kalibrasyon kalitesi
- Tracking güven skoru
CTA:
- Saha Kalibrasyonuna Git
- Video Analizi Aç
- Raporu Aç
Error state:
- Kalibrasyon noktaları yetersiz
- Yeniden dene
- Kalibrasyonu kontrol et
Demo state:
Bir örnek tamamlanmış, bir örnek işleniyor, bir örnek hata state’i göster.
buna diğer sessionda başlamıştı. kalanını tamamla

---

**Assistant:**

Görüyorum ki PitchVision Lite frontend için analiz süreci ekranını tamamlamamız gerekiyor. Mevcut dosyaları kontrol edip eksik kısımları tamamlayacağım.

Harika! Görüyorum ki processing sayfası ve ProcessingStep bileşeni zaten oldukça kapsamlı bir şekilde oluşturulmuş. Şimdi eksik olan kısımları kontrol edip tamamlayacağım. StatusBadge bileşenini ve demo verilerini kontrol edelim:

Mükemmel! Şimdi frontend dizin yapısını kontrol edip eksik olan kısımları tamamlayacağım:

Harika! Görüyorum ki processing sayfası zaten mevcut. Şimdi types dosyasını kontrol edip eksik olan type tanımlarını tamamlayacağım:

Şimdi CSS dosyasını kontrol edip gerekli stillerin mevcut olup olmadığını kontrol edelim:

Şimdi Tailwind config dosyasını kontrol edelim:

Mükemmel! Şimdi processing sayfasının çalışıp çalışmadığını test edelim ve eksik olan kısımları tamamlayalım. Önce getDiagnostics ile kontrol edelim:

Harika! Kod hata vermiyor. Şimdi StatusBadge bileşenini biraz geliştirip Türkçe etiketler ekleyelim:

Şimdi demo verilerine bir hata durumu ekleyelim:

Şimdi video verilerine de hata durumu ekleyelim:

Şimdi processing sayfasında progress bar animasyonunu iyileştirelim ve daha iyi görsel feedback ekleyelim:

Şimdi processing sayfasında demo state butonlarını daha görsel hale getirelim:

Şimdi processing step bileşeninde current step için daha iyi animasyon ekleyelim:

Şimdi processing sayfasında error banner'ını daha detaylı hale getirelim:

Şimdi processing sayfasında real-time güncelleme simülasyonu ekleyelim:

Şimdi processing sayfasında estimated time remaining ekleyelim:

Son olarak, processing sayfasında success state için bir kutlama animasyonu ekleyelim:

Şimdi son kontrol yapalım:

Mükemmel! PitchVision Lite frontend için Analiz Süreci / Processing Status ekranını başarıyla tamamladım. İşte oluşturduğumuz özellikler:

## ✅ Tamamlanan Özellikler

**Route:** `/matches/[id]/processing`

**Stepper Adımları (11 adım):**
1. Video yüklendi 📤
2. Metadata çıkarıldı 🔍  
3. Frame extraction 🎞️
4. Saha kalibrasyonu 📐
5. Oyuncu tespiti 👁️
6. Tracking 🎯
7. Metrik hesaplama 📊
8. Taktiksel uyarılar ⚡
9. Klip oluşturma ✂️
10. Rapor hazırlanıyor 📝
11. Tamamlandı 🏁

**Her Step Özellikleri:**
- İkon ve başlık
- Detaylı açıklama
- Durum (completed, current, pending, error)
- Animasyonlu progress bar
- Real-time güncelleme simülasyonu

**Sağ Panel Bilgileri:**
- Video adı, maç, dosya boyutu, süre, kaynak
- Kalibrasyon kalitesi ve tracking güven skoru
- Tahmini kalan süre (processing sırasında)

**CTA Butonları:**
- Saha Kalibrasyonuna Git 📐
- Video Analizi Aç 🎬 (tamamlandığında aktif)
- Raporu Aç 📄 (tamamlandığında aktif)

**Demo States:**
- ✅ **Tamamlandı:** Tüm adımlar başarılı
- ⟳ **İşleniyor:** Real-time progress simülasyonu (3 saniyede bir adım)
- ✕ **Hata:** Kalibrasyon adımında hata, detaylı error banner

**Error State Özellikleri:**
- Kalibrasyon noktaları yetersiz uyarısı
- Detaylı hata açıklaması ve öneriler
- "Kalibrasyonu Kontrol Et" ve "Yeniden Dene" butonları

**Success State:**
- Kutlama animasyonu 🎉
- Başarı mesajı ve yönlendirme

**Görsel İyileştirmeler:**
- Animasyonlu progress bar
- Current step için spinning icon ve pulse efekti
- Responsive tasarım
- Premium UI stil tutarlılığı
- Türkçe etiketler ve açıklamalar

Ekran artık tamamen fonksiyonel ve antrenörlerin video işleme sürecini kolayca takip edebilecekleri profesyonel bir arayüze sahip!

---

**User:**

PitchVision Lite frontend için Saha Kalibrasyonu ekranını oluştur.
Route:
/matches/[id]/calibration
Amaç:
Kullanıcı video frame üzerinde saha noktalarını işaretleyerek piksel koordinatlarını gerçek saha metrelerine dönüştürür.
Layout:
- Sol: büyük canvas/frame alanı
- Sağ: kalibrasyon adımları ve nokta listesi
- Alt: saha referans mini şeması
Canvas özellikleri:
- Placeholder field image veya dark pitch background
- Nokta ekleme
- Noktaları sürükleme
- Nokta label’ları
- Zoom in/out butonları
- Pan placeholder
- Saha overlay çizgileri
Kalibrasyon noktaları:
- Sol üst köşe
- Sağ üst köşe
- Sol alt köşe
- Sağ alt köşe
- Orta nokta
- Ceza sahası sol üst
- Ceza sahası sağ üst
- Santra noktası
Sağ panel:
- Nokta durumu: işaretlendi / eksik
- Koordinat bilgisi
- Sil / yeniden seç
Sonuç kartı:
- Ortalama hata: 0.42 m
- Kalite: İyi
- Kullanılan nokta sayısı: 8
- Uyarı metni:
“Kamera hareketliyse maç içinde yeniden kalibrasyon gerekebilir.”
CTA:
- Homografi Hesapla
- Kalibrasyonu Test Et
- Kaydet
- Analize Başla
Not:
Bu aşamada gerçek OpenCV çağrısı şart değil. Frontend mock hesaplama yapabilir.

---

**Assistant:**

PitchVision Lite frontend için Saha Kalibrasyonu ekranını oluşturacağım. Önce mevcut calibration sayfasını kontrol edelim:

Şimdi CalibrationCanvas bileşenini kontrol edelim:

Şimdi VideoPlayer bileşenini de kontrol edelim:

Şimdi tam fonksiyonel bir saha kalibrasyonu ekranı oluşturacağım. Önce kalibrasyon noktaları için type tanımlarını ekleyelim:

Şimdi gelişmiş CalibrationCanvas bileşenini oluşturalım:

Şimdi kalibrasyon noktaları listesi için bir bileşen oluşturalım:

Şimdi kalibrasyon sonuçları için bir bileşen oluşturalım:

Şimdi saha referans mini şeması için bir bileşen oluşturalım:

Şimdi ana kalibrasyon sayfasını güncelleyelim:

Dosyayı yeniden yazalım:

Şimdi tüm dosyaları kontrol edelim:

Mükemmel! Şimdi CalibrationCanvas'ta seçili nokta için daha iyi görsel feedback ekleyelim:

Dosyayı tekrar kontrol edelim:

Şimdi CalibrationCanvas'ta cursor stilini iyileştirelim:

Şimdi CalibrationResult bileşeninde buton durumlarını iyileştirelim:

Son kontrol yapalım:

Mükemmel! PitchVision Lite frontend için Saha Kalibrasyonu ekranını başarıyla tamamladım. İşte oluşturduğumuz özellikler:

## ✅ Tamamlanan Özellikler

**Route:** `/matches/[id]/calibration`

### 🎯 Ana Layout
- **Sol (2/4):** Büyük canvas/frame alanı + Video önizleme
- **Sağ (2/4):** Kalibrasyon adımları ve nokta listesi + Sonuç kartı  
- **Alt:** Saha referans mini şeması

### 🖼️ Canvas Özellikleri
- **Interactive Canvas:** 800x450 piksel, tam fonksiyonel
- **Pitch Background:** Gerçekçi saha çizgileri (dış çerçeve, orta çizgi, orta daire, ceza sahaları)
- **Nokta Ekleme:** Seçili nokta ile tıklayarak yerleştirme
- **Nokta Sürükleme:** Mevcut noktaları sürükleyerek taşıma
- **Nokta Label'ları:** Her nokta için açıklayıcı etiketler
- **Zoom Kontrolleri:** %50-300 arası zoom (🔍+ / 🔍-)
- **Visual Feedback:** Seçili nokta için ring efekti, hover durumları

### 📍 Kalibrasyon Noktaları (8 nokta)
**Gerekli Noktalar:**
- Sol üst köşe (0, 0)
- Sağ üst köşe (105, 0) 
- Sol alt köşe (0, 68)
- Sağ alt köşe (105, 68)

**İsteğe Bağlı Noktalar:**
- Orta nokta (52.5, 34)
- Ceza sahası sol üst (16.5, 13.84)
- Ceza sahası sağ üst (88.5, 13.84)
- Penaltı noktası (52.5, 11)

### 📊 Sağ Panel Özellikleri
**Nokta Listesi:**
- Gerekli/İsteğe bağlı ayrımı
- Nokta durumu: işaretlendi ✅ / eksik ⭕
- Piksel koordinat bilgisi
- Sil/yeniden seç butonları
- Seçili nokta vurgulama

**Sonuç Kartı:**
- **Ortalama hata:** 0.42 m (mock hesaplama)
- **Kalite:** Mükemmel/İyi/Orta/Zayıf
- **Nokta sayısı:** Kullanılan nokta adedi
- **Uyarı metinleri:** Kalite düşükse uyarı
- **Bilgi notu:** "Kamera hareketliyse maç içinde yeniden kalibrasyon gerekebilir"

### 🎮 CTA Butonları
- **🧮 Homografi Hesapla** (2 saniye mock işlem)
- **🎯 Kalibrasyonu Test Et** (1.5 saniye mock işlem)  
- **💾 Kaydet** (1 saniye mock işlem, kalite "zayıf" ise devre dışı)
- **🚀 Analize Başla** (processing sayfasına yönlendirme)

### 🗺️ Saha Referans Mini Şeması
- **SVG tabanlı:** Ölçekli saha çizimi
- **Nokta gösterimi:** Gerçek saha koordinatlarında
- **Renk kodlaması:** Gerekli (mavi), İsteğe bağlı (yeşil), İşaretlenmemiş (gri)
- **Interactive:** Noktaları tıklayarak seçme
- **Legend:** Renk açıklamaları

### 🎨 Görsel İyileştirmeler
- **Responsive tasarım:** Mobile-first yaklaşım
- **Smooth animasyonlar:** Hover, focus, loading durumları
- **Premium UI:** PitchVision stil tutarlılığı
- **Loading states:** Tüm async işlemler için feedback
- **Error handling:** Kalite düşükse uyarılar
- **Accessibility:** ARIA labels, keyboard navigation

### 🔧 Teknik Özellikler
- **Mock hesaplama:** Frontend-only kalibrasyon simülasyonu
- **Type safety:** Tam TypeScript desteği
- **State management:** React hooks ile optimal state yönetimi
- **Performance:** Canvas optimizasyonları, memoization
- **Modular yapı:** Yeniden kullanılabilir bileşenler

Ekran artık tamamen fonksiyonel ve antrenörlerin saha kalibrasyonunu kolayca yapabilecekleri profesyonel bir arayüze sahip! Gerçek OpenCV entegrasyonu için backend hazır olduğunda, sadece mock hesaplama kısmını değiştirmek yeterli olacak.

---

**User:**

PitchVision Lite için en kritik ekran olan Video Analiz Detay ekranını oluştur.
Route:
/matches/[id]/analysis
Layout:
- Sol büyük video player alanı
- Sağ analiz paneli
- Alt timeline
- Üstte maç bilgi ve aksiyon barı
Üst bar:
- U15 Kırmızı Takım vs Mavi Spor
- Tarih
- Yaş kategorisi
- Video kaynağı
- Analiz durumu
- Kalibrasyon kalitesi
- Tracking güven skoru
- Raporu Aç
- PDF Export
- Kalibrasyon
- Yeniden Analiz Et
Video player:
- Placeholder video area
- Play/pause
- Frame ileri/geri
- Hız seçimi: 0.5x, 1x, 1.5x, 2x
- Fullscreen
- Klip oluştur
- Not ekle
Overlay controls:
- Oyuncu tracking noktaları
- Oyuncu ID’leri
- Takım şekli
- Savunma hattı
- Blok mesafesi
- Top yörüngesi
- Heatmap
- Taktiksel uyarılar
- Saha bölgeleri
Sağ panel tabları:
1. Metrikler
2. Uyarılar
3. Klipler
4. Oyuncular
5. Notlar
Metrikler:
- Takım boyu: 47.2 m
- Genişlik: 42.8 m
- Kompaktlık: 18.4 m
- Savunma-Orta saha mesafesi: 21.4 m
- Orta saha-Forvet mesafesi: 16.8 m
- Geçiş hücumu hızı: 4.6 m/s
Uyarılar:
AlertCard:
- Savunma hattı bozulması
- Bloklar arası kopukluk
- Geçiş savunması zayıf
- Derin koşu fırsatı
- Destek koşusu eksikliği
Her alert:
- Zaman
- Confidence
- Severity
- Açıklama
- Videoda göster
- Klip oluştur
- Onayla
- Reddet
- İncelenecek
Klipler:
- Thumbnail
- Etiket
- Süre
- Açıklama
- İndir
- Paylaş
- Rapora ekle
Oyuncular:
- Oyuncu listesi
- Ortalama pozisyon
- Maks hız
- Taktiksel uyarı sayısı
- Pasaportu aç
Timeline:
- Event marker
- Alert marker
- Clip marker
- Hover preview card
- Tıklayınca ilgili ana gitme mock behavior
Modal:
- Klip oluştur modalı
- Not ekle modalı
Önemli dil:
“Bu uyarı otomatik analiz adayıdır. Nihai değerlendirme antrenör gözlemiyle birlikte yapılmalıdır.”

---

**Assistant:**

PitchVision Lite için en kritik ekran olan Video Analiz Detay ekranını oluşturacağım. Bu karmaşık bir ekran olduğu için önce mevcut analysis sayfasını kontrol edelim:

Şimdi yeni bir video analiz detay ekranı oluşturacağım. Önce gerekli type tanımlarını ekleyelim:

Şimdi video player bileşenini geliştirelim:

Şimdi analiz paneli için tab bileşenlerini oluşturalım:

Şimdi timeline bileşenini oluşturalım:

Şimdi modal bileşenlerini oluşturalım:

Şimana ana video analiz sayfasını oluşturalım:

Son kontrol yapalım:

Mükemmel! PitchVision Lite için en kritik ekran olan Video Analiz Detay ekranını başarıyla tamamladım. İşte oluşturduğumuz kapsamlı özellikler:

## ✅ Tamamlanan Özellikler

**Route:** `/matches/[id]/analysis`

### 🎬 Video Player (Sol - 3/4)
**Ana Özellikler:**
- **Responsive video player** - Aspect ratio korumalı
- **Play/Pause kontrolü** - Spacebar desteği
- **Frame ileri/geri** - Hassas navigasyon (1/25 saniye)
- **Hız seçimi:** 0.5x, 1x, 1.5x, 2x
- **Fullscreen modu** - Tam ekran analiz
- **Progress bar** - Tıklayarak atlama
- **Zaman göstergesi** - MM:SS formatında

**Overlay Kontrolleri:**
- ✅ Oyuncu tracking noktaları
- 🔢 Oyuncu ID'leri  
- ⚽ Takım şekli
- 🛡️ Savunma hattı
- 📏 Blok mesafesi
- 🎾 Top yörüngesi
- 🔥 Heatmap
- ⚠️ Taktiksel uyarılar
- 🗺️ Saha bölgeleri

**Video Üstü Butonlar:**
- **🎛️ Overlay** - Görsel katman menüsü
- **✂️ Klip** - Klip oluşturma modalı
- **📝 Not** - Not ekleme modalı

### 📊 Üst Bilgi Çubuğu
- **Maç bilgisi:** U15 Kırmızı Takım vs Rakip
- **Tarih ve yaş kategorisi**
- **Video kaynağı bilgisi**
- **Analiz durumu:** Tamamlandı
- **Kalibrasyon kalitesi:** İyi (0.8m)
- **Tracking güven skoru:** %94

**Aksiyon Butonları:**
- **📄 Raporu Aç** - Maç raporu sayfası
- **📥 PDF Export** - Rapor indirme
- **📐 Kalibrasyon** - Kalibrasyon sayfası
- **🔄 Yeniden Analiz Et** - Analizi tekrar çalıştır

### 📈 Sağ Panel Tabları (1/4)

#### 1️⃣ **Metrikler Sekmesi**
- **Takım Boyu:** 47.2 m (trend göstergeli)
- **Takım Genişliği:** 42.8 m
- **Kompaktlık:** 18.4 m
- **Savunma-Orta Saha:** 21.4 m
- **Orta Saha-Forvet:** 16.8 m
- **Geçiş Hızı:** 4.6 m/s
- **Trend göstergeleri:** ↗️ ↘️ → 
- **Açıklama metinleri** her metrik için

#### 2️⃣ **Uyarılar Sekmesi**
**Alert Card Özellikleri:**
- **Severity renk kodlaması:** Critical (kırmızı), High (turuncu), Medium (mavi), Low (yeşil)
- **Zaman damgası:** MM:SS formatında
- **Güven skoru:** %82 gibi
- **Durum filtreleme:** Tümü, Açık, İnceleniyor, Çözüldü
- **Aksiyon butonları:**
  - 🎬 Videoda Göster
  - ✂️ Klip Oluştur  
  - 👁️ İncele
  - ✅ Onayla
  - ❌ Reddet

**Örnek Uyarılar:**
- Savunma hattı bozulması
- Bloklar arası kopukluk
- Geçiş savunması zayıf
- Derin koşu fırsatı
- Destek koşusu eksikliği

#### 3️⃣ **Klipler Sekmesi**
- **Thumbnail placeholder** - Video önizleme
- **Etiket sistemi:** Geçiş, Baskı, İkili Mücadele, Kanat Yüklenmesi
- **Süre bilgisi:** 12.5s gibi
- **Aksiyon butonları:**
  - ▶️ Oynat
  - 📥 İndir
  - 📤 Paylaş
  - 📄 Rapora Ekle

#### 4️⃣ **Oyuncular Sekmesi**
- **Sıralama:** Uyarı sayısı, Maks hız, Taktiksel skor, İsim
- **Pozisyon renk kodlaması:** Kaleci (turuncu), Defans (kırmızı), Orta saha (mavi), Forvet (yeşil)
- **Performans metrikleri:**
  - Ortalama pozisyon (x, y)
  - Maksimum hız (km/h)
  - Taktiksel uyarı sayısı
  - Taktiksel skor (/10)
- **📊 Pasaport** butonu - Oyuncu detay sayfası
- **Gelişim notları** - Antrenör yorumları

#### 5️⃣ **Notlar Sekmesi**
- **Zaman damgalı notlar** - Video anında ekleme
- **Etiket sistemi:** #taktik #teknik #pozisyon
- **Önerilen etiketler:** 12 adet hazır etiket
- **Yazar ve tarih bilgisi**
- **Sıralama:** En yeni önce
- **🗑️ Silme** özelliği

### ⏱️ Alt Timeline
**Görsel Özellikler:**
- **10 dakikalık zaman işaretleri**
- **Progress bar** - Mevcut zaman göstergesi
- **Event markerları:**
  - 🔴 Uyarılar (kırmızı)
  - 🔵 Klipler (mavi)  
  - 🟢 Goller (yeşil)
  - 🟡 Kartlar (sarı)
  - ⚪ Değişiklikler (beyaz)

**İnteraktif Özellikler:**
- **Tıklayarak atlama** - Herhangi bir zamana
- **Event hover** - Detay bilgi kartı
- **Event tıklama** - O ana gitme
- **5 dakikalık grid çizgileri**

### 🎭 Modal Pencereler

#### ✂️ **Klip Oluştur Modalı**
- **Başlık girişi** (zorunlu)
- **Açıklama alanı** (isteğe bağlı)
- **Başlangıç/Bitiş zamanı** - Saniye hassasiyeti
- **Etiket seçimi:** 8 farklı kategori
- **Zaman formatı:** MM:SS gösterimi
- **Form validasyonu** ve hata kontrolü

#### 📝 **Not Ekle Modalı**
- **Mevcut zaman göstergesi** - Otomatik doldurma
- **Çok satırlı metin alanı**
- **Etiket girişi** - Virgülle ayırma
- **12 önerilen etiket** - Tek tıkla ekleme
- **Otomatik yazar/tarih** ekleme

### 🎨 Görsel İyileştirmeler
- **Premium UI tutarlılığı** - PitchVision tema
- **Responsive tasarım** - Tüm ekran boyutları
- **Smooth animasyonlar** - Hover, focus, transition
- **Loading states** - Tüm async işlemler
- **Color coding** - Severity, pozisyon, durum bazlı
- **Typography hierarchy** - Okunabilirlik optimizasyonu

### ⚠️ **Önemli Uyarı Metni**
> "Bu uyarılar otomatik analiz adayıdır. Nihai değerlendirme antrenör gözlemiyle birlikte yapılmalıdır."

### 🔧 Teknik Özellikler
- **Type Safety:** Tam TypeScript desteği
- **State Management:** React hooks optimizasyonu
- **Performance:** Memoization ve lazy loading
- **Accessibility:** ARIA labels, keyboard navigation
- **Mock Data:** Gerçekçi demo veriler
- **Modular Architecture:** Yeniden kullanılabilir bileşenler

Bu ekran artık PitchVision Lite'ın kalbi olarak, antrenörlerin video analizini derinlemesine yapabilecekleri, uyarıları değerlendirebilecekleri, klipler oluşturabilecekleri ve detaylı notlar alabilecekleri tam fonksiyonel bir platform sunuyor!

---

**User:**

Backend için tactical analytics engine oluştur.
Dosya yapısı:
backend/app/analytics/
team_shape.py
defensive_line.py
transitions.py
runs.py
alerts.py
player_scores.py
drill_mapping.py
Input:
TrackPoint benzeri koordinat datası:
- player_id
- team_id
- role
- timestamp
- x
- y
- speed optional
- vx optional
- vy optional
Fonksiyonlar:
1. calculate_team_shape(points)
Output:
- team_length = max(x) - min(x)
- team_width = max(y) - min(y)
- centroid_x
- centroid_y
- compactness = mean(distance(player, centroid))
2. calculate_block_gaps(points)
Role grupları:
- defenders
- midfielders
- forwards
Output:
- defensive_midfield_gap
- midfield_forward_gap
3. calculate_defensive_line_errors(defenders)
Formula:
line_x = mean(defender.x)
line_error = abs(defender.x - line_x)
Output:
Her defender için line_error
4. detect_defensive_line_break(defenders, threshold_m=4.0)
Alert üret:
- alert_type = defensive_line_break
- confidence = min(1.0, line_error / 8.0)
- severity:
- <4 düşük
- 4-6 orta
- >6 yüksek
5. calculate_transition_speed(start_x, end_x, seconds=5)
transition_speed = (end_x - start_x) / seconds
6. detect_block_gap_alert(dm_gap, mf_gap)
Threshold configurable olsun.
7. detect_depth_run_candidate(player_track, defensive_line_x, ball_carrier_position)
Rules:
- velocity_x > threshold
- player starts before defensive line
- player moves toward or beyond line
- passing lane placeholder true
Output alert candidate
8. generate_tactical_alerts(match_tracking_data)
Tüm alertleri tek fonksiyonda üret.
Test:
- pytest unit testleri yaz.
- Mock tracking data oluştur.
- Her fonksiyon için expected output test et.

---

**Assistant:**

Backend için tactical analytics engine oluşturacağım. Önce mevcut backend yapısını kontrol edelim:

Şimdi tactical analytics engine için gerekli dosyaları oluşturacağım. Önce temel veri yapılarını tanımlayalım:

Şimdi takım şekli analizi modülünü oluşturalım:

Şimdi savunma hattı analizi modülünü oluşturalım:

Şimdi geçiş oyunu analizi modülünü oluşturalım:

Şimdi derin koşu analizi modülünü oluşturalım:

Şimdi ana uyarı sistemi modülünü oluşturalım:

Önce alerts.py dosyasını okuyalım:

Şimdi yeni alerts.py dosyasını oluşturalım:

Şimdi oyuncu skorları modülünü oluşturalım:

Şimdi drill mapping modülünü oluşturalım:

Şimdi test dosyalarını oluşturalım:

Son olarak ana __init__.py dosyasını güncelleyelim:

---
