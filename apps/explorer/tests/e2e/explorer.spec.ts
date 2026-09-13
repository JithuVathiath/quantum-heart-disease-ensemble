import { expect, test } from "@playwright/test";

test("loads real benchmark evidence and opens the guide", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /One Published Result/ })).toBeVisible();
  await expect(page.getByText("No Quantum Advantage Under This Protocol")).toBeVisible();
  await expect(page.getByText("90.16%", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Open instructions" }).click();
  await expect(page.getByRole("heading", { name: "How to Read the Evidence" })).toBeVisible();
  await page.getByRole("button", { name: "Close instructions" }).click();
});

test("updates interactive calibration and transport views", async ({ page }) => {
  await page.goto("/#benchmark");
  await page.locator("#calibration-model").selectOption("bagged_quantum_kernel_svc");
  await expect(page.locator("#calibration-visual svg")).toHaveAttribute(
    "aria-label",
    /Bagged Quantum-Kernel SVC/,
  );
  await page.locator("#transport-model").selectOption("rbf_svc");
  await expect(page.locator("#transport-matrix")).toContainText("Long Beach VA");
});

test("remains usable on a mobile viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /One Published Result/ })).toBeVisible();
  await expect(page.getByRole("button", { name: "Open instructions" })).toBeVisible();
});
