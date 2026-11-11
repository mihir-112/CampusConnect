// The route table. Each page belongs to the feature named in its folder. Owner: student-dashboard.
import { Route, Routes } from "react-router-dom";
import ProtectedRoute from "@features/publisher-auth/frontend/components/ProtectedRoute";
import LoginPage from "@features/publisher-auth/frontend/pages/LoginPage";
import AnnouncementFormPage from "@features/core-announcement-engine/frontend/pages/AnnouncementFormPage";
import PublisherDashboardPage from "@features/core-announcement-engine/frontend/pages/PublisherDashboardPage";
import Layout from "@features/student-dashboard/frontend/components/Layout";
import HomePage from "@features/student-dashboard/frontend/pages/HomePage";
import NotFoundPage from "@features/student-dashboard/frontend/pages/NotFoundPage";
import NotificationsPage from "@features/search-notifications/frontend/pages/NotificationsPage";
import AnnouncementDetailPage from "@features/notice-details/frontend/pages/AnnouncementDetailPage";

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
