import { apiClient } from "@/services/apiClient";
import type { ApiResponse } from "@/types/api";
import type { Appointment, AppointmentPayload } from "@/types/appointment";

export async function bookAppointment(payload: AppointmentPayload): Promise<Appointment> {
  const { data } = await apiClient.post<ApiResponse<Appointment>>("/appointments", payload);
  if (!data.data) {
    throw new Error("Appointment response did not include data.");
  }
  return data.data;
}

export async function listMyAppointments(): Promise<Appointment[]> {
  const { data } = await apiClient.get<ApiResponse<Appointment[]>>("/appointments");
  return data.data ?? [];
}

export async function cancelAppointment(appointmentId: string): Promise<Appointment> {
  const { data } = await apiClient.post<ApiResponse<Appointment>>(
    `/appointments/${appointmentId}/cancel`,
  );
  if (!data.data) {
    throw new Error("Appointment response did not include data.");
  }
  return data.data;
}
