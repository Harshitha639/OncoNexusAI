import { apiClient } from "@/services/apiClient";
import type { ApiResponse } from "@/types/api";
import type { DashboardSummary } from "@/types/dashboard";

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  const { data } = await apiClient.get<ApiResponse<DashboardSummary>>("/dashboard");
  if (!data.data) {
    throw new Error("Dashboard response did not include data.");
  }
  return data.data;
}
