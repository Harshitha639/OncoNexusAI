import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  Activity,
  CalendarClock,
  FileText,
  Plus,
  Sparkles,
  Upload,
  UserRound,
} from "lucide-react";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/common/EmptyState";
import { FullPageSpinner } from "@/components/common/Spinner";
import { useAuth } from "@/contexts/AuthContext";
import { fetchDashboardSummary } from "@/services/dashboardService";

const ROLE_LABELS: Record<string, string> = {
  patient: "Patient",
  doctor: "Doctor",
  caregiver: "Caregiver",
  admin: "Admin",
};

const OCR_STATUS_VARIANT: Record<string, "default" | "success" | "warning" | "destructive"> = {
  pending: "default",
  processing: "warning",
  completed: "success",
  failed: "destructive",
};

function riskLabel(score: number | null): { label: string; variant: "success" | "warning" | "destructive" } {
  if (score === null) return { label: "Not available", variant: "success" };
  if (score < 34) return { label: `Low (${Math.round(score)})`, variant: "success" };
  if (score < 67) return { label: `Moderate (${Math.round(score)})`, variant: "warning" };
  return { label: `High (${Math.round(score)})`, variant: "destructive" };
}

const QUICK_ACTIONS = [
  { to: "/reports/upload", label: "Upload Report", icon: Upload },
  { to: "/appointments", label: "Book Appointment", icon: Plus },
  { to: "/profile/patient", label: "Update Profile", icon: UserRound },
  { to: "/reports", label: "View Reports", icon: FileText },
];

export function DashboardPage() {
  const { user } = useAuth();
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: fetchDashboardSummary,
  });

  if (isLoading || !data) {
    return <FullPageSpinner label="Loading your dashboard..." />;
  }

  const roleLabels = user?.roles.map((role) => ROLE_LABELS[role] ?? role).join(", ");
  const risk = riskLabel(data.latest_risk_score);

  return (
    <div className="container flex flex-col gap-8 py-10">
      {/* Welcome card */}
      <Card variant="glass" className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold">
          Welcome back{data.welcome.full_name ? `, ${data.welcome.full_name.split(" ")[0]}` : ""} 👋
        </h1>
        <p className="text-sm text-muted-foreground">
          {roleLabels ? `Signed in as ${roleLabels}` : "Signed in"} · {data.welcome.email}
        </p>
      </Card>

      {/* Quick actions */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {QUICK_ACTIONS.map(({ to, label, icon: Icon }) => (
          <Link key={to} to={to}>
            <Card
              variant="glass"
              className="flex flex-col items-center gap-2 py-6 text-center transition-transform hover:-translate-y-0.5"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Icon className="h-5 w-5" aria-hidden="true" />
              </div>
              <span className="text-sm font-medium">{label}</span>
            </Card>
          </Link>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Profile completion */}
        <Card variant="glass" className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold">Profile completion</h2>
            <UserRound className="h-5 w-5 text-primary" aria-hidden="true" />
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${data.profile_completion_percentage}%` }}
            />
          </div>
          <p className="text-sm text-muted-foreground">
            {data.profile_completion_percentage}% complete
          </p>
          <Link
            to={data.has_profile ? "/profile/patient" : "/profile/patient"}
            className="text-sm font-medium text-primary hover:underline"
          >
            {data.has_profile ? "Update profile" : "Complete your profile"} →
          </Link>
        </Card>

        {/* Latest risk score */}
        <Card variant="glass" className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold">Latest risk indicator</h2>
            <Activity className="h-5 w-5 text-primary" aria-hidden="true" />
          </div>
          <Badge variant={risk.variant} className="w-fit text-sm">
            {risk.label}
          </Badge>
          <p className="text-sm text-muted-foreground">
            {data.latest_ai_summary
              ? "Based on your most recent AI report summary."
              : "Generate an AI summary on a report to see a risk indicator here."}
          </p>
        </Card>

        {/* Upcoming appointments */}
        <Card variant="glass" className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold">Upcoming appointments</h2>
            <CalendarClock className="h-5 w-5 text-primary" aria-hidden="true" />
          </div>
          {data.upcoming_appointments.length === 0 ? (
            <p className="text-sm text-muted-foreground">No upcoming appointments.</p>
          ) : (
            <ul className="flex flex-col gap-2">
              {data.upcoming_appointments.slice(0, 3).map((appointment) => (
                <li key={appointment.id} className="text-sm">
                  <span className="font-medium">{appointment.doctor_name}</span>
                  <span className="text-muted-foreground">
                    {" "}
                    · {new Date(appointment.scheduled_at).toLocaleString(undefined, {
                      dateStyle: "medium",
                      timeStyle: "short",
                    })}
                  </span>
                </li>
              ))}
            </ul>
          )}
          <Link to="/appointments" className="text-sm font-medium text-primary hover:underline">
            View all appointments →
          </Link>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent reports */}
        <Card variant="glass" className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold">Recent reports</h2>
            <Link to="/reports" className="text-sm font-medium text-primary hover:underline">
              View all
            </Link>
          </div>
          {data.recent_reports.length === 0 ? (
            <EmptyState
              icon={FileText}
              title="No reports yet"
              description="Upload your first medical report to get started."
              action={
                <Link to="/reports/upload" className="text-sm font-medium text-primary hover:underline">
                  Upload a report →
                </Link>
              }
            />
          ) : (
            <ul className="flex flex-col divide-y divide-border">
              {data.recent_reports.map((report) => (
                <li key={report.id} className="flex items-center justify-between py-3">
                  <Link
                    to={`/reports/${report.id}`}
                    className="flex-1 text-sm font-medium hover:text-primary"
                  >
                    {report.title}
                  </Link>
                  <Badge variant={OCR_STATUS_VARIANT[report.ocr_status]}>{report.ocr_status}</Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* AI summary card */}
        <Card variant="glass" className="flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" aria-hidden="true" />
            <h2 className="text-base font-semibold">Latest AI summary</h2>
          </div>
          {data.latest_ai_summary ? (
            <>
              <p className="line-clamp-4 text-sm text-muted-foreground">
                {data.latest_ai_summary.patient_friendly_summary}
              </p>
              {data.latest_ai_summary.cancer_type && (
                <p className="text-sm">
                  <span className="font-medium">Type:</span> {data.latest_ai_summary.cancer_type}
                  {data.latest_ai_summary.cancer_stage
                    ? ` · Stage ${data.latest_ai_summary.cancer_stage}`
                    : ""}
                </p>
              )}
            </>
          ) : (
            <p className="text-sm text-muted-foreground">
              No AI summaries generated yet. Upload a report and generate one from the report
              details page.
            </p>
          )}
        </Card>
      </div>
    </div>
  );
}
