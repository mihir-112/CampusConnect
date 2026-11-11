// Vite configuration. Owner: student-dashboard (shared frontend infrastructure).
//
// Features keep React code in features/<member-feature-name>/frontend/.
// The app imports it using the "@features" shortcut.

import path from "node:path";
import { fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "..");

// Resolve packages from frontend/ for files inside features/.
function resolvePackagesFromFrontend() {
  const anchor = path.join(here, "index.html");

  return {
    name: "resolve-packages-from-frontend",
    enforce: "pre",

    async resolveId(source, importer, options) {
      if (!importer || importer.startsWith(here) || importer.includes("\0")) {
        return null;
      }

      if (
        source.startsWith(".") ||
        source.startsWith("/") ||
        source.startsWith("@features/") ||
        source.startsWith("@members/") ||
        source.startsWith("@shared/") ||
        source.startsWith("@app/") ||
        source.startsWith("@/")
      ) {
        return null;
      }

      if (
        path.isAbsolute(source) ||
        source.startsWith("\0") ||
        source.startsWith("node:")
      ) {
        return null;
      }

      return this.resolve(source, anchor, {
        ...options,
        skipSelf: true,
      });
    },
  };
}

export default defineConfig({
  plugins: [resolvePackagesFromFrontend(), react()],

  resolve: {
    alias: [
      // Direct member-prefixed feature folders
      { find: "@features/core-announcement-engine", replacement: path.join(repoRoot, "features/core-announcement-engine") },
      { find: "@features/publisher-auth", replacement: path.join(repoRoot, "features/publisher-auth") },
      { find: "@features/notice-details", replacement: path.join(repoRoot, "features/notice-details") },
      { find: "@features/student-dashboard", replacement: path.join(repoRoot, "features/student-dashboard") },
      { find: "@features/search-notifications", replacement: path.join(repoRoot, "features/search-notifications") },

      // Legacy feature names (backward compatibility)
      { find: "@features/core-announcement-engine", replacement: path.join(repoRoot, "features/core-announcement-engine") },
      { find: "@features/publisher-auth", replacement: path.join(repoRoot, "features/publisher-auth") },
      { find: "@features/notice-details", replacement: path.join(repoRoot, "features/notice-details") },
      { find: "@features/student-dashboard", replacement: path.join(repoRoot, "features/student-dashboard") },
      { find: "@features/search-notifications", replacement: path.join(repoRoot, "features/search-notifications") },

      { find: "@features", replacement: path.join(repoRoot, "features") },
      { find: "@members", replacement: path.join(repoRoot, "features") },

      // App and shared aliases
      { find: "@app", replacement: path.join(here, "src/app") },
      { find: "@shared", replacement: path.join(here, "src/shared") },

      // Shared subfolder mappings for clean imports
      { find: "@/api", replacement: path.join(here, "src/shared/api") },
      { find: "@/utils", replacement: path.join(here, "src/shared/utils") },
      { find: "@/components", replacement: path.join(here, "src/shared/components") },
      { find: "@/styles", replacement: path.join(here, "src/shared/styles") },
      { find: "@/test", replacement: path.join(here, "src/shared/test") },
      { find: "@", replacement: path.join(here, "src") },
    ],
  },

  server: {
    port: 5173,
    fs: {
      allow: [repoRoot],
    },
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },

  preview: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },

  test: {
    environment: "jsdom",

    environmentOptions: {
      jsdom: {
        url: "http://localhost:5173/",
      },
    },

    globals: true,

    setupFiles: ["./src/shared/test/setup.js"],

    include: [
      "src/**/*.test.{js,jsx}",
      "../features/*/tests/**/*.test.{js,jsx}",
    ],

    css: false,
  },
});
