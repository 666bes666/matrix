import { apiClient } from './client'
import type { NotificationRead, UnreadCountRead } from '../types/notification'

export const notificationsApi = {
  list: (limit = 50) =>
    apiClient.get<NotificationRead[]>('/notifications', { params: { limit } }).then((r) => r.data),
  unreadCount: () =>
    apiClient.get<UnreadCountRead>('/notifications/unread-count').then((r) => r.data),
  markRead: (id: string) =>
    apiClient.patch(`/notifications/${id}/read`),
  markAllRead: () =>
    apiClient.post('/notifications/read-all'),
}
