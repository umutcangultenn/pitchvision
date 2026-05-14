/**
 * Auth setup — login state'ini storage'a kaydeder,
 * diğer testler bu state'i yeniden kullanır.
 */
import { test as setup, expect } from "@playwright/test";
import path from "path";

export const authFile = path.join(__dirname, "../.auth/user.json");

setup("authenticate", async ({ page }) => {
  await page.goto("/login");

  await page.getByLabel(/e-posta/i).fill("coach@anadolu-akademi.demo");
  await page.getByLabel(/şifre/i).fill("demo12345");
  await page.getByRole("button", { name: /giriş/i }).click();

  // Dashboard'a yönlendirilmeli
  await expect(page).toHaveURL(/dashboard/);

  // Auth state'i kaydet
  await page.context().storageState({ path: authFile });
});
