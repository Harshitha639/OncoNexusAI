/** Mirrors the backend's `app.schemas.notification` contracts. */

export type NotificationType =
  | "appointment_reminder"
  | "medication_reminder"
  | "report_upload_success"
  | "general";

export interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  message: string;
  is_read: boolean;
  related_entity_type: string | null;
  related_entity_id: string | null;
  created_at: string;
}
