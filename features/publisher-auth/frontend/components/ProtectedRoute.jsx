// Sends visitors who are not logged in to the login page. Owner: publisher-auth.
// The real protection is on the server; this only avoids showing pages that would fail anyway.
import { Navigate, Outlet, useLocation } from "react-router-dom";
import StateMessage from "@features/student-dashboard/frontend/components/StateMessage";
import { useAuth } from "../auth/AuthContext";

export default function ProtectedRoute() {
  const { status } = useAuth();
  const location = useLocation();

  if (status === "loading") return <StateMessage kind="loading" title="Checking your session" />;
  if (status !== "authenticated") {
    return <Navigate to="/publisher/login" replace state={{ from: location.pathname + location.search }} />;
  }
  return <Outlet />;
}
