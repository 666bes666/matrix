import { useState, useEffect } from 'react'
import {
  Button,
  Group,
  LoadingOverlay,
  Paper,
  Radio,
  Stack,
  Text,
  Textarea,
  Title,
} from '@mantine/core'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { assessmentsApi } from '../api/assessments'
import type { ScoreInput, AssessmentScoreRead } from '../types/assessment'

const LEVEL_LABELS = ['0 — Нет', '1 — Новичок', '2 — Базовый', '3 — Продвинутый', '4 — Эксперт']

export function AssessmentFormPage() {
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()
  const [scores, setScores] = useState<Record<string, ScoreInput>>({})

  const { data: assessment, isLoading } = useQuery({
    queryKey: ['assessment', id],
    queryFn: () => assessmentsApi.getAssessment(id!),
    enabled: !!id,
  })

  useEffect(() => {
    if (assessment) {
      const initial: Record<string, ScoreInput> = {}
      assessment.scores.forEach((s) => {
        initial[s.competency_id] = {
          competency_id: s.competency_id,
          score: s.score,
          comment: s.comment ?? undefined,
        }
      })
      setScores(initial)
    }
  }, [assessment])

  const submitMutation = useMutation({
    mutationFn: (isDraft: boolean) =>
      assessmentsApi.submitScores(id!, {
        scores: Object.values(scores),
        is_draft: isDraft,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessment', id] })
    },
  })

  const setScore = (competencyId: string, score: number) => {
    setScores((prev) => ({
      ...prev,
      [competencyId]: { ...prev[competencyId], competency_id: competencyId, score },
    }))
  }

  const setComment = (competencyId: string, comment: string) => {
    setScores((prev) => {
      const existing = prev[competencyId]
      if (!existing) return prev
      return { ...prev, [competencyId]: { ...existing, comment } }
    })
  }

  const fullName = (u?: { first_name: string; last_name: string }) =>
    u ? `${u.last_name} ${u.first_name}` : ''

  return (
    <Stack>
      <Title order={2}>Форма оценки</Title>

      <Paper p="lg" withBorder pos="relative">
        <LoadingOverlay visible={isLoading} />

        {assessment && (
          <Stack>
            <Group>
              <Text size="sm">
                <b>Оцениваемый:</b> {fullName(assessment.assessee)}
              </Text>
              <Text size="sm">
                <b>Оценщик:</b> {fullName(assessment.assessor)}
              </Text>
              <Text size="sm">
                <b>Тип:</b> {assessment.assessor_type}
              </Text>
              <Text size="sm" c={assessment.status === 'completed' ? 'green' : 'orange'}>
                <b>Статус:</b> {assessment.status}
              </Text>
            </Group>

            {assessment.scores.length === 0 && (
              <Text c="dimmed" ta="center" py="xl">
                Компетенции для оценки не добавлены
              </Text>
            )}

            {assessment.scores.map((s: AssessmentScoreRead) => (
              <Paper key={s.competency_id} p="md" withBorder>
                <Stack gap="sm">
                  <Text fw={500}>{s.competency_id}</Text>
                  <Radio.Group
                    value={String(scores[s.competency_id]?.score ?? s.score)}
                    onChange={(v) => setScore(s.competency_id, parseInt(v))}
                  >
                    <Group>
                      {LEVEL_LABELS.map((label, i) => (
                        <Radio key={i} value={String(i)} label={label} />
                      ))}
                    </Group>
                  </Radio.Group>
                  <Textarea
                    placeholder="Комментарий (необязательно)"
                    value={scores[s.competency_id]?.comment ?? s.comment ?? ''}
                    onChange={(e) => setComment(s.competency_id, e.currentTarget.value)}
                    autosize
                    minRows={1}
                  />
                </Stack>
              </Paper>
            ))}

            {assessment.status !== 'completed' && (
              <Group justify="flex-end">
                <Button
                  variant="outline"
                  loading={submitMutation.isPending}
                  onClick={() => submitMutation.mutate(true)}
                >
                  Сохранить черновик
                </Button>
                <Button
                  color="green"
                  loading={submitMutation.isPending}
                  onClick={() => submitMutation.mutate(false)}
                >
                  Отправить оценку
                </Button>
              </Group>
            )}
          </Stack>
        )}
      </Paper>
    </Stack>
  )
}
