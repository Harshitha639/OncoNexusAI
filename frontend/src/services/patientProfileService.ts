import { apiClient } from "@/services/apiClient";
import type { ApiResponse } from "@/types/api";
import type { PatientProfile, PatientProfilePayload } from "@/types/patientProfile";

const BASE_PATH = "/patients/me/profile";

export async function fetchMyProfile(): Promise<PatientProfile> {
  const { data } = await apiClient.get<ApiResponse<PatientProfile>>(BASE_PATH);
  if (!data.data) {
    throw new Error("Profile response did not include data.");
  }
  return data.data;
}

export async function createMyProfile(payload: PatientProfilePayload): Promise<PatientProfile> {
  const { data } = await apiClient.post<ApiResponse<PatientProfile>>(BASE_PATH, payload);
  if (!data.data) {
    throw new Error("Profile response did not include data.");
  }
  return data.data;
}

export async function updateMyProfile(payload: PatientProfilePayload): Promise<PatientProfile> {
  const { data } = await apiClient.put<ApiResponse<PatientProfile>>(BASE_PATH, payload);
  if (!data.data) {
    throw new Error("Profile response did not include data.");
  }
  return data.data;
}
