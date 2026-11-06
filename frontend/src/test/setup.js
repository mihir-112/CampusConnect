import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

function createStorage() {
  let store = {};
  return {
    getItem: (key) => store[key] ?? null,
    setItem: (key, value) => {
      store[key] = String(value);
    },
    removeItem: (key) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
    get length() {
      return Object.keys(store).length;
    },
    key: (i) => Object.keys(store)[i] ?? null,
  };
}

if (!window.localStorage || typeof window.localStorage.clear !== "function") {
  Object.defineProperty(window, "localStorage", {
    value: createStorage(),
    configurable: true,
    writable: true,
  });
}

if (!window.sessionStorage || typeof window.sessionStorage.clear !== "function") {
  Object.defineProperty(window, "sessionStorage", {
    value: createStorage(),
    configurable: true,
    writable: true,
  });
}

afterEach(() => {
  cleanup();
  window.localStorage?.clear?.();
  window.sessionStorage?.clear?.();
});
