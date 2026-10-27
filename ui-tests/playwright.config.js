// Playwright config for the chat UI served by app.py at http://localhost:8000/
// Start the server first:  uvicorn app:app --port 8000
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  timeout: 60_000,                       // the bot calls an LLM, so answers take a few seconds
  expect: { timeout: 30_000 },
  reporter: [["list"], ["html", { open: "never", outputFolder: "../reports/playwright" }]],
  use: {
    baseURL: process.env.BASE_URL || "http://localhost:8000",
    screenshot: "only-on-failure",
  },
});
