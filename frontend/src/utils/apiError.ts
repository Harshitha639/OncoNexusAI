import { AxiosError } from "axios";

import type { ApiErrorResponse } from "@/types/api";

/**
 * Extract a human-readable message from a failed API call, falling back
 * gracefully when the backend didn't return the expected error envelope.
 */
export function getApiErrorMessage(error: unknown, fallback = "Something went wrong. Please try again."): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as ApiErrorResponse | undefined;
    if (data?.message) {
      return data.message;
    }
    if (data?.errors?.length) {
      return data.errors.map((e) => e.message).join(" ");
    }
  }
  return fallback;
}
