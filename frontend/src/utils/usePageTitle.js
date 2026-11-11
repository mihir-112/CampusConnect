import { useEffect } from "react";

/** Sets the browser tab title, e.g. "Announcements | CampusConnect". */
export function usePageTitle(title) {
  useEffect(() => {
    document.title = title ? `${title} | CampusConnect` : "CampusConnect";
  }, [title]);
}
