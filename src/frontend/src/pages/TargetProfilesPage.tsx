import { useState } from 'react'
import {
  Badge,
  Button,
  Group,
  LoadingOverlay,
  Select,
  Stack,
  Table,
  Text,
  Title,
} from '@mantine/core'
import { IconPlus } from '@tabler/icons-react'
import { useQuery } from '@tanstack/react-query'
import { targetProfilesApi } from '../api/target_profiles'
import { useAuthStore } from '../stores/authStore'
import type { TargetProfileRead, TargetProfileCompetencyRead } from '../types/target_profile'
import { UserRole } from '../types/enums'

export function TargetProfilesPage() {
  const { user: currentUser } = useAuthStore()
  const [deptFilter, setDeptFilter] = useState<string | null>(null)

  const { data: profiles, isLoading } = useQuery({
    queryKey: ['target-profiles', deptFilter],
    queryFn: () => targetProfilesApi.list(deptFilter || undefined),
  })

  const canManage = [UserRole.ADMIN, UserRole.HEAD, UserRole.DEPARTMENT_HEAD].includes(
    currentUser?.role as UserRole,
  )

  const deptMap = new Map<string, string>(
    (profiles ?? []).map((p): [string, string] => [p.department_id, p.department.name])
  )
  const deptOptions: { value: string; label: string }[] = Array.from(deptMap.entries()).map(
    ([id, name]) => ({ value: id, label: name })
  )

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={2}>Целевые профили</Title>
        {canManage && (
          <Button leftSection={<IconPlus size={16} />} size="sm">
            Создать профиль
          </Button>
        )}
      </Group>

      <Group>
        <Select
          data={[{ value: '', label: 'Все отделы' }, ...deptOptions]}
          value={deptFilter}
          onChange={(v) => setDeptFilter(v || null)}
          placeholder="Отдел"
          clearable
          style={{ width: 240 }}
        />
      </Group>

      <div style={{ position: 'relative' }}>
        <LoadingOverlay visible={isLoading} />
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Название</Table.Th>
              <Table.Th>Отдел</Table.Th>
              <Table.Th>Должность</Table.Th>
              <Table.Th>Компетенций</Table.Th>
              <Table.Th>Обязательных</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {profiles?.map((p: TargetProfileRead) => {
              const mandatory = p.competencies.filter((c: TargetProfileCompetencyRead) => c.is_mandatory).length
              return (
                <Table.Tr key={p.id}>
                  <Table.Td>
                    <Text size="sm" fw={500}>
                      {p.name}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm">{p.department.name}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="sm" c="dimmed">
                      {p.position ?? '—'}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge variant="light" size="sm">
                      {p.competencies.length}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Badge color={mandatory > 0 ? 'red' : 'gray'} variant="light" size="sm">
                      {mandatory}
                    </Badge>
                  </Table.Td>
                </Table.Tr>
              )
            })}
            {!isLoading && !profiles?.length && (
              <Table.Tr>
                <Table.Td colSpan={5}>
                  <Text ta="center" c="dimmed" py="md">
                    Нет целевых профилей
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </div>
    </Stack>
  )
}
