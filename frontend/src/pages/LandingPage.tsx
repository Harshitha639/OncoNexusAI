import { Link } from "react-router-dom";
import { Activity, FileText, HeartPulse, ShieldCheck, Sparkles, Users } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

const FEATURES = [
  {
    icon: Activity,
    title: "Risk Assessment",
    description:
      "ML-driven risk scoring with explainable predictions to support earlier, informed decisions.",
  },
  {
    icon: FileText,
    title: "Medical Report Understanding",
    description:
      "OCR and LLM-powered digitization turns uploaded reports into structured, searchable insight.",
  },
  {
    icon: Sparkles,
    title: "Personalized Guidance",
    description:
      "Multi-agent AI orchestration delivers guidance tailored to each patient's care journey.",
  },
  {
    icon: HeartPulse,
    title: "Rehabilitation Support",
    description: "Recovery and rehabilitation planning designed around individual progress.",
  },
  {
    icon: Users,
    title: "Care Team Collaboration",
    description: "Role-based access for patients, doctors, and caregivers to stay aligned.",
  },
  {
    icon: ShieldCheck,
    title: "Secure by Design",
    description: "JWT-based authentication and role-based access control protect every account.",
  },
];

export function LandingPage() {
  return (
    <div className="flex flex-col">
      <section className="bg-gradient-to-b from-primary/5 to-background">
        <div className="container flex flex-col items-center gap-6 py-24 text-center">
          <span className="rounded-full bg-primary/10 px-4 py-1 text-sm font-medium text-primary">
            Multi-Agent Intelligent Cancer Care
          </span>
          <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            AI-powered support for every step of the cancer care journey
          </h1>
          <p className="max-w-2xl text-lg text-muted-foreground">
            OncoNexus AI combines risk assessment, medical report understanding, personalized
            guidance, and rehabilitation support in one secure platform — for patients, doctors,
            and caregivers.
          </p>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Link to="/register">
              <Button className="h-12 w-auto px-8 text-base">Create your account</Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" className="h-12 w-auto px-8 text-base">
                Log in
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <section className="container py-20">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <Card key={title} className="flex flex-col gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Icon className="h-6 w-6" aria-hidden="true" />
              </div>
              <h3 className="text-lg font-semibold">{title}</h3>
              <p className="text-sm text-muted-foreground">{description}</p>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
