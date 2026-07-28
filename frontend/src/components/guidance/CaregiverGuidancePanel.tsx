import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  Activity,
  CalendarCheck,
  Heart,
  HelpCircle,
  Pill,
  Siren,
  Soup,
  Sparkles,
  Sun,
  Users,
} from "lucide-react";

import { AlertBanner } from "@/components/common/AlertBanner";
import { EmptyState } from "@/components/common/EmptyState";
import { Spinner } from "@/components/common/Spinner";
import { Button } from "@/components/ui/Button";
import { GuidanceSectionCard } from "@/components/guidance/GuidanceSectionCard";
import { fetchCaregiverGuidance, generateCaregiverGuidance } from "@/services/guidanceService";
import { getApiErrorMessage } from "@/utils/apiError";

interface CaregiverGuidancePanelProps {
  reportId: string;
  canGenerate: boolean;
}

export function CaregiverGuidancePanel({ reportId, canGenerate }: CaregiverGuidancePanelProps) {
  const queryClient = useQueryClient();

  const { data: guidance, isLoading } = useQuery({
    queryKey: ["caregiver-guidance", reportId],
    queryFn: () => fetchCaregiverGuidance(reportId),
  });

  const generateMutation = useMutation({
    mutationFn: () => generateCaregiverGuidance(reportId),
    onSuccess: (result) => {
      queryClient.setQueryData(["caregiver-guidance", reportId], result);
      toast.success("Caregiver guidance generated successfully.");
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error, "Could not generate caregiver guidance."));
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-10">
        <Spinner />
      </div>
    );
  }

  const content = guidance?.status === "completed" ? guidance.content : null;
  const hasFailed = guidance?.status === "failed";

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Users className="h-5 w-5 text-primary" aria-hidden="true" />
          <h2 className="text-base font-semibold">Caregiver support</h2>
        </div>
        <Button
          className="h-9 w-auto px-4"
          isLoading={generateMutation.isPending}
          disabled={!canGenerate}
          onClick={() => generateMutation.mutate()}
        >
          {content ? "Regenerate" : "Generate guidance"}
        </Button>
      </div>

      {!canGenerate && (
        <AlertBanner
          variant="info"
          message="Generate the AI report summary first — caregiver guidance builds on it."
        />
      )}

      {hasFailed && (
        <AlertBanner
          variant="error"
          message={guidance?.error_message ?? "Guidance generation failed. Please try again."}
        />
      )}

      {!content && !hasFailed && canGenerate && (
        <EmptyState
          icon={Users}
          title="No caregiver guidance yet"
          description="Click 'Generate guidance' to create supportive guidance a caregiver can use, based on this report's AI summary."
        />
      )}

      {content && (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            <GuidanceSectionCard icon={Sun} title="Daily support" items={content.daily_support} />
            <GuidanceSectionCard
              icon={Heart}
              title="Emotional support"
              items={content.emotional_support}
            />
            <GuidanceSectionCard
              icon={CalendarCheck}
              title="Appointment support"
              items={content.appointment_support}
            />
            <GuidanceSectionCard
              icon={Pill}
              title="Medication support"
              items={content.medication_support}
            />
            <GuidanceSectionCard
              icon={Soup}
              title="Nutrition and hydration"
              items={content.nutrition_and_hydration}
            />
            <GuidanceSectionCard
              icon={Activity}
              title="Fatigue and comfort support"
              items={content.fatigue_and_comfort_support}
            />
            <GuidanceSectionCard
              icon={Activity}
              title="Symptoms to observe"
              items={content.symptoms_to_observe}
            />
            <GuidanceSectionCard
              icon={Siren}
              title="Emergency warning signs"
              items={content.emergency_warning_signs}
            />
            <GuidanceSectionCard
              icon={Sparkles}
              title="Caregiver self-care"
              items={content.caregiver_self_care}
            />
            <GuidanceSectionCard
              icon={HelpCircle}
              title="Questions for the medical team"
              items={content.questions_for_medical_team}
            />
            <GuidanceSectionCard icon={HelpCircle} title="Limitations" items={content.limitations} />
          </div>

          <AlertBanner variant="info" message={content.disclaimer} />
        </>
      )}
    </div>
  );
}
