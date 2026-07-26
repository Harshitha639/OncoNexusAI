import { apiClient } from "@/services/apiClient";
import type { ApiResponse } from "@/types/api";
import type { Notification } from "@/types/notification";

export async function listMyNotifications(unreadOnly = false): Promise<Notification[]> {
  const { data } = await apiClient.get<ApiResponse<Notification[]>>("/notifications", {
    params: { unread_only: unreadOnly },
  });
  return data.data ?? [];
}

export async function fetchUnreadCount(): Promise<number> {
  const { data } = await apiClient.get<ApiResponse<{ unread_count: number }>>(
    "/notifications/unread-count",
  );
  return data.data?.unread_count ?? 0;
}

export async function markNotificationRead(notificationId: string): Promise<Notification> {
  const { data } = await apiClient.post<ApiResponse<Notification>>(
    `/notifications/${notificationId}/read`,
  );
  if (!data.data) {
    throw new Error("Notification response did not include data.");
  }
  return data.data;
}
