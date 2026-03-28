import { apiClient } from './client'

export interface DashboardStats {
  pending_assessments: number
  active_campaigns: number
  open_idp_goals: number
  unread_notifications: number
  user_name: string
  user_role: string
}

export const dashboardApi = {
  getStats: () => apiClient.get<DashboardStats>('/dashboard/stats').then((r) => r.data),
}
