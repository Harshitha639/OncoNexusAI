import { apiClient } from "@/services/apiClient";
import type { ApiResponse } from "@/types/api";
import type { CaregiverGuidance, PersonalizedGuidance } from "@/types/guidance";

export async function generatePatientGuidance(reportId: string): Promise<PersonalizedGuidance> {
  const { data } = await apiClient.post<ApiResponse<PersonalizedGuidance>>(
    `/reports/${reportId}/guidance/patient`,
  );
  if (!data.data) {
    throw new Error("Guidance response did not include data.");
  }
  return data.data;
}

export async function fetchPatientGuidance(reportId: string): Promise<PersonalizedGuidance | null> {
  try {
    const { data } = await apiClient.get<ApiResponse<PersonalizedGuidance>>(
      `/reports/${reportId}/guidance/patient`,
    );
    return data.data;
  } catch {
    return null;
  }
}

export async function generateCaregiverGuidance(reportId: string): Promise<CaregiverGuidance> {
  const { data } = await apiClient.post<ApiResponse<CaregiverGuidance>>(
    `/reports/${reportId}/guidance/caregiver`,
  );
  if (!data.data) {
    throw new Error("Guidance response did not include data.");
  }
  return data.data;
}

export async function fetchCaregiverGuidance(reportId: string): Promise<CaregiverGuidance | null> {
  try {
    const { data } = await apiClient.get<ApiResponse<CaregiverGuidance>>(
      `/reports/${reportId}/guidance/caregiver`,
    );
    return data.data;
  } catch {
    return null;
  }
}
