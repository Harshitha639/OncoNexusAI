import { apiClient } from "@/services/apiClient";
import type { ApiResponse, PaginatedResponse } from "@/types/api";
import type {
  MedicalReport,
  MedicalReportDetail,
  OcrStatus,
  ReportAnalysis,
  ReportFileType,
} from "@/types/report";

export interface ReportSearchParams {
  query?: string;
  file_type?: ReportFileType;
  ocr_status?: OcrStatus;
  page?: number;
  page_size?: number;
}

export async function uploadReport(
  title: string,
  description: string | undefined,
  file: File,
): Promise<MedicalReport> {
  const formData = new FormData();
  formData.append("title", title);
  if (description) {
    formData.append("description", description);
  }
  formData.append("file", file);

  const { data } = await apiClient.post<ApiResponse<MedicalReport>>("/reports", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  if (!data.data) {
    throw new Error("Upload response did not include data.");
  }
  return data.data;
}

export async function searchReports(
  params: ReportSearchParams,
): Promise<{ reports: MedicalReport[]; total: number; page: number; pageSize: number }> {
  const { data } = await apiClient.get<PaginatedResponse<MedicalReport[]>>("/reports", {
    params,
  });
  return {
    reports: data.data ?? [],
    total: data.meta.total,
    page: data.meta.page,
    pageSize: data.meta.page_size,
  };
}

export async function fetchReportDetail(reportId: string): Promise<MedicalReportDetail> {
  const { data } = await apiClient.get<ApiResponse<MedicalReportDetail>>(`/reports/${reportId}`);
  if (!data.data) {
    throw new Error("Report response did not include data.");
  }
  return data.data;
}

export async function deleteReport(reportId: string): Promise<void> {
  await apiClient.delete(`/reports/${reportId}`);
}

export async function generateReportSummary(reportId: string): Promise<ReportAnalysis> {
  const { data } = await apiClient.post<ApiResponse<ReportAnalysis>>(
    `/reports/${reportId}/summary`,
  );
  if (!data.data) {
    throw new Error("Summary response did not include data.");
  }
  return data.data;
}

export async function fetchReportSummary(reportId: string): Promise<ReportAnalysis | null> {
  try {
    const { data } = await apiClient.get<ApiResponse<ReportAnalysis>>(
      `/reports/${reportId}/summary`,
    );
    return data.data;
  } catch {
    return null;
  }
}
