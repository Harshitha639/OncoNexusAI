import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  AlertTriangle,
  CalendarCheck,
  ClipboardList,
  HelpCircle,
  Salad,
  ShieldAlert,
  Sparkles,
  Utensils,
} from "lucide-react";

import { AlertBanner } from "@/components/common/AlertBanner";
import { EmptyState } from "@/components/common/EmptyState";
import { Spinner } from "@/components/common/Spinner";
import { Button } from "@/components/ui/Button";
import { GuidanceSectionCard } from "@/components/guidance/GuidanceSectionCard";
import { fetchPatientGuidance, generatePatientGuidance } from "@/services/guidanceService";
import { getApiErrorMessage } from "@/utils/apiError";

interface PersonalizedGuidancePanelProps {
  reportId: string;
  canGenerate: boolean;
}

export function PersonalizedGuidancePanel({ reportId, canGenerate }: PersonalizedGuidancePanelProps) {
  const queryClient = useQueryClient();

  const { data: guidance, isLoading } = useQuery({
    queryKey: ["patient-guidance", reportId],
    queryFn: () => fetchPatientGuidance(reportId),
  });

  const generateMutation = useMutation({
    mutationFn: () => generatePatientGuidance(reportId),
    onSuccess: (result) => {
      queryClient.setQueryData(["patient-guidance", reportId], result);
      toast.success("Personalized guidance generated successfully.");
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error, "Could not generate personalized guidance."));
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
          <Sparkles className="h-5 w-5 text-primary" aria-hidden="true" />
          <h2 className="text-base font-semibold">Personalized guidance</h2>
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
          message="Generate the AI report summary first — personalized guidance builds on it."
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
          icon={Sparkles}
          title="No personalized guidance yet"
          description="Click 'Generate guidance' to create supportive, patient-friendly guidance based on this report's AI summary."
        />
      )}

      {content && (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            <GuidanceSectionCard icon={ShieldAlert} title="Precautions" items={content.precautions} />
            <GuidanceSectionCard icon={Salad} title="Nutrition guidance" items={content.nutrition_guidance} />
            <GuidanceSectionCard
              icon={Utensils}
              title="Lifestyle guidance"
              items={content.lifestyle_guidance}
            />
            <GuidanceSectionCard
              icon={HelpCircle}
              title="Questions for your doctor"
              items={content.questions_for_doctor}
            />
            <GuidanceSectionCard
              icon={ClipboardList}
              title="Follow-up checklist"
              items={content.follow_up_checklist}
            />
            <GuidanceSectionCard
              icon={CalendarCheck}
              title="Appointment preparation"
              items={content.appointment_preparation}
            />
            <GuidanceSectionCard
              icon={AlertTriangle}
              title="Warning signs — contact your care team"
              items={content.warning_signs}
            />
            <GuidanceSectionCard icon={HelpCircle} title="Limitations" items={content.limitations} />
          </div>

          <AlertBanner variant="info" message={content.disclaimer} />
        </>
      )}
    </div>
  );
}
