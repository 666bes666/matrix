import { Badge, Group, LoadingOverlay, Paper, SimpleGrid, Stack, Text, Title } from '@mantine/core'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { dashboardApi } from '../api/dashboard'
import { useAuthStore } from '../stores/authStore'

export function DashboardPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()

  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardApi.getStats,
  })

  const cards = stats
    ? [
        {
          label: 'Ожидают оценки',
          value: stats.pending_assessments,
          color: stats.pending_assessments > 0 ? 'orange' : 'gray',
          onClick: () => navigate('/my-tasks'),
        },
        {
          label: 'Активные кампании',
          value: stats.active_campaigns,
          color: 'blue',
          onClick: () => navigate('/campaigns'),
        },
        {
          label: 'Открытых целей ИПР',
          value: stats.open_idp_goals,
          color: stats.open_idp_goals > 0 ? 'teal' : 'gray',
          onClick: () => navigate('/idp'),
        },
        {
          label: 'Непрочитанных уведомлений',
          value: stats.unread_notifications,
          color: stats.unread_notifications > 0 ? 'red' : 'gray',
          onClick: () => navigate('/notifications'),
        },
      ]
    : []

  return (
    <Stack>
      <Group>
        <Title order={2}>Добро пожаловать{user ? `, ${user.last_name} ${user.first_name}` : ''}</Title>
        {user && <Badge size="lg" color="blue">{user.role}</Badge>}
      </Group>

      <Paper p="lg" withBorder pos="relative">
        <LoadingOverlay visible={isLoading} />
        <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
          {cards.map((card) => (
            <Paper
              key={card.label}
              p="lg"
              withBorder
              style={{ cursor: 'pointer' }}
              onClick={card.onClick}
            >
              <Stack gap="xs" align="center">
                <Text size="xl" fw={700} c={card.color}>
                  {card.value}
                </Text>
                <Text size="sm" c="dimmed" ta="center">
                  {card.label}
                </Text>
              </Stack>
            </Paper>
          ))}
        </SimpleGrid>
      </Paper>
    </Stack>
  )
}
