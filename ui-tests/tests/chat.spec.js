// UI tests for the QodeBench chat page.
// Run (from the ui-tests folder):  npx playwright test
const { test, expect } = require("@playwright/test");

// Full address here, so the tests work even when run from the project root
const BASE_URL = process.env.BASE_URL || "http://localhost:8000";

test.beforeEach(async ({ page }) => {
  await page.goto(BASE_URL + "/");
});

test("chat page loads with input box and send button", async ({ page }) => {
  await expect(page).toHaveTitle(/QodeBench/);
  await expect(page.getByTestId("question")).toBeVisible();
  await expect(page.getByTestId("send")).toBeEnabled();
});

test("in-scope question gets an answer from the FAQ", async ({ page }) => {
  await page.getByTestId("question").fill("What are your support hours?");
  await page.getByTestId("send").click();
  await expect(page.getByTestId("answer")).toContainText(/monday/i);
  await expect(page.getByTestId("question")).toHaveValue("");   // input clears after sending
});

test("out-of-scope question gets a polite refusal", async ({ page }) => {
  await page.getByTestId("question").fill("What is the capital of France?");
  await page.getByTestId("question").press("Enter");             // Enter key also sends
  const answer = page.getByTestId("answer");
  await expect(answer).toContainText(/sorry|don.t have/i);
  await expect(answer).not.toContainText(/paris/i);
});

test("empty question is not sent", async ({ page }) => {
  await page.getByTestId("send").click();
  await expect(page.getByTestId("messages")).toBeEmpty();
});