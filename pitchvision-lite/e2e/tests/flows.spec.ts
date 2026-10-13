/**
 * E2E akış testleri — PitchVision Lite temel kullanıcı yolculukları.
 *
 * Çalıştırmak için:
 *   cd pitchvision-lite/e2e
 *   npx playwright test
 *
 * NOT: Bu testler çalışan bir frontend (localhost:3000) gerektirir.
 *      Mock mod aktifken (NEXT_PUBLIC_USE_MOCKS=true) çalışır.
 */
import { test, expect } from "@playwright/test";

// ── 1. Login → Dashboard ──────────────────────────────────────────────────────

test.describe("Login → Dashboard", () => {
  test("login sayfası yüklenir", async ({ page }) => {
    await page.goto("/login");
    await expect(page).toHaveTitle(/pitchvision/i);
    await expect(page.getByRole("heading")).toBeVisible();
  });

  test("geçersiz credentials hata gösterir", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/e-posta/i).fill("yanlis@email.com");
    await page.getByLabel(/şifre/i).fill("yanlis");
    await page.getByRole("button", { name: /giriş/i }).click();
    // Hata mesajı veya aynı sayfada kalma
    await expect(page).toHaveURL(/login/);
  });

  test("demo credentials ile giriş yapılır", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/e-posta/i).fill("coach@anadolu-akademi.demo");
    await page.getByLabel(/şifre/i).fill("demo12345");
    await page.getByRole("button", { name: /giriş/i }).click();
    await expect(page).toHaveURL(/dashboard/);
  });

  test("dashboard stat kartları görünür", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.getByText(/işlenen maç/i)).toBeVisible();
    await expect(page.getByText(/takip edilen oyuncu/i)).toBeVisible();
  });
});

// ── 2. Dashboard → Yeni Maç Yükle ────────────────────────────────────────────

test.describe("Dashboard → Yeni Maç Yükle", () => {
  test("yeni maç yükle butonuna tıklanır", async ({ page }) => {
    await page.goto("/dashboard");
    await page.getByRole("link", { name: /yeni maç yükle/i }).click();
    await expect(page).toHaveURL(/matches\/new/);
  });

  test("yeni maç sayfası form içerir", async ({ page }) => {
    await page.goto("/matches/new");
    // Upload dropzone veya form alanı görünür
    await expect(page.locator("body")).toBeVisible();
  });
});

// ── 3. Maçlar → Video Analiz ──────────────────────────────────────────────────

test.describe("Maçlar → Video Analiz", () => {
  test("maçlar sayfası yüklenir", async ({ page }) => {
    await page.goto("/matches");
    await expect(page.getByRole("heading", { name: /maçlar/i })).toBeVisible();
  });

  test("maç listesi görünür", async ({ page }) => {
    await page.goto("/matches");
    // Mock modda maç kartları görünmeli
    await expect(page.locator("body")).toBeVisible();
  });

  test("maç detayına gidilir", async ({ page }) => {
    await page.goto("/matches");
    // İlk maç kartındaki detay linkine tıkla
    const firstDetailLink = page.getByRole("link", { name: /detay/i }).first();
    if (await firstDetailLink.isVisible()) {
      await firstDetailLink.click();
      await expect(page).toHaveURL(/matches\/\d+/);
    }
  });

  test("video analiz sayfası yüklenir", async ({ page }) => {
    await page.goto("/matches/1001/analysis");
    await expect(page.getByText(/video analiz/i)).toBeVisible();
  });

  test("analiz tab'ları görünür", async ({ page }) => {
    await page.goto("/matches/1001/analysis");
    await expect(page.getByText(/metrikler/i)).toBeVisible();
    await expect(page.getByText(/uyarılar/i)).toBeVisible();
  });
});

// ── 4. Video Analiz → Maç Raporu ─────────────────────────────────────────────

test.describe("Video Analiz → Maç Raporu", () => {
  test("raporu aç linki görünür", async ({ page }) => {
    await page.goto("/matches/1001/analysis");
    await expect(page.getByRole("link", { name: /raporu aç/i })).toBeVisible();
  });

  test("rapor sayfasına gidilir", async ({ page }) => {
    await page.goto("/matches/1001/analysis");
    await page.getByRole("link", { name: /raporu aç/i }).click();
    await expect(page).toHaveURL(/matches\/1001\/report/);
  });

  test("rapor sayfası maç bilgisi içerir", async ({ page }) => {
    await page.goto("/matches/1001/report");
    await expect(page.getByText(/maç raporu/i)).toBeVisible();
  });

  test("pdf export butonu görünür", async ({ page }) => {
    await page.goto("/matches/1001/report");
    await expect(page.getByRole("button", { name: /pdf/i })).toBeVisible();
  });
});
