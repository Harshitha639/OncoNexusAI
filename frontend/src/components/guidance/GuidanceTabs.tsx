import { useState } from "react";
import { HeartHandshake, Sparkles } from "lucide-react";

import { Card } from "@/components/ui/Card";
import { CaregiverGuidancePanel } from "@/components/guidance/CaregiverGuidancePanel";
import { PersonalizedGuidancePanel } from "@/components/guidance/PersonalizedGuidancePanel";
import { cn } from "@/utils/cn";

type GuidanceTab = "patient" | "caregiver";

interface GuidanceTabsProps {
  reportId: string;
  /** Whether the report's AI summary is completed — guidance generation
   * builds on it, so both agents stay disabled until it's ready. */
  canGenerate: boolean;
}

const TABS: Array<{ id: GuidanceTab; label: string; icon: typeof Sparkles }> = [
  { id: "patient", label: "Personalized Guidance", icon: Sparkles },
  { id: "caregiver", label: "Caregiver Support", icon: HeartHandshake },
];

/** Two clearly-separated sections (Personalized Guidance / Caregiver Support),
 * switched via a lightweight local-state tab control — no new dependency. */
export function GuidanceTabs({ reportId, canGenerate }: GuidanceTabsProps) {
  const [activeTab, setActiveTab] = useState<GuidanceTab>("patient");

  return (
    <Card variant="glass" className="flex flex-col gap-5">
      <div className="flex gap-2 border-b border-border pb-3">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => setActiveTab(id)}
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              activeTab === id
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            <Icon className="h-4 w-4" aria-hidden="true" />
            {label}
          </button>
        ))}
      </div>

      {activeTab === "patient" ? (
        <PersonalizedGuidancePanel reportId={reportId} canGenerate={canGenerate} />
      ) : (
        <CaregiverGuidancePanel reportId={reportId} canGenerate={canGenerate} />
      )}
    </Card>
  );
}
