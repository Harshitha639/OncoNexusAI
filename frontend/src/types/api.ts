/**
 * Shared API response contracts, mirroring the backend's
 * `app.common.responses` envelopes so the frontend and backend stay in sync.
 */

export type ResponseStatus = "success" | "error" | "fail";

export interface ApiResponse<T> {
  status: ResponseStatus;
  message: string;
  data: T | null;
}

export interface PaginationMeta {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginatedResponse<T> extends ApiResponse<T> {
  meta: PaginationMeta;
}

export interface ApiErrorDetail {
  code: string;
  message: string;
  field?: string;
}

export interface ApiErrorResponse {
  status: "error";
  message: string;
  errors: ApiErrorDetail[];
}
