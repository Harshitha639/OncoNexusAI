/** Mirrors the backend's `app.schemas.appointment` contracts. */

export type AppointmentStatus = "scheduled" | "cancelled" | "completed";

export interface Appointment {
  id: string;
  patient_id: string;
  doctor_name: string;
  department: string | null;
  scheduled_at: string;
  reason: string | null;
  notes: string | null;
  status: AppointmentStatus;
  created_at: string;
  updated_at: string;
}

export interface AppointmentPayload {
  doctor_name: string;
  department?: string | null;
  scheduled_at: string;
  reason?: string | null;
}
