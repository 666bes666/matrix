import {
  Badge,
  Button,
  Group,
  LoadingOverlay,
  Paper,
  Stack,
  Text,
  Title,
} from '@mantine/core'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { notificationsApi } from '../api/notifications'

const CATEGORY_COLORS: Record<string, string> = {
  assessment: 'blue',
  idp: 'teal',
  career: 'violet',
  system: 'gray',
}

const CATEGORY_LABELS: Record<string, string> = {
  assessment: 'Оценка',
  idp: 'ИПР',
  career: 'Карьера',
  system: 'Система',
}

export function NotificationsPage() {
  const queryClient = useQueryClient()

  const { data: notifications, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.list(100),
  })

  const markReadMutation = useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  })

  const markAllMutation = useMutation({
    mutationFn: notificationsApi.markAllRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  })

  const unreadCount = notifications?.filter((n) => !n.is_read).length ?? 0

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={2}>Уведомления</Title>
        {unreadCount > 0 && (
          <Button
            variant="outline"
            size="sm"
            loading={markAllMutation.isPending}
            onClick={() => markAllMutation.mutate()}
          >
            Прочитать все ({unreadCount})
          </Button>
        )}
      </Group>

      <Paper withBorder pos="relative">
        <LoadingOverlay visible={isLoading} />
        <Stack gap={0}>
          {notifications?.map((n) => (
            <Paper
              key={n.id}
              p="md"
              style={{
                backgroundColor: n.is_read ? undefined : 'var(--mantine-color-blue-0)',
                borderBottom: '1px solid var(--mantine-color-gray-2)',
                cursor: n.is_read ? 'default' : 'pointer',
              }}
              onClick={() => !n.is_read && markReadMutation.mutate(n.id)}
            >
              <Group justify="space-between" wrap="nowrap">
                <Stack gap={2}>
                  <Group gap="xs">
                    <Badge color={CATEGORY_COLORS[n.category] ?? 'gray'} size="xs">
                      {CATEGORY_LABELS[n.category] ?? n.category}
                    </Badge>
                    <Text size="sm" fw={n.is_read ? 400 : 600}>
                      {n.title}
                    </Text>
                  </Group>
                  <Text size="sm" c="dimmed">{n.message}</Text>
                </Stack>
                <Text size="xs" c="dimmed" style={{ whiteSpace: 'nowrap' }}>
                  {new Date(n.created_at).toLocaleDateString('ru-RU')}
                </Text>
              </Group>
            </Paper>
          ))}
          {notifications?.length === 0 && (
            <Text c="dimmed" ta="center" py="xl">Нет уведомлений</Text>
          )}
        </Stack>
      </Paper>
    </Stack>
  )
}
