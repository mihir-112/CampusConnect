// Loads search results and reports loading / error / success. Owner: search-notifications.
import { useCallback, useEffect, useState } from "react";
import { isAbort } from "@/api/client";
import { searchAnnouncements } from "../searchApi";

export function useAnnouncementSearch({ q, category, page }) {
  const [state, setState] = useState({ status: "loading", data: null, error: null });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setState((previous) => ({ ...previous, status: "loading", error: null }));
    searchAnnouncements({ q, category, page, signal: controller.signal })
      .then((data) => setState({ status: "success", data, error: null }))
      .catch((error) => {
        if (!isAbort(error)) setState({ status: "error", data: null, error });
      });
    return () => controller.abort(); // a newer search replaces this one
  }, [q, category, page, attempt]);

  const retry = useCallback(() => setAttempt((n) => n + 1), []);
  return { ...state, retry };
}
