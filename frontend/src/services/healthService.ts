import { apiClient } from "@/services/apiClient";
import type { ApiResponse } from "@/types/api";

export interface HealthStatus {
  service: string;
  version: string;
  environment: string;
}

export async function fetchHealthStatus(): Promise<ApiResponse<HealthStatus>> {
  const { data } = await apiClient.get<ApiResponse<HealthStatus>>("/health");
  return data;
}
