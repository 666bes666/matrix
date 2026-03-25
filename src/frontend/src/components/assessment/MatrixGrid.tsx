import { Box, Text, Tooltip } from '@mantine/core'
import type { MatrixData } from '../../types/analytics'

const LEVEL_COLORS = ['#c92a2a', '#e67700', '#fab005', '#2f9e44', '#1971c2']
const LEVEL_LABELS = ['Нет', 'Новичок', 'Базовый', 'Продвинутый', 'Эксперт']

interface MatrixGridProps {
  data: MatrixData
  onCellClick?: (userId: string, competencyId: string) => void
}

function ScoreCell({
  score,
  userId,
  competencyId,
  userName,
  competencyName,
  onCellClick,
}: {
  score: number | undefined
  userId: string
  competencyId: string
  userName: string
  competencyName: string
  onCellClick?: (userId: string, competencyId: string) => void
}) {
  const level = score !== undefined ? Math.round(score) : -1
  const color = level >= 0 ? LEVEL_COLORS[level] : '#dee2e6'
  const label = level >= 0 ? `${LEVEL_LABELS[level]} (${score?.toFixed(1)})` : 'Нет оценки'

  return (
    <Tooltip label={`${userName} — ${competencyName}: ${label}`} withArrow>
      <Box
        style={{
          width: 32,
          height: 32,
          backgroundColor: color,
          cursor: onCellClick ? 'pointer' : 'default',
          borderRadius: 4,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
        onClick={() => onCellClick?.(userId, competencyId)}
      >
        {level >= 0 && (
          <Text size="xs" c="white" fw={700}>
            {level}
          </Text>
        )}
      </Box>
    </Tooltip>
  )
}

export function MatrixGrid({ data, onCellClick }: MatrixGridProps) {
  if (data.users.length === 0 || data.competencies.length === 0) {
    return (
      <Text c="dimmed" ta="center" py="xl">
        Нет данных для отображения
      </Text>
    )
  }

  return (
    <Box style={{ overflowX: 'auto', overflowY: 'auto', maxHeight: 'calc(100vh - 220px)' }}>
      <table style={{ borderCollapse: 'collapse', tableLayout: 'fixed' }}>
        <thead>
          <tr>
            <th
              style={{
                position: 'sticky',
                left: 0,
                top: 0,
                zIndex: 3,
                backgroundColor: 'var(--mantine-color-body)',
                minWidth: 180,
                maxWidth: 180,
                padding: '8px',
                borderBottom: '1px solid var(--mantine-color-gray-3)',
                textAlign: 'left',
              }}
            >
              <Text size="sm" fw={600}>
                Сотрудник
              </Text>
            </th>
            {data.competencies.map((comp) => (
              <th
                key={comp.id}
                style={{
                  position: 'sticky',
                  top: 0,
                  zIndex: 2,
                  backgroundColor: 'var(--mantine-color-body)',
                  width: 40,
                  minWidth: 40,
                  padding: '8px 4px',
                  borderBottom: '1px solid var(--mantine-color-gray-3)',
                  textAlign: 'center',
                }}
              >
                <Tooltip label={comp.name} withArrow position="top">
                  <Text
                    size="xs"
                    style={{
                      writingMode: 'vertical-rl',
                      transform: 'rotate(180deg)',
                      whiteSpace: 'nowrap',
                      maxHeight: 120,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      cursor: 'default',
                    }}
                  >
                    {comp.name}
                  </Text>
                </Tooltip>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.users.map((user) => (
            <tr key={user.id}>
              <td
                style={{
                  position: 'sticky',
                  left: 0,
                  zIndex: 1,
                  backgroundColor: 'var(--mantine-color-body)',
                  padding: '8px',
                  borderBottom: '1px solid var(--mantine-color-gray-2)',
                  minWidth: 180,
                  maxWidth: 180,
                }}
              >
                <Text size="sm" fw={500} truncate>
                  {user.full_name}
                </Text>
                {user.team && (
                  <Text size="xs" c="dimmed" truncate>
                    {user.team}
                  </Text>
                )}
              </td>
              {data.competencies.map((comp) => (
                <td
                  key={comp.id}
                  style={{
                    padding: '4px',
                    borderBottom: '1px solid var(--mantine-color-gray-2)',
                    textAlign: 'center',
                  }}
                >
                  <ScoreCell
                    score={data.scores[user.id]?.[comp.id]}
                    userId={user.id}
                    competencyId={comp.id}
                    userName={user.full_name}
                    competencyName={comp.name}
                    onCellClick={onCellClick}
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </Box>
  )
}
