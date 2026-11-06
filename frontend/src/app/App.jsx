import { AuthProvider } from "@features/aariz-publisher-auth/frontend/auth/AuthContext";
import { NotificationsProvider } from "@features/mridul-search-notifications/frontend/hooks/NotificationsContext";
import ErrorBoundary from "@/shared/components/ErrorBoundary";
import AppRoutes from "./AppRoutes";

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <NotificationsProvider>
          <AppRoutes />
        </NotificationsProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
