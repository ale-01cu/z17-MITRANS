import { test, expect } from "@playwright/test";

test("signin-success", async ({ page }) => {
  await page.goto("http://localhost:5173/signin");

  await page.getByTestId("username").fill("alejandrofr");
  await page.getByTestId("pass").fill("01082968160Ale*");

  await page.getByTestId("signin-btn-submit").click();

  await expect(page).toHaveURL("http://localhost:5173/");
});