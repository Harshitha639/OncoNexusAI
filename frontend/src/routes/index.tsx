import { Route, Routes } from "react-router-dom";

import { AuthLayout } from "@/layouts/AuthLayout";
import { RootLayout } from "@/layouts/RootLayout";
import { AppointmentsPage } from "@/pages/AppointmentsPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { ForgotPasswordPage } from "@/pages/ForgotPasswordPage";
import { LandingPage } from "@/pages/LandingPage";
import { LoginPage } from "@/pages/LoginPage";
import { MedicalProfilePage } from "@/pages/MedicalProfilePage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { PatientProfilePage } from "@/pages/PatientProfilePage";
import { RegisterPage } from "@/pages/RegisterPage";
import { ReportDetailsPage } from "@/pages/ReportDetailsPage";
import { ReportHistoryPage } from "@/pages/ReportHistoryPage";
import { UploadReportPage } from "@/pages/UploadReportPage";
import { GuestRoute } from "@/routes/GuestRoute";
import { ProtectedRoute } from "@/routes/ProtectedRoute";

/**
 * Central route table for the application.
 *
 * New feature pages should be added here, nested under the appropriate
 * layout/guard, once their corresponding backend endpoints exist.
 */
export function AppRoutes() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        <Route index element={<LandingPage />} />

        <Route element={<AuthLayout />}>
          <Route element={<GuestRoute />}>
            <Route path="login" element={<LoginPage />} />
            <Route path="register" element={<RegisterPage />} />
            <Route path="forgot-password" element={<ForgotPasswordPage />} />
          </Route>
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route path="dashboard" element={<DashboardPage />} />

          <Route path="profile/patient" element={<PatientProfilePage />} />
          <Route path="profile/medical" element={<MedicalProfilePage />} />

          <Route path="reports" element={<ReportHistoryPage />} />
          <Route path="reports/upload" element={<UploadReportPage />} />
          <Route path="reports/:reportId" element={<ReportDetailsPage />} />

          <Route path="appointments" element={<AppointmentsPage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
