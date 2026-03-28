export type NotificationCategory = 'assessment' | 'idp' | 'career' | 'system'

export interface NotificationRead {
  id: string
  user_id: string
  category: NotificationCategory
  title: string
  message: string
  is_read: boolean
  telegram_sent: boolean
  created_at: string
}

export interface UnreadCountRead {
  count: number
}
