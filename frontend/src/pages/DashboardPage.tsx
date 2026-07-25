import { Activity, FileText, HeartPulse, ShieldCheck } from "lucide-react";

import { Card } from "@/components/ui/Card";
import { useAuth } from "@/contexts/AuthContext";

const ROLE_LABELS: Record<string, string> = {
  patient: "Patient",
  doctor: "Doctor",
  caregiver: "Caregiver",
  admin: "Admin",
};

const PLACEHOLDER_MODULES = [
  {
    icon: Activity,
    title: "Risk Assessment",
    description: "ML-driven risk scoring will appear here once the module is implemented.",
  },
  {
    icon: FileText,
    title: "Medical Reports",
    description: "Uploaded reports and OCR/LLM summaries will be listed here.",
  },
  {
    icon: HeartPulse,
    title: "Rehabilitation Plan",
    description: "Your personalized rehabilitation plan will be tracked here.",
  },
  {
    icon: ShieldCheck,
    title: "Care Team",
    description: "Connected doctors and caregivers will be managed here.",
  },
];

/** Placeholder dashboard — confirms authenticated access; real widgets land in later milestones. */
export function DashboardPage() {
  const { user } = useAuth();
  const roleLabels = user?.roles.map((role) => ROLE_LABELS[role] ?? role).join(", ");

  return (
    <div className="container flex flex-col gap-8 py-10">
      <div>
        <h1 className="text-2xl font-bold">Welcome back{user ? `, ${user.full_name}` : ""}</h1>
        <p className="text-sm text-muted-foreground">
          {roleLabels ? `Signed in as ${roleLabels}` : "Signed in"} · {user?.email}
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {PLACEHOLDER_MODULES.map(({ icon: Icon, title, description }) => (
          <Card key={title} className="flex flex-col gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Icon className="h-6 w-6" aria-hidden="true" />
            </div>
            <h3 className="text-base font-semibold">{title}</h3>
            <p className="text-sm text-muted-foreground">{description}</p>
          </Card>
        ))}
      </div>

      <Card>
        <h2 className="mb-2 text-lg font-semibold">Account details</h2>
        <dl className="grid grid-cols-1 gap-2 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-muted-foreground">Email</dt>
            <dd>{user?.email}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Role(s)</dt>
            <dd>{roleLabels}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Account status</dt>
            <dd>{user?.is_active ? "Active" : "Inactive"}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Verified</dt>
            <dd>{user?.is_verified ? "Yes" : "No"}</dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
