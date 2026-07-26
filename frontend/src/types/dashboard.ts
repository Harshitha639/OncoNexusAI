/** Mirrors the backend's `app.schemas.dashboard` contracts. */

import type { Appointment } from "@/types/appointment";
import type { MedicalReport, ReportAnalysis } from "@/types/report";

export interface DashboardWelcome {
  full_name: string;
  email: string;
  roles: string[];
}

export interface DashboardSummary {
  welcome: DashboardWelcome;
  profile_completion_percentage: number;
  has_profile: boolean;
  recent_reports: MedicalReport[];
  latest_ai_summary: ReportAnalysis | null;
  latest_risk_score: number | null;
  upcoming_appointments: Appointment[];
  unread_notification_count: number;
  total_reports: number;
}
