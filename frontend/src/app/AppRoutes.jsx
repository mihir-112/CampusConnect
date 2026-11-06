// The route table. Each page belongs to the feature named in its folder. Owner: Moksh.
import { Route, Routes } from "react-router-dom";
import ProtectedRoute from "@features/aariz-publisher-auth/frontend/components/ProtectedRoute";
import LoginPage from "@features/aariz-publisher-auth/frontend/pages/LoginPage";
import AnnouncementFormPage from "@features/mihir-core-announcement-engine/frontend/pages/AnnouncementFormPage";
import PublisherDashboardPage from "@features/mihir-core-announcement-engine/frontend/pages/PublisherDashboardPage";
import Layout from "@features/moksh-student-dashboard/frontend/components/Layout";
import HomePage from "@features/moksh-student-dashboard/frontend/pages/HomePage";
import NotFoundPage from "@features/moksh-student-dashboard/frontend/pages/NotFoundPage";
import NotificationsPage from "@features/mridul-search-notifications/frontend/pages/NotificationsPage";
import AnnouncementDetailPage from "@features/nayeem-notice-details/frontend/pages/AnnouncementDetailPage";

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="announcements/:id" element={<AnnouncementDetailPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route path="publisher/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="publisher" element={<PublisherDashboardPage />} />
          <Route path="publisher/announcements/new" element={<AnnouncementFormPage />} />
          <Route path="publisher/announcements/:id/edit" element={<AnnouncementFormPage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
