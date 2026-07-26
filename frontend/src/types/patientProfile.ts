/** Mirrors the backend's `app.schemas.patient_profile` contracts. */

export type Gender = "male" | "female" | "other" | "prefer_not_to_say";
export type BloodGroup = "A+" | "A-" | "B+" | "B-" | "AB+" | "AB-" | "O+" | "O-" | "unknown";
export type SmokingStatus = "never" | "former" | "current";
export type AlcoholConsumption = "never" | "occasional" | "regular" | "frequent";

export interface PatientProfile {
  id: string;
  user_id: string;
  date_of_birth: string | null;
  gender: Gender | null;
  phone_number: string | null;
  blood_group: BloodGroup | null;
  height_cm: number | null;
  weight_kg: number | null;
  address: string | null;
  emergency_contact_name: string | null;
  emergency_contact_phone: string | null;
  emergency_contact_relationship: string | null;
  family_history: string | null;
  allergies: string | null;
  current_medications: string | null;
  smoking_status: SmokingStatus | null;
  alcohol_consumption: AlcoholConsumption | null;
  completion_percentage: number;
  created_at: string;
  updated_at: string;
}

export type PatientProfilePayload = Partial<
  Omit<PatientProfile, "id" | "user_id" | "completion_percentage" | "created_at" | "updated_at">
>;
