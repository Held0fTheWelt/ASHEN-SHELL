import { test, expect } from "@playwright/test";

test("login page responds", async ({ page }) => {
  const res = await page.goto("/login", { waitUntil: "domcontentloaded" });
  expect(res?.ok()).toBeTruthy();
  await expect(page.locator("body")).toBeVisible();
});
