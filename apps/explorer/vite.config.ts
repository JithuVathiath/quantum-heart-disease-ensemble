import { defineConfig } from "vitest/config";

export default defineConfig({
  base: process.env.GITHUB_ACTIONS ? "/quantum-heart-disease-ensemble/" : "/",
  build: {
    sourcemap: true,
  },
  test: {
    exclude: ["tests/e2e/**", "node_modules/**"],
  },
});
