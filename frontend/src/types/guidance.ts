/**
 * Mirrors the backend's `app.schemas.guidance` contracts (Phase 4 —
 * Personalized Guidance and Caregiver Support agents).
 */

import type { AiSummaryStatus } from "@/types/report";

export type GuidanceType = "patient_guidance" | "caregiver_guidance";

export interface PersonalizedGuidanceContent {
  precautions: string[];
  nutrition_guidance: string[];
  lifestyle_guidance: string[];
  questions_for_doctor: string[];
  follow_up_checklist: string[];
  appointment_preparation: string[];
  warning_signs: string[];
  limitations: string[];
  disclaimer: string;
}

export interface CaregiverGuidanceContent {
  daily_support: string[];
  emotional_support: string[];
  appointment_support: string[];
  medication_support: string[];
  nutrition_and_hydration: string[];
  fatigue_and_comfort_support: string[];
  symptoms_to_observe: string[];
  emergency_warning_signs: string[];
  caregiver_self_care: string[];
  questions_for_medical_team: string[];
  limitations: string[];
  disclaimer: string;
}

interface GuidanceBase {
  id: string;
  report_id: string;
  patient_id: string;
  analysis_id: string;
  guidance_type: GuidanceType;
  status: AiSummaryStatus;
  error_message: string | null;
  model_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface PersonalizedGuidance extends GuidanceBase {
  content: PersonalizedGuidanceContent | null;
}

export interface CaregiverGuidance extends GuidanceBase {
  content: CaregiverGuidanceContent | null;
}
